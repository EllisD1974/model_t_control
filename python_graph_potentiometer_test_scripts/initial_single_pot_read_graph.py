## FOR SINGLE POT
import serial
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

# --- Arduino Serial Setup ---
ser = serial.Serial('COM3', 115200, timeout=1)

# --- PyQtGraph App Setup ---
app = QtWidgets.QApplication([])

win = pg.GraphicsLayoutWidget(show=True, title="Potentiometer Real-Time Plot")
win.resize(800, 400)
win.setWindowTitle('Potentiometer Live Graph')

plot = win.addPlot(title="Voltage (0-5V)")
plot.setYRange(0, 5)
curve = plot.plot(pen='y')

data = []

# --- Update Function ---
def update():
    while ser.in_waiting:
        line_raw = ser.readline().decode('utf-8').strip()
        if line_raw:
            try:
                parts = line_raw.split(',')
                if len(parts) == 2:
                    voltage = float(parts[1])
                    data.append(voltage)
                    if len(data) > 200:      # keep last 200 points
                        data.pop(0)
            except:
                pass

    curve.setData(data)

# --- Timer for real-time updates ---
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(20)  # update every 20ms (~50 Hz)

# --- Start the app ---
app.exec_()
