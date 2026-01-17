# file: com_selector_widget.py
from PyQt5 import QtWidgets, QtCore
import serial.tools.list_ports


class ComSelectorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, default_baud=9600):
        super().__init__(parent)

        # Layout
        layout = QtWidgets.QHBoxLayout(self)

        # COM Port drop-down
        self.com_box = QtWidgets.QComboBox()
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        layout.addWidget(QtWidgets.QLabel("COM Port:"))
        layout.addWidget(self.com_box)
        layout.addWidget(self.refresh_button)

        # Baud rate drop-down
        self.baud_box = QtWidgets.QComboBox()
        self.baud_box.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_box.setCurrentText(str(default_baud))
        layout.addWidget(QtWidgets.QLabel("Baud Rate:"))
        layout.addWidget(self.baud_box)

        # Refresh COM ports on button click
        self.refresh_button.clicked.connect(self.refresh_ports)

        # Initial port scan
        self.refresh_ports()

    def refresh_ports(self):
        """Scan and populate available COM ports."""
        ports = serial.tools.list_ports.comports()
        self.com_box.clear()
        for port in ports:
            self.com_box.addItem(port.device)

    def get_selection(self):
        """Return currently selected (port, baud) as tuple."""
        port = self.com_box.currentText()
        try:
            baud = int(self.baud_box.currentText())
        except ValueError:
            baud = 9600
        return port, baud
