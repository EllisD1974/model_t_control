from PyQt5 import QtWidgets, QtCore
from com_selector_widget import ComSelectorWidget
from serial_plot_widget import SerialPlotWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Plot with Persistent Connection")
        self.resize(800, 600)

        # --- QSettings ---
        self.settings = QtCore.QSettings("NEL", "SerialPlotApp")

        # --- Central Widget ---
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)

        # --- Top Controls: COM selector + Connect ---
        top_layout = QtWidgets.QHBoxLayout()
        self.com_selector = ComSelectorWidget()
        top_layout.addWidget(QtWidgets.QLabel("Device:"))
        top_layout.addWidget(self.com_selector)

        self.connect_btn = QtWidgets.QPushButton("Connect")
        top_layout.addWidget(self.connect_btn)
        main_layout.addLayout(top_layout)

        # --- Plot Widget ---
        self.plot_widget = SerialPlotWidget(channels=["A6", "A7"], max_points=1000)
        main_layout.addWidget(self.plot_widget)

        # --- Bottom Controls: Recording / Load ---
        bottom_layout = QtWidgets.QHBoxLayout()
        self.record_btn = QtWidgets.QPushButton("Start Recording")
        self.load_btn = QtWidgets.QPushButton("Load CSV")
        bottom_layout.addWidget(self.record_btn)
        bottom_layout.addWidget(self.load_btn)
        main_layout.addLayout(bottom_layout)

        # --- Signals ---
        self.connect_btn.clicked.connect(self.connect_device)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.load_btn.clicked.connect(self.load_csv)

        self.recording = False

        # --- Restore last COM and baud from QSettings ---
        last_port = self.settings.value("last_port", "")
        last_baud = self.settings.value("last_baud", "9600")
        if last_port:
            index = self.com_selector.com_box.findText(last_port)
            if index != -1:
                self.com_selector.com_box.setCurrentIndex(index)
        self.com_selector.baud_box.setCurrentText(str(last_baud))

    def connect_device(self):
        port, baud = self.com_selector.get_selection()
        if not port:
            QtWidgets.QMessageBox.warning(self, "Error", "No COM port selected!")
            return
        success = self.plot_widget.connect_serial(port, baud)
        if success:
            # Save successful connection to QSettings
            self.settings.setValue("last_port", port)
            self.settings.setValue("last_baud", str(baud))
        else:
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

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
