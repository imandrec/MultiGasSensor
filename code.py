import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
import struct
import math
import time
from DFRobotMultiGasSensor import *

i2c = busio.I2C(board.SCL, board.SDA)
sensor = DFRobotMultiGasSensor(i2c)

while True:
    concentration = sensor.read_gas_concentration_ppm()
    print("Gas concentration: {:.2f} ppm".format(concentration))
    time.sleep(10)
