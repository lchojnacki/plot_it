"""
Module containing additional external functions.
"""

import re


def binomial_of_newton(n, k):
    """
    Calculate the newtonian binomial for the given arguments.

    :param n: first argument
    :param k: second argument
    :return: result of the calculation

    :Example:

    >>> binomial_of_newton(5, 3)
    10.0

    """
    result = 1
    for i in range(1, k + 1):
        result = result * (n - i + 1) / i
    return result


def newton_nth_root(a, n):
    """
    Calculate nth root of number.
    :param a: a number
    :param n: the degree of the root
    :return: nth root of a number a

    :Example:

    >>> newton_nth_root(125, 3)
    5.0

    """
    x_k = a
    while True:
        x_1 = (1/n) * ((n-1)*x_k + (a / x_k ** (n-1)))
        if abs(a - x_k ** n) < 0.0000001:
            break
        else:
            x_k = x_1
    return x_1


def check_string(user_string):
    """
    Check if the string is properly constructed.

    :param user_string: user input string
    :type user_string: str
    :return: returns True or False after verifying that the string is constructed correctly.
    :rtype: bool

    :Example:

    >>> check_string("x^2+3x-1")
    True

    """

    """
    valid_chars = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                   'x', '^', '+', '-', '*', '|', '(', ')', '/', '.', ' ')
    is_valid = True
    for single_char in user_string:
        if single_char not in valid_chars:
            is_valid = False
    return is_valid
    """

    pattern = '^((\d*([.]|[,]|[\/])?\d+)?((?<=\d)e\+\d*|(?<=\d)e\-\d*)?((?<=\d)(\*(?=x)))?(x|x\^(?=\d))?\d*){1}' \
              '(( )?(\+|-)( )?' \
              '(\d*([.]|[,]|[\/])?\d+)?((?<=\d)e\+\d*|(?<=\d)e\-\d*)?((?<=\d)(\*(?=x)))?(x|x\^(?=\d))?\d*)*$'

    # ^ - start of the string
    # (\d*([.]|[,]|[\/])?\d+)?((?<=\d)e\+\d*|(?<=\d)e\-\d*)? - 0 or 1 float (0 or more digits, 0 or 1 occur of ',' or
    #                       '.' or '/', 1 or more digits and 0 or 1 'e+digit' or 'e-digit')
    # ((?<=\d)(\*(?=x)))? - 0 or 1 '*' if it's followed by 'x' and preceded by a digit
    # (x|x\^(?=\d))? - 0 or 1 'x' or 'x^', 'x^' only if it's followed by a digit
    # \d* - 0 or more digits
    # $ - end of the string

    try:
        assert isinstance(user_string, str)
        assert re.match(pattern, user_string)
        return True
    except AssertionError:
        return False


def dict_to_list(dictionary):
    """
    Convert the dictionary into a list.

    :param dictionary: dictionary with positive integer keys
    :type dictionary: dict
    :return: list of dictionary values
    :rtype: list
    """

    new_list = []
    max_key = 0
    for key in dictionary.keys():
        if key > max_key:
            max_key = key

    for i in range(max_key + 1):
        try:
            new_list.append(dictionary[i])
        except KeyError:
            new_list.append(0)

    return new_list
