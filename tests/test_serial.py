#!/usr/bin/env python3

# Test bases for the library
# This is not automatic testing program

import sys
import serial
import time

# Serial port init
ser = serial.Serial('/dev/ttyACM0', timeout=1)
# ser = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=1)
# ser = serial.Serial('/dev/ttyACM1', baudrate=1000000, timeout=1)

# Serial port name
print("Serial Device = ", ser.name)

# Test subject
single_byte = b'a'
sample_msg32 = b'hello, this is a sample message!'  # 32 bytes sample
sample_msg64 = b'hello, this is a sample message!!egassem elpmas a si siht ,olleh'  # 64 bytes sample

# Main program
try:
    while True:
        data = input("Send > ")

        start_time = time.perf_counter()
        ser.write(data.encode('ascii'))
        # ser.write(sample_msg32)

        recv = ser.read()   # initialize recv variable

        # wait for hardware serial to receive the remaining bytes? this is hardware dependent
        # time.sleep(0.005)
        # while ser.in_waiting != 0:
        #     recv += ser.read()

        for _ in range(0, len(data)-2):
            recv += ser.read()

        t_delay = (time.perf_counter() - start_time) * 1000
        ser.reset_input_buffer()

        print("Recv < ", recv)
        print("Delay(ms) = ", t_delay)

except KeyboardInterrupt:
    ser.close()
    print("Bye!")
