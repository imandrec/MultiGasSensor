import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
import struct
import math
import time

# Constants
CMD_GET_GAS_CONCENTRATION = 0x86
DFROBOT_GAS_O2 = 0x05
DFROBOT_GAS_PH3 = 0x45
DFROBOT_GAS_ON = True

class DFRobotMultiGasSensor:
    def __init__(self, i2c, addr=0x74):
        self.i2c_device = I2CDevice(i2c, addr)
        self._temp = 25 
        self._tempswitch = False
        self._gastype = None

    def read_gas_concentration_ppm(self):
        command = CMD_GET_GAS_CONCENTRATION
        self.write_data(command, 0)
        time.sleep(0.1) 

        recvbuf = self.read_data(0, 9)
        print("Raw data received:", recvbuf)

        if self._check_sum(recvbuf) == recvbuf[8]:
            self._gastype = recvbuf[4]  
            decimal_digits = recvbuf[5]
            concentration = ((recvbuf[2] << 8) + recvbuf[3]) * 1.0

            if decimal_digits == 1:
                concentration *= 0.1
            elif decimal_digits == 2:
                concentration *= 0.01

            if self._tempswitch and self._gastype == DFRobot_GAS_PH3:
                concentration = self._temp_correction(concentration)

            print("Concentration (ppm):", concentration)
            return concentration
        else:
            print("Invalid data received")
            return 0.0

    def _check_sum(self, data):
        checksum = 0
        for i in range(len(data) - 1):
            checksum += data[i]
        checksum = ~checksum & 0xFF
        return checksum

    def _temp_correction(self, concentration):
        if -20 < self._temp <= 40:
            return concentration / (0.005 * self._temp + 0.9)
        else:
            return concentration

    def write_data(self, command, mode):
        if not (0 <= command <= 0xFF and 0 <= mode <= 0xFF):
            raise ValueError("Command and mode must be byte values (0-255)")

        buf = bytearray([0xFF, 0x01, command, mode, 0x00, 0x00, 0x00, 0x00])
        checksum = self._check_sum(buf)
        buf.append(checksum)

        with self.i2c_device as i2c:
            i2c.write(buf)
            print("Writing to I2C:", buf)

    def read_data(self, reg, length):
        result = bytearray(length)
        try:
            with self.i2c_device as i2c:
                i2c.write_then_readinto(bytearray([reg]), result)
        except ValueError:
            print("I2C read error")
            return None
        print("Reading from I2C:", result)
        return result
