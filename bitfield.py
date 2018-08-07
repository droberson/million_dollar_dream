from math import ceil
from collections import namedtuple

class BitField():
    """BitField class -- Implements bitfields using the standard library.

    Attributes:
        size (int) - size of the bit field
        bitfield (bytearray) - byte array containing the bitfield
        Position (namedtuple) - Named tuple representing a bit's location
                                within the bytearray.
    """
    def __init__(self, size):
        self.size = size # TODO bounds checking
        self.bitfield = bytearray([0x00] * int(ceil(size / 8)))
        self.position = namedtuple("position", ["byte", "bit"])

    def setbit(self, position):
        """BitField.setbit() - set bit at specified position to 1

        Args:
            position (int) - Position to set.

        Returns:
            Nothing.
        """
        pos = self.getpos(position)
        self.bitfield[pos.byte] |= (0x01 << pos.bit) & 0xff

    def unsetbit(self, position):
        """BitField.unsetbit() - set bit at specified position to 0

        Args:
            position (int) - Position to unset.

        Returns:
            Nothing.
        """
        pos = self.getpos(position)
        self.bitfield[pos.byte] &= ~(0x01 << pos.bit) & 0xff

    def getbit(self, position):
        """Bitfield.getbit() - Retrieve contents of bit at a specific location.

        Args:
            position (int) - Position to retrieve.

        Returns:
            True if bit is set (1).
            False if bit is not set (0).
        """
        pos = self.getpos(position)
        if self.bitfield[pos.byte] & ((0x01 << pos.bit) & 0xff):
            return True
        return False

    def zero(self):
        """Bitfield.zero() - Set all bits to zero.

        Args:
            None

        Returns:
            Nothing
        """
        for position in range(len(self.bitfield)):
            self.bitfield[position] = 0x00

    def one(self):
        """Bitfield.one() - Set all bits to one.

        Args:
            None

        Returns:
            Nothing
        """
        for position in range(len(self.bitfield)):
            self.bitfield[position] = 0xff

    def getpos(self, position):
        """Bitfield.getpos() - Get position of a bit in a bitfield.

        Args:
            position (int) - Position to retrieve.

        Returns:
            position (namedtuple) containing byte and bit positions.

        Example:
            I want to get the position of the 100th bit. Since this is stored
            in a bytearray, one can't just do something like this:
                value = bitfield[100] # This will get the 100th byte, not bit!

            The 100th bit of a bytearray will be 4 bits into the 12th byte:
                >>> bitfield.getpos(100)
                Position(byte=12, bit=4)
        """
        bytepos = int(ceil(position / 8)) - 1
        bitpos = position % 8
        if bitpos != 0:
            bitpos = 8 - bitpos
        return self.position(bytepos, bitpos)


