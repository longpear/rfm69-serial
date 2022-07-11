#!/usr/bin/env python3

# Test bases for the library
# This is not automatic testing program

import sys
import pyftdi.serialext
from pyftdi.ftdi import Ftdi
import time

# Serial port init
ser = pyftdi.serialext.serial_for_url('ftdi://ftdi:232:AD0JIPUE/1', baudrate=9600)

# Serial port name
Ftdi.show_devices()

# Test subject
single_byte = b'a'
sample_msg32 = b'hello, this is a sample message!'  # 32 bytes sample
sample_msg64 = b'hello, this is a sample message!!egassem elpmas a si siht ,olleh'  # 64 bytes sample

# Main program
try:
    while True:
        data = input("Send > ")

        start_time = time.perf_counter()
        # ser.write(data.encode('ascii'))
        ser.write(sample_msg64)

        recv = ser.read()   # initialize recv variable

        # wait for hardware serial to receive the remaining bytes? this is hardware dependent
        # time.sleep(0.005)
        # while ser.in_waiting != 0:
        #     recv += ser.read()

        for _ in range(0, len(sample_msg64)-1):
            recv += ser.read()

        t_delay = (time.perf_counter() - start_time) * 1000
        ser.reset_input_buffer()

        print("Recv < ", recv)
        print("Delay(ms) = ", t_delay)

except KeyboardInterrupt:
    ser.close()
    print("Bye!")
