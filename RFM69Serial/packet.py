# RFM69 Packet Class

class RFM69Packet:
    """RFM69 packet class to store received message in a defined data structure.
    Currently, each packet object contains information about sender address and received message
    from the sender. The class also provides a public method to convert data list to string if necessary.

    __slots__ is used to reduce memory.
    """

    __slots__ = '_sender_addr', '_message_data'

    def __init__(self, addr=0):
        self._sender_addr = addr
        self._message_data = []

    @property
    def sender(self):
        return self._sender_addr

    @sender.setter
    def sender(self, address=0):
        if type(address) == int and 0 <= address < 255:
            self._sender_addr = address
        else:
            raise ValueError("Sender address must be of type int (0 <= id < 255)")

    @property
    def message(self):
        return self._message_data

    @message.setter
    def message(self, data):
        if type(data) == list:
            self._message_data = data
        else:
            raise TypeError("Received data must be a list")

    def message_to_string(self):
        """Convert message data list to string if string type message is required by callers.
        """
        return "".join([chr(item) for item in self._message_data])
