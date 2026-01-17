# serial_plot_widget.py
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import serial
import threading
import time
import csv


class SerialPlotWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, channels=None, max_points=200):
        super().__init__(parent)

        self.channels = channels or ["Channel1"]
        self.max_points = max_points

        # --- GUI ---
        self.layout = QtWidgets.QVBoxLayout(self)
        self.plot_widget = pg.PlotWidget(title="Serial Data")

        self.plot_widget.setYRange(0, 5)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.25)  # 25% opacity

        self.plot_widget.addLegend()
        self.layout.addWidget(self.plot_widget)

        self.curves = {}
        for ch in self.channels:
            self.curves[ch] = self.plot_widget.plot(pen=pg.intColor(len(self.curves)), name=ch)

        self.plot_widget.setYRange(0, 5)
        self.data = {ch: [] for ch in self.channels}

        # Serial
        self.ser = None
        self.thread = None
        self.running = False

        # Recording
        self.recording = False
        self.record_file = None
        self.csv_writer = None

        # Timer for GUI updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)

    # --- Serial Connection ---
    def connect_serial(self, port, baud=9600):
        try:
            self.ser = serial.Serial(port, baud, timeout=0.1)
            self.running = True
            self.thread = threading.Thread(target=self.read_serial)
            self.thread.daemon = True
            self.thread.start()
            return True
        except Exception as e:
            print("Serial connection error:", e)
            return False

    def disconnect_serial(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None

    # --- Background Serial Reading ---
    def read_serial(self):
        while self.running and self.ser:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    parts = line.split(',')
                    if len(parts) != len(self.channels):
                        continue
                    values = []
                    for i, ch in enumerate(self.channels):
                        value = float(parts[i])
                        self.data[ch].append(value)
                        if len(self.data[ch]) > self.max_points:
                            self.data[ch].pop(0)
                        values.append(value)

                    # Write to CSV if recording
                    if self.recording and self.csv_writer:
                        self.csv_writer.writerow(values)

            except Exception as e:
                print("Read error:", e)
            time.sleep(0.005)

    # --- Start/Stop Recording ---
    def start_recording(self, filename="recorded_data.csv"):
        try:
            self.record_file = open(filename, 'w', newline='')
            self.csv_writer = csv.writer(self.record_file)
            # Write header
            self.csv_writer.writerow(self.channels)
            self.recording = True
            print(f"Recording started: {filename}")
        except Exception as e:
            print("Failed to start recording:", e)

    def stop_recording(self):
        self.recording = False
        if self.record_file:
            self.record_file.close()
            self.record_file = None
            self.csv_writer = None
            print("Recording stopped.")

    # --- Update Plot ---
    def update_plot(self):
        for ch in self.channels:
            self.curves[ch].setData(self.data[ch])

    def load_csv(self, filename):
        """
        Load CSV data and plot it.
        CSV must have headers matching self.channels.
        """
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                # Clear existing data
                for ch in self.channels:
                    self.data[ch] = []
                for row in reader:
                    for ch in self.channels:
                        if ch in row:
                            self.data[ch].append(float(row[ch]))
            # Update plot immediately
            self.update_plot()
            print(f"Loaded {len(self.data[self.channels[0]])} samples from {filename}")
        except Exception as e:
            print("Failed to load CSV:", e)
