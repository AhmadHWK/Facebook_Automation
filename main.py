import sys
from PyQt5.QtWidgets import QApplication
from interface import BotControlPanel

if __name__ == '__main__':
    app = QApplication(sys.argv)
    panel = BotControlPanel()
    panel.show()
    sys.exit(app.exec_())