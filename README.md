rfm69-serial 
============
A Python package for connecting PC to RFM69HCW board via USB Serial interface.

Overview
--------
RFM69HCW module from HopeRF is an excellent tool for RF communication under license-free ISM band. Despite the fact that
the community already has well-written library for interfacing the module to Arduino boards (e.g. RFM69 library from LowPowerLab @https://github.com/LowPowerLab/RFM69)
or Raspberry Pi computer (e.g. Rpi-RFM69 library @https://rpi-rfm69.readthedocs.io/en/latest/), there are many times I find myself **in need of the module to work with PCs - which don't have SPI communication capability.** 
The best way to achieve interfacing between the RFM69 module and PCs is by using UART/Serial via USB port.

How does it work?
-----------------
The idea for this library is simple: 

An Arduino or Teensy board (middle man) is used to exchange data between RFM69HCW module and PC (running Linux OS). 
The connection diagram is shown as below:

**PC / Raspberry Pi (USB Port) <---> (USB Port) Arduino / Teensy Board (SPI) <---> RFM69HCW Module**

### Firmware Code
The firmware code for Arduino/Teensy device is included in **firmware/RFM69_Serial** directory. The code is based on well-known
RFM69 library from LowPowerLab @https://github.com/LowPowerLab/RFM69. The program is written in Arduino language (C++) with 
a set of commands (pre-defined by command opcode table). At the system start-up, the device is connected to PC using its USB port. 
After initialization process, the device sits idle waiting for the command opcode (and possibly data) to be transferred through USB port. 
The program selects the corresponding function and executes them to communicate with physical RFM69 module through SPI connection.
After execution of the command, the device go back to waiting state, ready for the next command to be transferred.

_Note: as the Arduino program uses RFM69 library from LowPowerLab, you need to install the library to your Arduino IDE first._

### Python Library
The Python library covers almost every function/method from the RFM69 Arduino library. Each function is given an unique opcode
as shown in the table below:

![RFM69 Serial Function LUT](/img/RFM69_Serial_function_LUT.jpg)
_Table 1. function opcode look-up table._

At the system start-up, the middle man device is initialized using default values for system parameters such as device ID, 
network ID, chip select pin and interrupt pin. It is user's responsibility to reinitialize the middle man device to your 
own system parameter set before requesting any other function to the RFM69 device. This can be done by calling constructor method
with correct system parameter set for corresponding physical board (see examples in /examples).

Installation
------------
### Firmware Installation
RFM69 Serial project currently supports all Arduino devices as well as devices that use Arduino IDE. The firmware (Arduino sketch)
can be found in **firmware/RFM69_Serial/RFM69_Serial.ino**. The only thing needed to be done is to upload the sketch to your 
Arduino device.

### Python Library Installation
For general usage, user can install the package from PyPi:

`python3 -m pip install rfm69-serial`

or 

`pip3 install rfm69-serial`

For un-published version or developer version, git-clone the specific package then perform local install an editable package.

`python3 -m pip install -e .`

Then, you are free to modify the source code however you like it.

Supported Hardware and Limitations
----------------------------------
RFM69 Serial library supports most Arduino devices. The only problem is that "low-end" Arduino boards such as Arduino UNO
do NOT support serial baudrate greater than 115200 kbps. Therefore, there is limitation in data transfer speed between 
PC and physical RFM69 module using such middle man devices.

Here is the list of devices that I used to test the RFM69 Serial library:

![Supported Device List](/img/Arduino_USB_serial_speed.jpg)
_Table 2. Supported and Tested Physical Boards (Middle Man)._

(*): For Arduino MKRZERO, its serial buffer is smaller than 64 bytes -> cannot handle 64-byte message. Thus, 32-bit long
message is used instead.

**Recommendation:** I use Teensy series as the middle man when it is possible as this class of devices comes with a well-designed
USB serial connection to PC.

APIs Reference
--------------
Refer to **docs/**

Documentation of RFM69-Serial library is done automatically using Sphynx.
Access **build/html/** for the lastest build of the docs.
