import time
import threading
import os
import sys
import json
import ctypes
from ctypes import wintypes
import webview
from PIL import Image

import pyperclip
import pystray
from pynput import keyboard as pynput_keyboard

from app_const import APP_NAME, APP_VERSION, COPYRIGHT
from config import Config
from state import State
from agent import Agent
from api import ClipAssistantApi

MAX_HISTORY = 100

# ----- Resource helpers -----
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # main.py is in src/, so we need to go up one level to get to project root
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)

class ClipAssistantApp:
    def __init__(self, agent: Agent, config: Config):
        self.config = config
        self.agent = agent
        self.last_ctrl_c_time = 0.0
        self.ctrl_pressed = False
        self.is_generating = False
        self.keyevent_listener = None
        self.history = []
        self.state = State.load()
        self.current_mode = config.find_mode(self.state.current_mode_label)
        self.window = None
        self.is_quitting = False

    def start(self):
        # API instance for JS communication
        self.api = ClipAssistantApi(self)

        # Create window
        self.window = webview.create_window(
            f"{APP_NAME} {APP_VERSION}",
            url=resource_path("src/view/index.html"),
            width=self.config.window.width,
            height=self.config.window.height,
            js_api=self.api,
            resizable=True,
            text_select=True,
            hidden=self.config.window.start_hidden
        )

        # Start background threads
        self.start_hotkeys()
        self.start_tray_icon()
        
        # Bind events
        self.window.events.loaded += self.on_loaded
        self.window.events.closing += self.on_closing

        # Start WebView
        webview.start(debug=False)

    def on_loaded(self):
        # Initialize UI with modes and current state
        modes_data = [{"label": m.label} for m in self.config.modes]
        usage_msg = self.current_mode.usage_message
        
        # Call JS init function
        js = f"window.app.init({json.dumps(modes_data)}, {json.dumps(self.current_mode.label)}, {json.dumps(usage_msg)})"
        self.window.evaluate_js(js)

        if not self.config.window.start_hidden:
            self.restore_window()
            
        # Close PyInstaller splash screen if it exists
        if getattr(sys, 'frozen', False):
            try:
                import pyi_splash # type: ignore
                if pyi_splash.is_alive():
                    pyi_splash.close()
            except ImportError:
                pass

    def on_closing(self):
        if self.is_quitting:
            return True

        # Hide window instead of closing
        # Use a timer to avoid blocking the event loop or causing deadlocks
        threading.Timer(0.1, self.window.hide).start()
        return False

    def quit(self):
        self.is_quitting = True
        # Clean up resources
        if self.keyevent_listener:
            self.keyevent_listener.stop()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.window.destroy()
        os._exit(0)

    def reload_config(self):
        try:
            # Re-load config without exiting on error
            new_config = Config.load(exit_on_error=False)
            self.config = new_config
            
            # Re-initialize agent
            self.agent = Agent(self.config)
            
            # Update mode
            # Try to persist keeping current mode label if it exists in new config
            current_label = self.state.current_mode_label
            new_mode = self.config.find_mode(current_label)
            
            if new_mode:
                self.current_mode = new_mode
            else:
                # Fallback to first mode available
                if self.config.modes:
                    self.current_mode = self.config.modes[0]
                    self.state.current_mode_label = self.current_mode.label
                    self.state.save()
            
            # Update UI
            # 1. Update modes list and usage message in JS
            modes_data = [{"label": m.label} for m in self.config.modes]
            # We can re-use the init logic or just set content. 
            # Ideally we have a JS function to update just the config, but init works if we don't mind resetting partial state.
            
            js = f"window.app.init({json.dumps(modes_data)}, {json.dumps(self.current_mode.label)}, {json.dumps(self.current_mode.usage_message)})"
            self.window.evaluate_js(js)
            
            # Update font size
            self.window.evaluate_js(f"window.app.setFontSize({self.config.window.font_size})")

            # Show success toast
            self.window.evaluate_js("window.app.showToast('設定を再読み込みしました。', 'success')")

        except Exception as e:
            # Show error toast (escape quotes in error message if needed, simplified here)
            error_msg = str(e).replace("'", "\\'").replace("\n", " ")
            self.window.evaluate_js(f"window.app.showToast('設定の再読み込みに失敗しました: {error_msg}', 'error')")

    # ----- UI interactions -----
    def set_mode(self, label: str):
        new_mode = self.config.find_mode(label)
        if new_mode:
            self.current_mode = new_mode
            self.state.current_mode_label = label
            self.state.save()
            # Update UI instruction text if no history is showing
            self.window.evaluate_js(f"window.app.setContent({json.dumps(new_mode.usage_message)})")

    def add_to_history(self, original: str, generated: str):
        title = original.replace("\n", " ")[:50] + "..."
        self.history.insert(0, {
            "mode": self.current_mode.label, 
            "title": title, 
            "original": original, 
            "generated": generated
        })
        if len(self.history) > MAX_HISTORY:
            self.history.pop()

        # Update JS history list
        self.window.evaluate_js(f"window.app.updateHistory({json.dumps(self.history)})")
        # Select the new item
        self.window.evaluate_js("window.app.selectHistoryItem(0)")

    def restore_window(self):
        if self.window:
            self.window.restore()
            self.window.show()
            self.window.on_top = True
            # Reset on_top after a short delay to allow focusing but not stuck on top
            threading.Timer(0.5, lambda: setattr(self.window, 'on_top', False)).start()

    def load_history_item(self, index: int):
        if 0 <= index < len(self.history):
            item = self.history[index]
            self._display_result(item["generated"], item["original"])

    def _display_result(self, generated: str, original: str = None):
        # Use json.dumps to safely serialize strings for JS
        js = f"window.app.setContent({json.dumps(generated)}, {json.dumps(original) if original else 'null'})"
        self.window.evaluate_js(js)

    # ----- Hotkey handling -----
    def on_ctrl_c(self):
        now = time.time()
        if now - self.last_ctrl_c_time < 0.5:
            self.handle_double_ctrl_c()
        self.last_ctrl_c_time = now

    def handle_double_ctrl_c(self):
        if self.is_generating:
            return
        
        text = pyperclip.paste()
        if not text:
            return

        self.is_generating = True
        
        # Show window and loading overlay
        self.restore_window()
        # Show window and loading overlay
        self.restore_window()
        self.window.evaluate_js(f"window.app.showLoading({json.dumps(text[:50] + '...')})")

        def worker():
            try:
                generated = self.agent.generate_text(text, self.current_mode)
                # Success
                self.add_to_history(text, generated)
                self._display_result(generated, text if self.current_mode.display_original_text else None)
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self._display_result(error_msg, text)
            finally:
                self.is_generating = False
                self.window.evaluate_js("window.app.hideLoading()")

        threading.Thread(target=worker, daemon=True).start()

    def on_press(self, key):
        try:
            if key == pynput_keyboard.Key.ctrl_l or key == pynput_keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if key == pynput_keyboard.Key.ctrl_l or key == pynput_keyboard.Key.ctrl_r:
                self.ctrl_pressed = False
            else:
                if self.ctrl_pressed and hasattr(key, 'char') and key.char == '\x03':
                    self.on_ctrl_c()
        except AttributeError:
            pass

    def start_hotkeys(self):
        self.keyevent_listener = pynput_keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.keyevent_listener.start()

    # ----- System tray handling -----
    def start_tray_icon(self):
        if os.name != "nt":
            return  

        icon_path = resource_path("src/view/app.ico")
        
        try:
            image = Image.open(icon_path)
            menu = pystray.Menu(
                pystray.MenuItem("表示", self.tray_show, default=True),
                pystray.MenuItem("設定の再読み込み", self.tray_reload_config),
                pystray.MenuItem("終了", self.tray_quit),
            )
            self.tray_icon = pystray.Icon(APP_NAME, image, f"{APP_NAME}", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Failed to start tray icon: {e}")

    def tray_show(self, icon=None, item=None):
        self.restore_window()

    def tray_reload_config(self, icon=None, item=None):
        self.reload_config()

    def tray_quit(self, icon=None, item=None):
        self.quit()

# ----- Entry point -----

def ensure_single_instance(mutex_name: str) -> bool:
    if os.name != "nt": return True
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.GetLastError.argtypes = []
    kernel32.GetLastError.restype = wintypes.DWORD
    ERROR_ALREADY_EXISTS = 183
    
    h = kernel32.CreateMutexW(None, False, mutex_name)
    if not h: return True
    
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        # すでに存在する場合は、今取得したハンドルを閉じる（そうしないと、このプロセスがMutexを保持し続けてしまう）
        kernel32.CloseHandle(h)
        return False
    
    # 新しく作成できた場合は、ハンドルを保持し続ける（アプリケーション終了時にOSが解放）
    # グローバル変数等に保持しておかないとGCされる？ -> ctypesの戻り値は単なるintなのでGCされないはずだが、
    # 関数スコープを抜けてもハンドルはオープンなまま。OSがクリーンアップするのはプロセス終了時。
    # 明示的に閉じない限り有効。
    return True

def main():
    # 最近の高DPIディスプレイ（文字がぼやけないようにする）
    if os.name == "nt":
        try:
            from ctypes import windll
            # Windows 8.1以降のDPI意識設定
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            # 古いOSや環境で失敗してもアプリ自体は起動するように
            pass

    mutex_name = "ClipAssistantApp_Mutex_v1"
    
    if not ensure_single_instance(mutex_name):
        # 既に起動している場合、スプラッシュを閉じてからダイアログを出す
        if getattr(sys, 'frozen', False):
            try:
                import pyi_splash # type: ignore
                if pyi_splash.is_alive():
                    pyi_splash.close()
            except ImportError:
                pass

        ctypes.windll.user32.MessageBoxW(0, "すでに起動しています。タスクトレイをご確認ください。", APP_NAME, 0x40)
        return

    config = Config.load()
    
    agent = Agent(config)
    app = ClipAssistantApp(agent, config)
    app.start()

if __name__ == "__main__":
    main()
