from million_dollar_dream.bitfield import BitField


class TestBitField(object):

    def test_zero_and_set(self):
        size = 128
        bitfield = BitField(size)
        bitfield.zero()
        for position in range(size):
            assert bitfield.getbit(position) == 0
            bitfield.setbit(position)
            assert bitfield.getbit(position) == 1

    def test_one_and_unset(self):
        size = 128
        bitfield = BitField(size)
        bitfield.one()
        for position in range(size):
            assert bitfield.getbit(position) == 1
            bitfield.unsetbit(position)
            assert bitfield.getbit(position) == 0

    def test_get_pos(self):
        size = 128
        bitfield = BitField(size)
        position = bitfield.getpos(100)
        assert position.byte == 12
        assert position.bit == 4
