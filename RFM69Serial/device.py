import time
import serial
from RFM69Serial import RFM69Packet

# Constants and globals
RFM69_FSTEP = 61.03515625


class Rfm69SerialDevice(serial.Serial):
    """This class provides serial device objects that represent physical RFM69 module as if it is connected
    directly to PC/Laptop.
    Thus, device parameters such as addresses, pin configurations are passed to constructor to create a runnable
    serial device object.
    """

    def __init__(self, address=1, network=101, cs_pin=0, int_pin=1, port="/dev/ttyACM0", time_out=1):
        super(Rfm69SerialDevice, self).__init__(port=port, timeout=time_out)

        self._devAddress = address
        self._networkID = network

        # storage for chip select and interrupt pins
        self._CS_Pin = cs_pin
        self._Int_Pin = int_pin

        # encryption mode data
        self._is_encrypted = False
        self._encryption_key = 'samplekey16bytes'

        # initialize RFM69 module
        t_start = time.perf_counter()
        while time.perf_counter() - t_start < 10:
            time.sleep(0.1) # Hardware deceleration factor
            if self._init_rf_module():
                break
        else:
            raise TimeoutError("Could not connect to RFM69 device!")

    @property
    def device_address(self):
        return self._devAddress

    @property
    def network_id(self):
        return self._networkID

    @property
    def chip_select_pin(self):
        return self._CS_Pin

    @property
    def interrupt_pin(self):
        return self._Int_Pin

    @property
    def is_encrypted(self):
        return self._is_encrypted

    @property
    def encryption_key(self):
        return self._encryption_key

    def _serial_transfer(self, command) -> bool:
        """Perform single serial transaction for data exchange between PC and Arduino devices.
        This is the atomic utility method for RFM69 Serial bridge library. It should be noted that the method
        only suitable for covering SET-type functions. GET-type functons that return data bytes should be
        handled differently as they may return values different than Boolean.

        :param  command: a single or serie of bytes object(s) to transfer to the Arduino device. It should be noted
            that command always start with $ followed by opcode and data arguments.
        :return: True if the transaction is successful, False otherwise.
        """

        if type(command) == bytes:
            self.write(command)
            recv = self.read()
            self.reset_input_buffer()
        else:
            raise TypeError("Argument command must be of type (bytes)")

        if recv == b'y':
            return True
        else:
            return False

    # def _serial_get(self, command):
    #     pass

    def _init_rf_module(self):
        """Initialize RFM69 module via Serial port.
        This function is called by the constructor method right after device parameters are established.

        :return: True if the RFM69 module is initialized successfully, False otherwise.
        """

        serial_cmd = b'$\x00'
        serial_cmd += self._devAddress.to_bytes(1, 'little')
        serial_cmd += self._networkID.to_bytes(1, 'little')
        serial_cmd += self._CS_Pin.to_bytes(1, 'little')
        serial_cmd += self._Int_Pin.to_bytes(1, 'little')

        return self._serial_transfer(serial_cmd)

    def set_dev_address(self, address):
        """Set the address of RFM69 module, default value is 1
        Note: it should noted that the device address in this library is currently limited to 254, though
        the original Arduino RFM69 implement maximum 1024 nodes in a network. The reason is for simplicity.
        This may be reviewed and improved in the next version ;P

        :param address: nominated address of the RFM69 module
        :return: True if the device's address is set, False otherwise.
        """

        if type(address) == int and 0 < address < 255:
            self._devAddress = address
        else:
            self._devAddress = 1

        serial_cmd = b'$\x01' + self._devAddress.to_bytes(1, 'little')
        return self._serial_transfer(serial_cmd)

    def set_network_id(self, nid):
        """Set the network ID of RFM69 module, default value is 101

        :param nid: nominated network ID, max 255
        :return: True if the device's network ID is set, False otherwise.
        """

        if type(nid) == int and 0 < nid < 255:
            self._networkID = nid
        else:
            self._networkID = 101

        serial_cmd = b'$\x02' + self._networkID.to_bytes(1, 'little')
        return self._serial_transfer(serial_cmd)

    def send_msg(self, target_addr, msg, ack_request=False):
        """Send a single message to target device specified by target address.
        This method covers the send() function in RFM69 Arduino library.

        :param  target_addr: the address of receiving Arduino board.
        :param  msg: message to send, message must be of type string or a list of byte values (0-255).
        :param  ack_request: acknowledge request status, if True, the request is embedded in the message.

        :return: True if the message is sent, False otherwise.
        """

        ack = b'\x01' if ack_request else b'\x00'
        # check type
        assert type(target_addr) == int

        if type(msg) == str:
            serial_cmd = b'$\x03' + target_addr.to_bytes(1, 'little') + ack + \
                        len(msg).to_bytes(1, 'little') + msg.encode('ASCII')
        elif type(msg) == list:
            serial_cmd = b'$\x03' + target_addr.to_bytes(1, 'little') + ack + len(msg).to_bytes(1, 'little')
            for item in msg:
                serial_cmd += item.to_bytes(1, 'little')
        else:
            raise TypeError("message must be a list or string")

        return self._serial_transfer(serial_cmd)

    def send_msg_with_retry(self, target_addr, msg, retries=2, time_out=50):
        """Send a single message a number (retries) of times to ensure the message deliverance.
        This method covers the sendWithRetry() function in RFM69 Arduino library.

        :param  target_addr: the address of receiving Arduino board.
        :param  msg: message to send, message must be of type string or a list of byte values (0-255)
        :param  retries: number of times the sender attempts to send the message to the receiver.
        :param  time_out: each attempt waits for "time_out" miliseconds before moving to the next attempt.

        :return: True if the message is sent, False otherwise.
        """

        assert type(target_addr) == int

        if type(msg) == str:
            serial_cmd = b'$\x04' + target_addr.to_bytes(1, 'little') + retries.to_bytes(1, 'little') + \
                          time_out.to_bytes(1, 'little') + len(msg).to_bytes(1, 'little') + msg.encode('ASCII')
        elif type(msg) == list:
            serial_cmd = b'$\x04' + target_addr.to_bytes(1, 'little') + retries.to_bytes(1, 'little') + \
                          time_out.to_bytes(1, 'little') + len(msg).to_bytes(1, 'little')
            for item in msg:
                serial_cmd += item.to_bytes(1, 'little')
        else:
            raise TypeError("outbound message must be a list or string")

        return self._serial_transfer(serial_cmd)

    def begin_receive(self):
        """Change RFM69 module from TX to RX and wait for message to arrive.
        This method covers receiveBegin() function in RFM69 Arduino library.

        :return: True if state changed, False otherwise.
        """

        serial_cmd = b'$\x05'
        return self._serial_transfer(serial_cmd)

    def receive_done(self):
        """Check if there is a newly received message in device's memory.
        This method covers receiveDone() function in RFM69 Arduino library.

        :return: True if there is a new message, False otherwise.
        """

        serial_cmd = b'$\x06'
        return self._serial_transfer(serial_cmd)

    def ACK_received(self, target_addr=2):
        """Check if an acknowledge is embedded in newly received message from the device at target_addr
        Should be polled immediately after sending a packet with ACK request
        """

        serial_cmd = b'$\x07' + target_addr.to_bytes(1, 'little')
        return self._serial_transfer(serial_cmd)

    def ACK_requested(self):
        """Check whether an ACK was requested in the last received packet
        """

        serial_cmd = b'$\x08'
        return self._serial_transfer(serial_cmd)

    def send_ACK(self, msg):
        """Send back an acknowledge message to the sender if ACK_requested is detected.
        Should be called immediately after reception in case sender wants ACK.

        :param msg: some message to be sent along with ACK.

        :return: True if ACK is sent, False otherwise.
        """

        if type(msg) == str:
            serial_cmd = b'$\x09' + len(msg).to_bytes(1, 'little') + msg.encode('ASCII')
        elif type(msg) == list:
            serial_cmd = b'$\x09' + len(msg).to_bytes(1, 'little')
            for item in msg:
                serial_cmd += item.to_bytes(1, 'little')
        else:
            raise TypeError("outbound message must be a list or string")

        return self._serial_transfer(serial_cmd)

    def get_frequency(self):
        """Read the current frequency setting from RFM69 module.
        This method covers getFrequency() function in RFM69 Arduino library.

        :return: current set carrier frequency (in decimal) if read command succeeded. None if failed.
        """

        serial_cmd = b'$\x0A'
        self.write(serial_cmd)
        if self.read() == b'y':
            frf_MSB = ord(self.read())
            frf_MID = ord(self.read())
            frf_LSB = ord(self.read())
            frequency = (frf_MSB << 16) + (frf_MID << 8) + frf_LSB
            return int(round(RFM69_FSTEP * frequency))
        else:
            return None

    def set_frequency(self, freq=915000000):
        """Set the carrier frequency of RFM69 module to a specific value/
        This method covers getFrequency() function in RFM69 Arduino library.

        :param freq: nominated carrier frequency to be set for the RFM69 module (in decimal)

        :return: True if set, False otherwise.
        """

        serial_cmd = b'$\x0B'
        bitmask = 0xFF
        for i in range(0, 4):
            nibble = (freq >> (i * 8)) & bitmask
            serial_cmd += (nibble.to_bytes(1, 'little'))
        return self._serial_transfer(serial_cmd)

    def encrypt(self, key='samplekey16bytes'):
        """Enable/Disable encryption feature on RFM69 module.
        This method covers encrypt() function in RFM69 Arduino library.

        :param key: 16-byte long encryption key to be set for RFM69 module's AES engine.
                    If the key is set to null string (''), the encryption mode is disabled.
                    If no key is provided, the encryption mode is set to be enabled with default key 'samplekey16bytes'.

        :return: True if the command was acknowledge, False otherwie.
        """

        serial_cmd = b'$\x0C'
        if len(key) == 0:
            self._is_encrypted = False
            serial_cmd += b'\x00'
        elif len(key) == 16:
            self._is_encrypted = True
            self._encryption_key = key

            serial_cmd += b'\x01'
            for i in range(0, 16):
                serial_cmd += key[i].encode('ascii')
        else:
            # invalid key, disable encryption feature
            self._is_encrypted = False
            serial_cmd += b'\x00'

        return self._serial_transfer(serial_cmd)

    def set_chip_select(self, pin=0):
        """Set chip select pin on the serial device.
        This method covers setCS() function in RFM69 Arduino library.

        :param pin: nominated dev board's digital pin for chip select

        :return: True if the pin is set, False otherwise.
        """

        if type(pin) == int and 0 <= pin < 255:
            serial_cmd = b'$\x0D' + pin.to_bytes(1, 'little')
            self._CS_Pin = pin
        else:
            raise ValueError("pin must be a number typed int")
        return self._serial_transfer(serial_cmd)

    def set_interrupt_pin(self, pin=0):
        """Set interrupt pin on the serial device.
        This method covers setIrq() function in RFM69 Arduino library.

        :param pin: nominated dev board's digital pin for interrupt function.

        :return: True if the pin is set, False otherwise.
        """

        if type(pin) == int and 0 <= pin < 255:
            serial_cmd = b'$\x0E' + pin.to_bytes(1, 'little')
            self._Int_Pin = pin
        else:
            raise ValueError("pin must be a number typed int")
        return self._serial_transfer(serial_cmd)

    def get_rssi(self, force=False):
        """Get signal strength value from RFM69 module.
        This method covers readRSSI() function in RFM69 Arduino library.

        :param force: Force trigger state.

        :return: RSSI value in decimal if read command is successful. None otherwise.
        """

        forceTrigger = b'\x01' if force else b'\x00'
        serial_cmd = b'$\x0F' + forceTrigger
        self.write(serial_cmd)
        if self.read() == b'y':
            return -ord(self.read())
        else:
            return None

    def set_spy(self, enable=False):
        """Enable RFM69 module promiscuous mode to listen to any packet in the network.
        This method covers spyMode() function in RFM69 Arduino library.

        :param enable: bool value to enable/disable the spy mode. default to False.

        :return: True if the command is successful. False otherwise.
        """

        enabled = b'\x01' if enable else b'\x00'
        serial_cmd = b'$\x10' + enabled
        return self._serial_transfer(serial_cmd)

    def set_high_power(self, enable=True):
        enabled = b'\x01' if enable else b'\x00'
        serial_cmd = b'$\x11' + enabled
        return self._serial_transfer(serial_cmd)

    def set_power_level(self, level=100):
        serial_cmd = b'$\x11' + level.to_bytes(1, 'little')
        return self._serial_transfer(serial_cmd)

    def get_power_level(self):
        pass

    def sleep(self):
        """Put the RFM69 module into sleep mode.

        :return: True if the module is set to sleep. False otherwise.
        """

        serial_cmd = b'$\x15'
        return self._serial_transfer(serial_cmd)

    def read_temperature(self):
        pass

    def rc_calibration(self):
        serial_cmd = b'$\x17'
        return self._serial_transfer(serial_cmd)

    def read_register(self, reg_addr):
        """Read value from configuraton and status registers built-in RFM69 module.
        This method covers readReg() function in RFM69 Arduino library.

        :param reg_addr: Register address, it must be of type bytes

        :return: the current value of the register @reg_addr if successful. None if failed.
        """

        if type(reg_addr) == bytes:
            serial_cmd = b'$\x1A' + reg_addr
            self.write(serial_cmd)
            if self.read() == b'y':
                return self.read()
            else:
                return None
        else:
            raise TypeError("Target register address must be of type bytes")

    def write_register(self, reg_addr, value):
        """Write value to specific configuraton and status registers built-in RFM69 module.
        This method covers writeReg() function in RFM69 Arduino library.

        :param reg_addr: Register address, it must be of type bytes
        :param value: specific value to write to register @reg_addr, must be of type bytes

        :return True if write command is successful, False otherwise.
        """

        if type(reg_addr) == bytes and type(value) == bytes:
            serial_cmd = b'$\x1B' + reg_addr + value
            return self._serial_transfer(serial_cmd)
        else:
            raise TypeError("Target register address and value must be of type bytes")

    def get_rx_data(self):
        """Request received data from RFM69 device.
        This method assumes that the caller already checked for message received status.

        :return: If success, returns a RFM69Packet object containing sender address and the received message.
        Else, None.
        Also note that received message is a list of bytes object, use appropriate methods to convert it to
        other type.
        """

        rx_packet = RFM69Packet()

        serial_cmd = b'$\x1E'
        self.write(serial_cmd)

        ack_byte = self.read()
        rx_packet.sender = ord(self.read())
        msg_len = ord(self.read())
        for _ in range(0, msg_len):
            rx_packet.message.append(self.read())

        if ack_byte == b'y':
            return rx_packet
        else:
            return None

    def is_device_connected(self):
        """Check if serial device is online and connected.
        The strategy is to use read_register() method to figure out payload length (which is 66).
        If the number 66 is returned, we know that both SPI and UART connection are good.

        :return: True if the serial device is present and connected to PC, False otherwise
        """
        if ord(self.read_register(b'\x38')) == 66:
            return True
        else:
            return False
