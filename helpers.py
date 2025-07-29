from bitarray import bitarray


def print_byte(*args):
    endchar = " "
    for i, arg in enumerate(args):
        if i == len(args) - 1:
            endchar = "\n"

        if isinstance(arg, int):
            # print(bin(arg)[2:].rjust(8, "0"), end=endchar)
            print(bin(arg)[2:], end=endchar)
        else:
            print(arg, end=endchar)


def int_to_bitarray(value: int, length: int = 0) -> bitarray:
    """Convert an into into a bytearray of the given length.
    0 bits will only be added to fit length, not removed."""
    string = bin(value)[2:]
    if length:
        string = string.rjust(length, "0")
    return bitarray(string)
