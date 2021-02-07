from datetime import datetime
import requests
from PyQt6 import QtWidgets, QtCore
import clientui


class Messenger(QtWidgets.QMainWindow, clientui.UiMainWindow):
    def __init__(self, server_host):
        super().__init__()
        self.setup_ui(self)

        self.server_host = server_host

        self.pushButton.pressed.connect(self.send_message)

        self.after = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.get_messages)
        self.timer.start(1000)

    def get_messages(self):
        try:
            response = requests.get(
                f'{self.server_host}/messages',
                params={'after': self.after}
            )
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        messages = response.json()['messages']

        for message in messages:
            self.print_message(message)
            self.after = message['time']

    def print_message(self, message):
        message_time = datetime.fromtimestamp(message['time'])
        message_time = message_time.strftime('%Y/%m/%d %H:%M:%S')
        self.textBrowser.append(message_time + ' ' + message['name'])
        self.textBrowser.append(message['text'])
        self.textBrowser.append('')

    def send_message(self):
        name = self.lineEdit.text()
        text = self.textEdit.toPlainText()

        try:
            response = requests.post(
                f'{self.server_host}/send',
                json={'name': name, 'text': text}
            )
        except requests.exceptions.HTTPError as err:
            self.textBrowser.append("Server unreachable. Try again later")
            self.textBrowser.append(SystemExit(err))
            return

        if response.status_code != 200:
            self.textBrowser.append("There was an error while sending your message")
            self.textBrowser.append("Check the name and the text if not empty")
            self.textBrowser.append('')
            return

        self.textEdit.setText('')


app = QtWidgets.QApplication([])
window = Messenger(server_host='http://127.0.0.1:5000/')
window.show()
app.exec()
