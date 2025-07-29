from bitarray import bitarray


class Modes:
    NUMERIC = bitarray("0001")
    ASCII = bitarray("0010")  # (Alpha numeric)
    LATIN1 = bitarray("0100")
    KANJI = bitarray("1000")
    ECI = bitarray("0111")  # (Extended Channel Interpretation) e.g. UTF-8


ENCODING_MODES = [Modes.NUMERIC, Modes.ASCII, Modes.LATIN1, Modes.KANJI, Modes.ECI]


TERMINATION_BLOCK = bitarray("0000")