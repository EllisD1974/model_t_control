## FOR DOUBLE POT
import serial
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

# --- Arduino Serial Setup ---
ser = serial.Serial('COM3', 115200, timeout=1)

# --- PyQtGraph App Setup ---
app = QtWidgets.QApplication([])

win = pg.GraphicsLayoutWidget(show=True, title="Two Potentiometers Live Plot")
win.resize(800, 400)
win.setWindowTitle('Potentiometer Live Graph')

plot = win.addPlot(title="Voltage (0-5V)")
plot.setYRange(0, 5)
plot.addLegend()

curve1 = plot.plot(pen='y', name='Pot A6')
curve2 = plot.plot(pen='c', name='Pot A7')

data1 = []
data2 = []

# --- Update Function ---
def update():
    while ser.in_waiting:
        line_raw = ser.readline().decode('utf-8').strip()
        if line_raw:
            try:
                parts = line_raw.split(',')
                if len(parts) == 2:
                    voltage1 = float(parts[0])
                    voltage2 = float(parts[1])

                    data1.append(voltage1)
                    data2.append(voltage2)

                    # Keep only the last 200 points
                    if len(data1) > 200:
                        data1.pop(0)
                        data2.pop(0)

                    # Update curves
                    curve1.setData(data1)
                    curve2.setData(data2)
            except:
                pass

# --- Timer for real-time updates ---
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(20)  # update every 20ms (~50 Hz)

# --- Start the app ---
app.exec_()
