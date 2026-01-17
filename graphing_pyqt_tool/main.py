from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from pyqtgraph.exporters import ImageExporter
from com_selector_widget import ComSelectorWidget
from serial_plot_widget import SerialPlotWidget


def resource_path(relative_path):
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base_path / relative_path


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Plot with Toggle Connect")
        self.resize(800, 600)
        self.setWindowIcon(QIcon(str(resource_path("resources/icons/icon.ico"))))

        self.settings = QtCore.QSettings("NEL", "SerialPlotApp")

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)

        # --- Top Controls ---
        top_layout = QtWidgets.QHBoxLayout()
        self.com_selector = ComSelectorWidget()
        top_layout.addWidget(QtWidgets.QLabel("Device:"))
        top_layout.addWidget(self.com_selector)

        # Reuse Connect button for toggle
        self.connect_btn = QtWidgets.QPushButton("Connect")
        top_layout.addWidget(self.connect_btn)

        self.pause_btn = QtWidgets.QPushButton("Pause")
        top_layout.addWidget(self.pause_btn)
        main_layout.addLayout(top_layout)

        # --- Plot Widget ---
        self.plot_widget = SerialPlotWidget(channels=["A6", "A7"], max_points=1000)
        main_layout.addWidget(self.plot_widget)

        # --- Bottom Controls ---
        bottom_layout = QtWidgets.QHBoxLayout()
        self.record_btn = QtWidgets.QPushButton("Start Recording")
        self.load_btn = QtWidgets.QPushButton("Load CSV")
        self.screenshot_btn = QtWidgets.QPushButton("Save Screenshot")
        bottom_layout.addWidget(self.record_btn)
        bottom_layout.addWidget(self.load_btn)
        bottom_layout.addWidget(self.screenshot_btn)
        main_layout.addLayout(bottom_layout)

        # --- Signals ---
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.load_btn.clicked.connect(self.load_csv)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.screenshot_btn.clicked.connect(self.save_screenshot)

        self.recording = False
        self.connected = False

        # --- Restore last COM/baud from QSettings ---
        last_port = self.settings.value("last_port", "")
        last_baud = self.settings.value("last_baud", "9600")
        if last_port:
            index = self.com_selector.com_box.findText(last_port)
            if index != -1:
                self.com_selector.com_box.setCurrentIndex(index)
        self.com_selector.baud_box.setCurrentText(str(last_baud))

    # --- Connect/Disconnect Toggle ---
    def toggle_connection(self):
        if not self.connected:
            # Try to connect
            port, baud = self.com_selector.get_selection()
            if not port:
                QtWidgets.QMessageBox.warning(self, "Error", "No COM port selected!")
                return
            success = self.plot_widget.connect_serial(port, baud)
            if success:
                self.connected = True
                self.connect_btn.setText("Disconnect")
                QtWidgets.QMessageBox.information(self, "Connected", f"Connected to {port} at {baud} baud")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to connect to {port}.")
        else:
            # Disconnect
            self.plot_widget.disconnect_serial()
            self.connected = False
            self.connect_btn.setText("Connect")
            QtWidgets.QMessageBox.information(self, "Disconnected", "Serial connection closed.")

    # --- Other Methods ---
    def toggle_recording(self):
        if not self.recording:
            self.plot_widget.start_recording("pot_data.csv")
            self.record_btn.setText("Stop Recording")
        else:
            self.plot_widget.stop_recording()
            self.record_btn.setText("Start Recording")
        self.recording = not self.recording

    def toggle_pause(self):
        self.plot_widget.toggle_pause()
        if self.plot_widget.paused:
            self.pause_btn.setText("Resume")
        else:
            self.pause_btn.setText("Pause")

    def load_csv(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv)"
        )
        if filename:
            self.plot_widget.load_csv(filename)

    def save_screenshot(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Screenshot", "", "PNG Files (*.png);;JPEG Files (*.jpg)"
        )
        if filename:
            try:
                exporter = ImageExporter(self.plot_widget.plot_widget.plotItem)
                exporter.export(filename)
                QtWidgets.QMessageBox.information(self, "Saved", f"Screenshot saved to {filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save screenshot:\n{e}")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
