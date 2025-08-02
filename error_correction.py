# Generate lookup tables for performing maths on the Galois Field GF(256). Don't ask me what that means.

LOG = [0] * 256
EXP = [0] * 256
value = 1
for exponent in range(1, 256):
    value = (value << 1) ^ 285 if value > 127 else value << 1
    LOG[value] = exponent % 255
    EXP[exponent % 255] = value


# Galois arithmetic. Weirdness.
def galois_add(a: int, b: int) -> int:
    return a ^ b


# This is the same as add in GF. Weirdness.
def galois_sub(a: int, b: int) -> int:
    return a ^ b


def galois_mul(a: int, b: int) -> int:
    if a and b:
        return EXP[(LOG[a] + LOG[b]) % 255]
    return 0


def galois_div(a: int, b: int) -> int:
    ret = EXP[(LOG[a] + LOG[b] * 254) % 255]
    return ret


def polynomial_mul(poly_1: list[int], poly_2: list[int]) -> list[int]:
    """Get the product of two polynomials, using galois arithmetic"""
    # preallocate final coefficients list
    coefficients = [0] * (len(poly_1) + len(poly_2) - 1)

    for index in range(len(coefficients)):
        coeff = 0
        for p1index in range(index + 1):
            p2index = index - p1index

            # BE CAREFUL. The guide says something about potential out of range errors in other languages, but I don't really know what it means.
            poly_1_value = poly_1[p1index] if p1index <= len(poly_1) - 1 else 0
            poly_2_value = poly_2[p2index] if p2index <= len(poly_2) - 1 else 0
            coeff = galois_add(coeff, galois_mul(poly_1_value, poly_2_value))
        coefficients[index] = coeff

    return coefficients


def polynomial_remainder(dividend: list[int], divisor: list[int]) -> list[int]:
    """Get the remainder of the division of two polynomials, using galois arithmetic"""
    quotient_length = len(dividend) - len(divisor) + 1
    print(quotient_length)

    remainder = dividend.copy()

    # I have no idea if this is correct
    for _ in range(quotient_length):
        # If the first term is 0, we can just skip this iteration
        if remainder[0]:
            factor = galois_div(remainder[0], divisor[0])
            subtr = polynomial_mul(divisor, [factor])
            subtr += [0] * (len(remainder) - len(subtr))  # add padding zeros

            for index, value in enumerate(remainder):
                remainder[index] = galois_sub(value, subtr[index])
            remainder = remainder[1:]
        else:
            remainder = remainder[1:]

    return remainder


def get_generator_polynomial(degree: int) -> list[int]:
    """Get the generator polynomial that is used as the divisor."""
    last_polynomial = [1]
    for i in range(degree):
        last_polynomial = polynomial_mul(last_polynomial, [1, EXP[i]])
    return last_polynomial


def get_error_correction_bytes(data_codewords: list[int], total_codewords: int) -> list[int]:
    degree = total_codewords - len(data_codewords)
    message_polynomial = data_codewords.copy()
    message_polynomial += [0] * (total_codewords - len(message_polynomial))
    return polynomial_remainder(message_polynomial, get_generator_polynomial(degree))
