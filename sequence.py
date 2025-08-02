from bitarray import bitarray
from constants import ENCODING_MODES, Modes
from helpers import int_to_bitarray


def get_encoding_mode(string: str) -> bitarray:
    """
    TODO: IMPLEMENT!
    Return the byte representing the best encoding mode for the given string.
    """
    # Always return Latin1 Encoding for now
    return ENCODING_MODES[2]


def get_version(string: str) -> int:
    """
    TODO: IMPLEMENT!
    Get the optimal version for the given string
    """
    return 2


def get_length_bits_count(mode: bitarray, version: int) -> int:
    """
    Get the number of bits to be used for encoding the length of the encoded data.
    """
    LENGTH_BITS = [
        [10, 12, 14],  # Numeric
        [9, 11, 13],  # Alphanumeric
        [8, 16, 16],  # Latin1
        [8, 10, 12],  # Kanji
    ]  # 1-9, 10-26, 27-40

    # Get row
    if mode == Modes.ECI:
        # ECI Mode doesn't have a length section, so just return the one for Latin1
        mode_index = 2
    else:
        mode_index: int = ENCODING_MODES.index(mode)

    # Get column
    bits_index = 0
    if version > 9:
        bits_index = 1
    if version > 26:
        bits_index = 2

    return LENGTH_BITS[mode_index][bits_index]


def get_payload_bits(payload: str, mode: bitarray) -> bitarray:
    """
    TODO: IMPLEMENT!
    Convert the payload into a bitarray
    """
    bits = bitarray()
    if mode == Modes.LATIN1:
        bits.frombytes(payload.encode("latin-1"))

    return bits


def combine_message(
    encoding_mode: bitarray, length_bits: bitarray, payload_bits: bitarray, total_data_codewords: int
) -> bitarray:
    """
    Combine the separate elements into a single bitarray.
    This includes the termination block, and any necessary padding.
    """
    message_bits: bitarray = encoding_mode + length_bits + payload_bits

    if len(message_bits) / 8 > total_data_codewords:
        raise ValueError(
            f"Message too long! ({len(message_bits) / 8} codewords) Doesn't fit in {total_data_codewords} codewords."
        )

    # Add termination block. This is a maximum of 4 zeros, though it can be less if there is not enough space.
    termination_length = min(total_data_codewords * 8 - len(message_bits), 4)
    message_bits += "0" * termination_length

    # Add zeros to make a whole number of codewords/bytes
    remainder = len(message_bits) % 8
    if remainder:
        message_bits += "0" * (8 - remainder)

    # Add padding bytes of alternating 17 and 236
    remaining_bytes = total_data_codewords - (len(message_bits) // 8)
    for i in range(remaining_bytes):
        message_bits += int_to_bitarray(17, 8) if i % 2 else int_to_bitarray(236, 8)

    return message_bits


def get_byte_data(payload: str, data_codewords_count: int) -> list[int]:
    """Convert the given payload into the data bytes of the qr code"""
    encoding_mode = get_encoding_mode(payload)
    version = get_version(payload)

    length_bits_count = get_length_bits_count(encoding_mode, version=version)
    length_bits = int_to_bitarray(len(payload), length_bits_count)
    payload_bits = get_payload_bits(payload, encoding_mode)
    message_bits = combine_message(encoding_mode, length_bits, payload_bits, data_codewords_count)
    # print(message_bits)
    # print(list(message_bits.tobytes()))

    return list(message_bits.tobytes())
