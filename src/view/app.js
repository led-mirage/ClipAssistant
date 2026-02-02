document.addEventListener('DOMContentLoaded', () => {
    try {
        if (typeof marked === 'undefined') throw new Error('marked is not defined');
        if (typeof hljs === 'undefined') throw new Error('hljs is not defined');

        const modeSelect = document.getElementById('modeSelect');
        const historySelect = document.getElementById('historySelect');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const copyBtn = document.getElementById('copyBtn');
        const contentArea = document.getElementById('contentArea');
        const loadingOverlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');

        // Configure marked with highlight.js
        marked.use({
            renderer: {
                code({ text, lang }) {
                    // Marked v15 passes an object {text, lang, ...} to renderer.code if using use() ?
                    // Actually, let's handle signature variation or object.
                    // Check if first arg is object (Token)
                    let codeContent = text;
                    let language = lang;

                    if (typeof arguments[0] === 'object') {
                        const token = arguments[0];
                        codeContent = token.text || "";
                        language = token.lang || "";
                    } else {
                        // Fallback for older signatures or string args
                        codeContent = typeof arguments[0] === 'string' ? arguments[0] : String(arguments[0] || "");
                        language = arguments[1] || "";
                    }

                    const validLanguage = hljs.getLanguage(language) ? language : 'plaintext';
                    return '<pre><code class="hljs language-' + validLanguage + '">' +
                        hljs.highlight(codeContent, { language: validLanguage }).value +
                        '</code></pre>';
                }
            }
        });

        // UI Interaction Listeners
        modeSelect.addEventListener('change', (e) => {
            pywebview.api.set_mode(e.target.value).then(() => {
                // Mode changed
            });
        });

        historySelect.addEventListener('change', (e) => {
            const index = parseInt(e.target.value);
            if (!isNaN(index)) {
                pywebview.api.load_history_item(index);
            }
        });

        prevBtn.addEventListener('click', () => {
            // Prev = 過去の履歴 = リストの下の方 = indexが増える
            // optionsの0番目はプレースホルダなので、実質1番目からが履歴。
            const maxIndex = historySelect.options.length - 1;

            // 何も選ばれていない(0) or 履歴が空の場合は何もしない
            if (historySelect.options.length <= 1) return;

            if (historySelect.selectedIndex === 0) {
                // 最初は最新(1)を選択
                historySelect.selectedIndex = 1;
            } else if (historySelect.selectedIndex < maxIndex) {
                historySelect.selectedIndex++;
            }
            triggerHistoryChange();
        });

        nextBtn.addEventListener('click', () => {
            // Next = 新しい履歴 = リストの上の方 = indexが減る
            // index 1 が最新。0はプレースホルダ。
            if (historySelect.selectedIndex > 1) {
                historySelect.selectedIndex--;
                triggerHistoryChange();
            }
        });

        copyBtn.addEventListener('click', () => {
            const generatedDiv = contentArea.querySelector('.generated-text');
            if (generatedDiv) {
                pywebview.api.copy_to_clipboard(generatedDiv.innerText);

                // Visual feedback
                const icon = copyBtn.querySelector('i');
                // Switch from Regular Clipboard to Solid Check
                icon.classList.remove('fa-regular', 'fa-clipboard');
                icon.classList.add('fa-solid', 'fa-check');

                setTimeout(() => {
                    // Switch back
                    icon.classList.remove('fa-solid', 'fa-check');
                    icon.classList.add('fa-regular', 'fa-clipboard');
                }, 1000);
            }
        });

        function triggerHistoryChange() {
            const event = new Event('change');
            historySelect.dispatchEvent(event);
        }

        // Exposed functions to be called from Python
        window.app = {
            init: (modes, currentModeLabel, currentUsageMessage) => {
                // Populate modes
                modeSelect.innerHTML = '';
                modes.forEach(mode => {
                    const option = document.createElement('option');
                    option.value = mode.label;
                    option.textContent = mode.label;
                    if (mode.label === currentModeLabel) {
                        option.selected = true;
                    }
                    modeSelect.appendChild(option);
                });

                // Set initial content
                window.app.setContent(currentUsageMessage);
            },

            updateHistory: (historyItems) => {
                historySelect.innerHTML = '<option value="">--- 履歴 ---</option>';
                historyItems.forEach((item, index) => {
                    const option = document.createElement('option');
                    option.value = index;
                    option.textContent = `【${item.mode}】${item.title}`;
                    historySelect.appendChild(option);
                });
                // Select the most recent one (index 0 which corresponds to option 1)
                if (historyItems.length > 0) {
                    historySelect.value = "0";
                }
            },

            selectHistoryItem: (index) => {
                historySelect.value = index.toString();
            },

            setContent: (generated, original = null) => {
                let html = `<div class="generated-text markdown-body">${marked.parse(generated || "")}</div>`;
                if (original) {
                    html += `<div class="original-text">${formatText(original)}</div>`;
                }
                contentArea.innerHTML = html;
                // Scroll matching container to top
                if (contentArea.parentElement) {
                    contentArea.parentElement.scrollTop = 0;
                }
            },

            showLoading: (text) => {
                loadingText.textContent = text || "";
                loadingOverlay.classList.add('active');
            },

            hideLoading: () => {
                loadingOverlay.classList.remove('active');
            },

            setFontSize: (size) => {
                document.documentElement.style.setProperty('--font-size-base', size + 'px');
            },

            showToast: (message, type = 'info') => {
                const container = document.getElementById('toastContainer');
                const toast = document.createElement('div');
                toast.className = `toast ${type}`;
                toast.textContent = message;

                container.appendChild(toast);

                // Trigger reflow to enable transition
                requestAnimationFrame(() => {
                    toast.classList.add('visible');
                });

                // Remove after 3 seconds
                setTimeout(() => {
                    toast.classList.remove('visible');
                    toast.addEventListener('transitionend', () => {
                        if (toast.parentElement) {
                            toast.parentElement.removeChild(toast);
                        }
                    });
                }, 3000);
            }
        };

        function formatText(text) {
            if (!text) return "";
            return text
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");
        }
    } catch (e) {
        alert("App Error: " + e.message);
        document.body.innerHTML = `<div style="color:red; padding:20px;">App Error: ${e.message}</div>`;
    }
});

window.addEventListener("pywebviewready", async function () {
    const fontSize = await pywebview.api.get_font_size();
    document.documentElement.style.setProperty('--font-size-base', fontSize + 'px');
});
