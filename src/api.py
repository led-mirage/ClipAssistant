import pyperclip


class ClipAssistantApi:
    def __init__(self, main_app):
        from main import ClipAssistantApp
        self._main_app: ClipAssistantApp = main_app

    def get_font_size(self) -> int:
        """Get the configured font size."""
        return self._main_app.config.window.font_size

    def set_mode(self, label: str):
        """Set the current processing mode."""
        self._main_app.set_mode(label)
        return True

    def load_history_item(self, index: int):
        """Load a specific history item by index."""
        self._main_app.load_history_item(index)

    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        pyperclip.copy(text)
