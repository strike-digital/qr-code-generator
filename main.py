import math

from bitarray import bitarray
from display import display_qr_code
from error_correction import get_error_correction_bytes, polynomial_remainder
from helpers import int_to_bitarray
from sequence import (
    combine_message,
    get_byte_data,
    get_encoding_mode,
    get_length_bits_count,
    get_payload_bits,
    get_version,
)

"""
https://dev.to/maxart2501/let-s-develop-a-qr-code-generator-part-iii-error-correction-1kbm
"""


def get_size_from_version(version: int):
    """Get the side length of the qr code from its version number"""
    return version * 4 + 17


def get_new_matrix(version: int) -> list[list[int]]:
    """Return an empty matrix with the correct size for the give version"""
    size = get_size_from_version(version)
    return [[0 for _ in range(size)] for _ in range(size)]


def fill_area(matrix: list[list[int]], row: int, column: int, width: int, height: int, fill=1):
    """Fill a rectangle in a matrix with the given value"""
    for row_idx in range(row, row + height):
        row = matrix[row_idx]
        for column_idx in range(column, column + width):
            matrix[row_idx][column_idx] = fill


def get_module_sequence(version: int) -> list[list[int, int]]:

    matrix = get_new_matrix(version)
    size = get_size_from_version(version)

    # Finder patterns + divisors
    fill_area(matrix, 0, 0, 9, 9)
    fill_area(matrix, 0, size - 8, 8, 9)
    fill_area(matrix, size - 8, 0, 9, 8)

    # Alignment pattern - yes, we just place one. For the general
    # implementation, wait for the next parts in the series!
    fill_area(matrix, size - 9, size - 9, 5, 5)
    # Timing patterns
    fill_area(matrix, 6, 9, version * 4, 1)
    fill_area(matrix, 9, 6, 1, version * 4)
    # Dark module
    matrix[size - 8][8] = 1

    # This part is copy and pasted from the tutorial, only the syntax is changed
    row_step = -1
    row = size - 1
    column = size - 1
    sequence = []
    index = 0
    while column >= 0:
        if matrix[row][column] == 0:
            sequence.append([row, column])

        # Checking the parity of the index of the current module
        if index & 1:
            row += row_step
            if row == -1 or row == size:
                row_step = -row_step
                row += row_step
                column -= 2 if column == 7 else 1
            else:
                column += 1

        else:
            column -= 1
        index += 1

    # display_qr_code(matrix, sequence)
    return sequence


def get_raw_qr_matrix(payload: str) -> list[list[int]]:
    VERSION = 2
    TOTAL_CODEWORDS = 44
    DATA_CODEWORDS = 28

    encoding_mode = get_encoding_mode(payload)
    length_bits_count = get_length_bits_count(encoding_mode, VERSION)

    data_codewords = get_byte_data(payload, DATA_CODEWORDS)
    error_codewords = get_error_correction_bytes(data_codewords, TOTAL_CODEWORDS)
    # print(data_codewords)
    codewords = data_codewords + error_codewords

    size = get_size_from_version(VERSION)
    qr_matrix = get_new_matrix(VERSION)
    sequence = get_module_sequence(VERSION)

    # Place fixed patterns
    # Finder patterns
    for row, col in [[0, 0], [size - 7, 0], [0, size - 7]]:
        fill_area(qr_matrix, row, col, 7, 7)
        fill_area(qr_matrix, row + 1, col + 1, 5, 5, 0)
        fill_area(qr_matrix, row + 2, col + 2, 3, 3)

    # Separators
    fill_area(qr_matrix, 7, 0, 8, 1, 0)
    fill_area(qr_matrix, 0, 7, 1, 7, 0)
    fill_area(qr_matrix, size - 8, 0, 8, 1, 0)
    fill_area(qr_matrix, 0, size - 8, 1, 7, 0)
    fill_area(qr_matrix, 7, size - 8, 8, 1, 0)
    fill_area(qr_matrix, size - 7, 7, 1, 7, 0)

    # Alignment pattern
    fill_area(qr_matrix, size - 9, size - 9, 5, 5)
    fill_area(qr_matrix, size - 8, size - 8, 3, 3, 0)
    qr_matrix[size - 7][size - 7] = 1

    # Timing patterns
    # Something fishy going on here, with an off by one error seemingly not present in the tutorial code
    for pos in range(8, VERSION * 4 + 8 + 1, 2):
        qr_matrix[6][pos] = 1
        qr_matrix[6][pos + 1] = 0
        qr_matrix[pos][6] = 1
        qr_matrix[pos + 1][6] = 0

    qr_matrix[6][size - 7] = 1
    qr_matrix[size - 7][6] = 1
    # Dark module
    qr_matrix[size - 8][8] = 1

    # Place the codewords according to the sequence
    codeword_bits = bitarray()
    codeword_bits.frombytes(bytes(codewords))
    for i, (row, column) in enumerate(sequence):
        if i > len(codeword_bits) - 1:
            break
        qr_matrix[row][column] = codeword_bits[i]

    return qr_matrix


def place_fixed_patterns(matrix: list[list[int]]):
    size = len(matrix)

    # Place fixed patterns
    # Finder patterns
    for row, col in [[0, 0], [size - 7, 0], [0, size - 7]]:
        fill_area(matrix, row, col, 7, 7)
        fill_area(matrix, row + 1, col + 1, 5, 5, 0)
        fill_area(matrix, row + 2, col + 2, 3, 3)

    # Separators
    fill_area(matrix, 7, 0, 8, 1, 0)
    fill_area(matrix, 0, 7, 1, 7, 0)
    fill_area(matrix, size - 8, 0, 8, 1, 0)
    fill_area(matrix, 0, size - 8, 1, 7, 0)
    fill_area(matrix, 7, size - 8, 8, 1, 0)
    fill_area(matrix, size - 7, 7, 1, 7, 0)

    # Alignment pattern
    fill_area(matrix, size - 9, size - 9, 5, 5)
    fill_area(matrix, size - 8, size - 8, 3, 3, 0)
    matrix[size - 7][size - 7] = 1

    # Timing patterns
    # Something fishy going on here, with an off by one error seemingly not present in the tutorial code
    # for pos in range(8, VERSION * 4 + 8 + 1, 2):
    for pos in range(8, size - 9, 2):
        matrix[6][pos] = 1
        matrix[6][pos + 1] = 0
        matrix[pos][6] = 1
        matrix[pos + 1][6] = 0

    matrix[6][size - 7] = 1
    matrix[size - 7][6] = 1
    # Dark module
    matrix[size - 8][8] = 1


# The functions to generate each of the 7 different masks
MASK_FNS = [
    lambda row, column: ((row + column) & 1) == 0,
    lambda row, column: (row & 1) == 0,
    lambda row, column: column % 3 == 0,
    lambda row, column: (row + column) % 3 == 0,
    lambda row, column: (((row >> 1) + math.floor(column / 3)) & 1) == 0,
    lambda row, column: ((row * column) & 1) + ((row * column) % 3) == 0,
    lambda row, column: ((((row * column) & 1) + ((row * column) % 3)) & 1) == 0,
    lambda row, column: ((((row + column) & 1) + ((row * column) % 3)) & 1) == 0,
]


def get_masked_matrix(version: int, codewords: list[int], mask_index: int) -> list[list[int]]:
    """Place the bits of the given codewords into the correctly sized matrix, in the correct pattern"""
    sequence = get_module_sequence(version)
    qr_matrix = get_new_matrix(version)
    mask_function = MASK_FNS[mask_index]

    # Place the codewords according to the sequence
    codeword_bits = bitarray()
    codeword_bits.frombytes(bytes(codewords))
    for i, (row, column) in enumerate(sequence):
        if i > len(codeword_bits) - 1:
            break
        qr_matrix[row][column] = codeword_bits[i] ^ mask_function(row, column)
    return qr_matrix


ERROR_ORDER = "MLHQ"
FORMAT_DIVISOR = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]
FORMAT_MASK = [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]


def get_format_bits(error_level: str, mask_index: int) -> bitarray:
    """Get the bits making up the reserved format sections of the qr code."""
    format_poly = bitarray("0" * 15)
    error_level_index = ERROR_ORDER.index(error_level)

    # Create polynomial (this seems arbitrary but idk)
    format_poly[0] = error_level_index >> 1
    format_poly[1] = error_level_index & 1
    format_poly[2] = mask_index >> 2
    format_poly[3] = (mask_index >> 1) & 1
    format_poly[4] = mask_index & 1

    # Do some more weird polynomial division
    remainder = polynomial_remainder(format_poly, FORMAT_DIVISOR)
    format_poly = remainder + bitarray("0" * (15 - len(remainder)))

    # Apply format mask
    format_poly = format_poly ^ bitarray(FORMAT_MASK)
    return format_poly


def set_sublist(list_a: list, sub_list: list, index: int):
    """Helper function to replace part of a list with a sub list at the given index"""
    for sub_i, i in enumerate(range(index, index + len(sub_list))):
        list_a[i] = sub_list[sub_i]


def place_format_bits(matrix: list[list[int]], error_level: str, mask_index: int):
    """Place the format bits in the provided matrix"""
    format_poly = get_format_bits(error_level, mask_index)

    # Rows
    set_sublist(matrix[8], format_poly[0:6], 1)
    set_sublist(matrix[8], format_poly[6:8], 7)
    set_sublist(matrix[8], format_poly[7:], len(matrix) - 8)

    # Single corner piece left in part cut off by timing sections
    matrix[7][8] = format_poly[8]

    # Columns
    for i, value in enumerate(format_poly[:7]):
        matrix[len(matrix) - i - 1][8] = value

    for i, value in enumerate(format_poly[9:]):
        matrix[5 - i][8] = value


def get_qr_matrix_from_data(version: int, codewords: list[int], error_level: str, mask_index: int):
    matrix = get_masked_matrix(version, codewords, mask_index)
    place_format_bits(matrix, error_level, mask_index)
    place_fixed_patterns(matrix)
    return matrix


def create_qr_code(payload: str) -> list[list[int]]:
    VERSION = 2
    TOTAL_CODEWORDS = 44
    DATA_CODEWORDS = 28
    ERROR_LEVEL = "M"
    MASK_INDEX = 0

    data_codewords = get_byte_data(payload, DATA_CODEWORDS)
    error_codewords = get_error_correction_bytes(data_codewords, TOTAL_CODEWORDS)
    codewords = data_codewords + error_codewords

    qr_code = get_qr_matrix_from_data(VERSION, codewords, ERROR_LEVEL, MASK_INDEX)
    return qr_code


def main():
    # get_module_sequence(2)
    # print(polynomial_mul([1, 3, 2], [2, 1, 7]))
    # print(polynomial_remainder([4, 4, 7, 5], [2, 1]))
    # generator = get_generator_polynomial(16)

    TEMP_TOTAL_CODEWORDS = 28
    # PAYLOAD = "https://www.qrcode.com/"
    PAYLOAD = "https://www.sundial.co.uk/"

    qr_code = create_qr_code(PAYLOAD)
    display_qr_code(qr_code)
    # get_format_bits("H", 3)
    # qr_code = get_raw_qr_matrix(PAYLOAD)
    # place_format_bits(qr_code, "H", 3)
    return

    encoding_mode = get_encoding_mode(PAYLOAD)
    version = get_version(PAYLOAD)

    length_bits_count = get_length_bits_count(encoding_mode, version=version)
    length_bits = int_to_bitarray(len(PAYLOAD), length_bits_count)
    payload_bits = get_payload_bits(PAYLOAD, encoding_mode)

    message = combine_message(encoding_mode, length_bits, payload_bits, TEMP_TOTAL_CODEWORDS)
    # print("Encoding:     ", encoding_mode)
    # print("Length:       ", length_bits)
    # print("Payload:      ", payload_bits)
    # print("Final Message:", message_bits)
    # print("Final Message:", message_bits.to01(8))

    error_correction_data = get_error_correction_bytes(message, 44)
    print(get_error_correction_bytes(message, 44))

    # print(len(message_bits) % 8)

    # print(encoding_mode)


if __name__ == "__main__":
    main()
