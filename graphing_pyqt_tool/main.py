# main_app_with_screenshot.py
from PyQt5 import QtWidgets
from pyqtgraph.exporters import ImageExporter
from com_selector_widget import ComSelectorWidget
from serial_plot_widget import SerialPlotWidget

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Plot with Screenshot")
        self.resize(800, 600)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)

        # --- Top Controls ---
        top_layout = QtWidgets.QHBoxLayout()
        self.com_selector = ComSelectorWidget()
        top_layout.addWidget(QtWidgets.QLabel("Device:"))
        top_layout.addWidget(self.com_selector)

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
        self.connect_btn.clicked.connect(self.connect_device)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.load_btn.clicked.connect(self.load_csv)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.screenshot_btn.clicked.connect(self.save_screenshot)

        self.recording = False

    def connect_device(self):
        port, baud = self.com_selector.get_selection()
        if not port:
            QtWidgets.QMessageBox.warning(self, "Error", "No COM port selected!")
            return
        success = self.plot_widget.connect_serial(port, baud)
        if not success:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to connect to {port}.")

    def toggle_recording(self):
        if not self.recording:
            self.plot_widget.start_recording("pot_data.csv")
            self.record_btn.setText("Stop Recording")
        else:
            self.plot_widget.stop_recording()
            self.record_btn.setText("Start Recording")
        self.recording = not self.recording

    def load_csv(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv)"
        )
        if filename:
            self.plot_widget.load_csv(filename)

    def toggle_pause(self):
        self.plot_widget.toggle_pause()
        if self.plot_widget.paused:
            self.pause_btn.setText("Resume")
        else:
            self.pause_btn.setText("Pause")

    def save_screenshot(self):
        # Open file dialog
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
