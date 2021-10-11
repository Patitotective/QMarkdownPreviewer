import sys
import commonmark

from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QTextBrowser
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView

from github_markdown_style import GITHUB_MARKDOWN_STYLE

class CheckFileWorker(QObject):
    update = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()

        self.path = path
        self.stop_checking = False

    def run(self):
        old_text = self.read_markdown_file()

        while not self.stop_checking:
            new_text = self.read_markdown_file()
            if not old_text == new_text:
                self.update.emit(new_text)
                old_text = new_text
    
    def read_markdown_file(self):
        with open(self.path, "r") as file:
            return file.read()

    def stop(self):
        self.stop_checking = True

class MarkdownPreviewer(QWidget):
    def __init__(self, path, title="Markdown preview", current_theme="dark", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path = path

        self.setLayout(QVBoxLayout())
        self.setWindowTitle(title)
        self.web_view = QWebEngineView()
        self.web_view.setHtml(self.read_markdown_file())

        self.layout().addWidget(self.web_view)

        self.init_thread()

    def init_thread(self):
        self.thread = QThread()
        self.worker = CheckFileWorker(self.path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)    

        self.worker.update.connect(self.update_markdown)

        self.thread.start()

    def closeEvent(self, event):
        self.worker.stop()
        self.worker.deleteLater()
        
        self.thread.quit()
        self.thread.deleteLater()

        event.accept()

    def read_markdown_file(self):
        with open(self.path, "r") as file:
            return self.markdown_to_html(file.read())

    def update_markdown(self, md_text):
        self.web_view.setHtml(self.markdown_to_html(md_text))

    def markdown_to_html(self, text: str) -> str:
        text = f"<head><style>{GITHUB_MARKDOWN_STYLE}</style></head><body>{commonmark.commonmark(text)}</body>"

        return text


if __name__ == '__main__':
    PATH = "README.md"
    
    app = QApplication(sys.argv)

    markdown_previewer_dialog = MarkdownPreviewer(PATH)
    markdown_previewer_dialog.show()

    sys.exit(app.exec_())
