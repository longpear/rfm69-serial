rfm69-serial 
============
A Python package for connecting PC to RFM69HCW board via USB Serial interface.

Overview
--------
RFM69HCW module from HopeRF is an excellent tool for RF communication under license-free ISM band. Despite the fact that
the community already has well-written library for interfacing the module to Arduino boards (e.g. RFM69 library from LowPowerLab @https://github.com/LowPowerLab/RFM69)
or Raspberry Pi computer (e.g. Rpi-RFM69 library @https://rpi-rfm69.readthedocs.io/en/latest/), there are many times I find myself in need of the module to work with PCs - which don't have SPI communication capability. 
The best way to achieve interfacing between the RFM69 module and PCs is by using UART/Serial via USB port.



Installation
------------
For un-published version, git-clone the package then perform local install an editable package.

`python3 -m pip install -e .`

Then, you are free to modify the source code however you like it.

APIs Reference
--------------
Refer to docs/


