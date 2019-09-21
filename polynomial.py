"""
Module containing the polynomial class with transformation methods.
"""

import numpy
import matplotlib.pyplot as plt
from plotit.functions import binomial_of_newton, dict_to_list, newton_nth_root


class Polynomial(object):
    def __init__(self, coefficients):
        self.coeff = coefficients

    def __call__(self, x):
        """
        Evaluate the polynomial using Horner's scheme.
        :param x: point
        :type x: float
        :rtype: float
        """
        value = self.horner(x)
        return value[-1]

    def __add__(self, other):
        """
        Return self + other as Polynomial object.
        :param other: Polynomial object
        :type other: Polynomial
        :rtype: Polynomial
        """
        # Two cases:
        #
        # self:   X X X X X X X
        # other:  X X X
        #
        # or:
        #
        # self:   X X X X X
        # other:  X X X X X X X X

        # Start with the longest list and add in the other
        if len(self.coeff) > len(other.coeff):
            result_coeff = self.coeff[:]  # copy!
            for i in range(len(other.coeff)):
                result_coeff[i] += other.coeff[i]
        else:
            result_coeff = other.coeff[:]  # copy!
            for i in range(len(self.coeff)):
                result_coeff[i] += self.coeff[i]
        return Polynomial(result_coeff)

    def __mul__(self, other):
        """
        Return self * other as Polynomial object.
        :param other: Polynomial object
        :type other: Polynomial
        :rtype: Polynomial
        """
        c = self.coeff
        d = other.coeff
        m = len(c) - 1
        n = len(d) - 1
        result_coeff = numpy.zeros(m + n + 1)
        for i in range(0, m + 1):
            for j in range(0, n + 1):
                result_coeff[i + j] += c[i] * d[j]
        return Polynomial(result_coeff)

    def differentiate(self):
        """
        Differentiate this polynomial in-place.
        """
        for i in range(1, len(self.coeff)):
            self.coeff[i - 1] = i * self.coeff[i]
        del self.coeff[-1]
        if len(self.coeff) == 0:
            self.coeff.append(0)

    def derivative(self):
        """
        Copy this polynomial and return its derivative.
        :rtype: Polynomial
        """
        dpdx = Polynomial(self.coeff[:])  # make a copy
        dpdx.differentiate()
        return dpdx

    def reflection_about_x(self):
        """
        Copy this polynomial and returns polynomial reflected about x-axis.
        f(x) = -f(x)
        :rtype: Polynomial
        """

        p = Polynomial(self.coeff[:])
        for (index, value) in enumerate(p.coeff):
            p.coeff[index] = -1 * value

        return p

    def reflection_about_y(self):
        """
        Copy this polynomial and returns polynomial reflected about x-axis.
        f(x) = f(-x)
        :rtype: Polynomial
        """

        p = Polynomial(self.coeff[:])
        for (index, value) in enumerate(p.coeff):
            if index % 2 != 0:
                p.coeff[index] = -1 * value

        return p

    def translation(self, p, q):
        """
        f(x) = f(x-p)+q
        :param p: p value of vector
        :param q: q value of vector
        :type p: int
        :type q: int
        :rtype: Polynomial
        """

        poly = Polynomial(self.coeff[:])
        coeff_dict = dict()
        for (index, value) in enumerate(poly.coeff):
            if index != 0:
                tmp_dict = dict()
                for k in range(index + 1):
                    ck = index - k
                    cv = (-1) ** k * binomial_of_newton(index, k) * p ** k
                    try:
                        tmp_dict[ck] += cv
                    except KeyError:
                        tmp_dict[ck] = cv
                for ck in tmp_dict:
                    tmp_dict[ck] *= value
                    try:
                        coeff_dict[ck] += tmp_dict[ck]
                    except KeyError:
                        coeff_dict[ck] = tmp_dict[ck]
        try:
            coeff_dict[0] += q + poly.coeff[0]
        except KeyError:
            coeff_dict[0] = q + poly.coeff[0]

        poly.coeff = dict_to_list(coeff_dict)

        return poly

    def multiply_function_by_k(self, k):
        """
        f(x) = k * f(x)
        :param k: value to multiply
        :type k: float
        :rtype: Polynomial
        """

        p = Polynomial(self.coeff[:])
        for (index, value) in enumerate(p.coeff):
            p.coeff[index] = k * value

        return p

    def multiply_x_by_k(self, k):
        """
        f(x) = f(k*x)
        :param k: value to multiply
        :type k: float
        :rtype: Polynomial
        """

        p = Polynomial(self.coeff[:])
        for (index, value) in enumerate(p.coeff):
            if index != 0:
                p.coeff[index] = k ** index * value

        return p

    def __str__(self):
        s = ''
        if len(self.coeff) == 1 and self.coeff[0] == 0:
            s += ' + %g*x^%d' % (self.coeff[0], 0)
        for i in reversed(range(0, len(self.coeff))):
            if self.coeff[i] != 0:
                s += ' + %g*x^%d' % (self.coeff[i], i)

        # Fix layout
        s = s.replace('+ -', '- ')
        s = s.replace('*x^0', '')
        s = s.replace(' 1*', ' ')
        s = s.replace('x^1 ', 'x ')
        # s = s.replace('x^1', 'x') # will replace x^100 by x^00
        if s[0:3] == ' + ':  # remove initial +
            s = s[3:]
        if s[0:3] == ' - ':  # fix spaces for initial -
            s = '-' + s[3:]
        return s

    def simple_str(self):
        s = ''
        if len(self.coeff) == 1 and self.coeff[0] == 0:
            s += ' + %g*x^%d' % (self.coeff[0], 0)
        for i in reversed(range(0, len(self.coeff))):
            s += ' + %g*x^%d' % (self.coeff[i], i)
        return s

    def find_range_radius(self):
        """
        Find range with all the roots using the theorem of the circle containing the roots of a polynomial.
        :return: tuple containing the start and end of the interesting range of the polynomial
        """
        if len(self.coeff) > 1:
            an = abs(self.coeff[-1])
            max_ak = 0
            for i in range(len(self.coeff) - 1):
                if abs(self.coeff[i]) > max_ak:
                    max_ak = abs(self.coeff[i])
            r = 1 + (1 / an) * max_ak

            return -r, r
        else:
            return -5, 5

    def lagrange_r(self):
        """
        Calculate Lagrange's R.
        :return: upper bound of the positive roots of the polynomial
        """

        coeff = self.coeff[:]

        if coeff[-1] < 0:
            for i in range(len(coeff)):
                coeff[i] *= (-1)
        for i in range(len(coeff) - 1):
            a_n = coeff[len(coeff) - 1 - i]
            if a_n != 0:
                break
        b = 0
        k = 0
        for i in range(len(coeff) - 1):
            if coeff[i] < b:
                b = coeff[i]
            if coeff[i] < 0:
                k = len(coeff) - 1 - i
        if k > 0:
            max_positive = 1 + newton_nth_root(abs(b) / a_n, k)
            return max_positive

    def find_range_lagrange(self):
        """
        Find range with all the roots using Lagrange's theorem
        :return: tuple containing the start and end of the interesting range of the polynomial
        """

        poly_range = []

        if len(self.coeff) > 1:
            positive_roots = False
            negative_roots = False
            for i in range(len(self.coeff)):
                if self.coeff[i] < 0:
                    positive_roots = True
                    break

            if positive_roots:
                max_positive = self.lagrange_r()
                p_reversed = Polynomial(list(reversed(self.coeff)))
                min_positive = p_reversed.lagrange_r()
                if max_positive:
                    poly_range.append(max_positive)
                if min_positive:
                    poly_range.append(1 / min_positive)

            temp = self.reflection_about_y()
            for i in range(len(temp.coeff)):
                if temp.coeff[i] < 0:
                    negative_roots = True
                    break

            if negative_roots:
                min_negative = temp.lagrange_r()
                temp_reversed = Polynomial(list(reversed(temp.coeff)))
                max_negative = temp_reversed.lagrange_r()
                if min_negative:
                    poly_range.append((-1) * min_negative)
                if max_negative:
                    poly_range.append((-1) / max_negative)

            poly_range.sort()

            return poly_range[0], poly_range[-1]

        else:
            return (-5, 5), []

    def horner(self, x):
        """
        Calculate b coefficients of Horner's method
        :param x: point
        :return: list of coefficients
        """
        n = len(self.coeff) - 1
        b = (n + 1) * [0]
        b[n - 1] = self.coeff[n]
        for k in range(n - 1, -1, -1):
            b[k - 1] = self.coeff[k] + x * b[k]
        return b

    def deflation(self, a):
        """
        Horner's table deflation: W(x) / (x-a)
        :param a: subtrahend of (x-a)
        :return: tuple with result polynomial and the rest of the division
        """
        t = self.horner(a)
        return Polynomial(t[:-1])

    def newton_roots(self, accuracy_zero=10**-4):
        """
        Find real roots of the polynomial
        :return: list of real roots
        """

        p1 = Polynomial(self.coeff[:])

        def newton(poly, start, accuracy=10 ** -16, max_steps=10):

            der = poly.derivative()
            x1 = start
            for k in range(max_steps):
                if poly(x1) == 0:
                    break
                try:
                    x0 = x1
                    x1 = x0 - poly(x0) / der(x0)
                except ZeroDivisionError:
                    x0 = x1 - 10**-8
                    x1 = x0 - poly(x0) / der(x0)
                if abs(x0 - x1) < accuracy:
                    break
            return x1

        roots = []
        temp = 0
        max_roots = len(p1.coeff)
        root = self.lagrange_r() if self.lagrange_r() else 0
        while len(p1.coeff) > 1 and temp <= max_roots:
            temp += 1
            root = newton(p1, start=root, max_steps=max_roots ** 2)
            while abs(p1(root)) < accuracy_zero:
                root = round(root, 12)
                roots.append(root)
                p1 = p1.deflation(root)
        roots.sort()
        return roots

    def find_range_newton(self):
        """
        Find an interesting part of the polynomial (containing all the real roots, extremes
        and inflection points)

        :return: tuple containing the start and end of the interesting range of the polynomial
        """

        if len(self.coeff) > 1:
            points_x = self.newton_roots()
        else:
            return -5, 5

        points_x.extend(self.find_points())

        points_x.sort()

        if len(points_x) > 0:
            min_x = points_x[0]
            max_x = points_x[-1]
        else:
            min_x = -5
            max_x = 5

        difference_x = max_x - min_x
        margin_x = 0.1 * difference_x
        if margin_x < 1:
            margin_x = 2

        return min_x - margin_x, max_x + margin_x

    def find_points(self):
        """
        Find the roots, maxima, minima and inflection points of a polynomial.
        :return: sorted list of maxima, minima and inflection points
        """
        if len(self.coeff) > 1:

            points_x = []
            d_roots = []
            d2_roots = []

            try:
                d = self.derivative()
                d_prev = self.derivative()
                d_roots.extend(d.newton_roots())
            except ValueError:
                pass

            try:
                d2_roots.extend(d.derivative().newton_roots())
            except ValueError:
                pass
            except IndexError:
                pass

            n = 1
            while d.coeff != [0]:
                for x0 in d_roots:
                    if d(x0) != 0 and abs(d_prev(x0)) < 10**-4 and n > 1 and n % 2 == 0:
                        points_x.append(x0)
                for x0 in d2_roots:
                    if d(x0) != 0 and abs(d_prev(x0)) < 10**-4 and n > 2 and n % 2 != 0:
                        points_x.append(x0)
                d_prev = Polynomial(d.coeff[:])
                d.differentiate()
                n += 1

            points_x.sort()

            return points_x

        else:
            return []

    def draw(self):
        """
        Draw polynomial within the range found by the find_range function in new window.
        """

        x_range = self.find_range_newton()
        x_range = numpy.linspace(x_range[0], x_range[1], 10000)
        y = []
        for x in x_range:
            y.append(self(x))
        points_x = self.find_points()
        points_x.extend(self.newton_roots())
        points_y = []
        for x in points_x:
            points_y.append(self(x))
        plt.plot(x_range, y, label=str(self))
        plt.scatter(points_x, points_y, s=20)
        plt.title("P(x)=" + str(self))
        # plt.legend(loc='upper left')
        plt.grid(True)
        plt.axhline(linewidth=0.5, color='black')
        plt.axvline(linewidth=0.5, color='black')
        if max(y) == min(y):  # f(x) = const
            plt.ylim(min(y) - 5, max(y) + 5)
        plt.xlim(x_range[0], x_range[-1])
        plt.show()


def string_to_polynomial(user_string):
    """
    Parse string to polynomial object.

    :param user_string: string that user inputs in program window
    :return: Polynomial object converted from user_string
    :type user_string: str
    :rtype: Polynomial

    :Example:

    >>> string_to_polynomial('5x^7')
    <__main__.Polynomial object at 0x039D1E90>

    """

    if user_string == '':
        return

    user_string = user_string.replace('-', '+-')
    if user_string[0] == '+':
        user_string = user_string[1:]

    user_string = user_string.replace('*x', 'x')
    user_string = user_string.replace('e+', '*10**')
    user_string = user_string.replace(' ', '')
    user_string = user_string.replace(',', '.')

    coeff_string_list = user_string.split('+')
    coeff_dict = dict()
    for coeff_string in coeff_string_list:
        if 'x' in coeff_string:
            if '^' in coeff_string:
                coeff = coeff_string.split('x^')
                if coeff[0] == '':
                    coeff[0] = '1'
                if coeff[0] == '-':
                    coeff[0] = '-1'
            else:
                coeff = coeff_string.split('x')
                if coeff[0] == '':
                    coeff[0] = '1'
                if coeff[0] == '-':
                    coeff[0] = '-1'
                coeff[1] = '1'
            assert (len(coeff) == 2)
            dict_key = int(coeff[1])
            try:
                dict_value = eval(coeff[0])
            except SyntaxError:
                coeff[0] = coeff[0].replace('*10**', 'e+')
                dict_value = eval(coeff[0])
            try:
                coeff_dict[dict_key] += dict_value
            except KeyError:
                coeff_dict[dict_key] = dict_value
        else:
            try:
                coeff_dict[0] += eval(coeff_string)
            except KeyError:
                coeff_dict[0] = eval(coeff_string)

    coeff_list = dict_to_list(coeff_dict)

    polynomial = Polynomial(coeff_list)

    return polynomial


def test_polynomial():
    p1 = Polynomial([1, -1])
    p2 = Polynomial([0, 1, 0, 0, -6, -1])
    p3 = p1 + p2
    p3_exact = Polynomial([1, 0, 0, 0, -6, -1])
    msg = 'p1 = %s, p2 = %s\np3=p1+p2 = %s\nbut wrong p3 = %s' % \
          (p1, p2, p3_exact, p3)
    assert p3.coeff == p3_exact.coeff, msg
    # Note __add__ applies lists only, here with integers, so
    # == for comparing lists is not subject to round-off errors

    p4 = p1 * p2
    # p4.coeff becomes a numpy array, see __mul__
    p4_exact = Polynomial(numpy.array([0, 1, -1, 0, -6, 5, 1]))
    msg = 'p1 = %s, p2 = %s\np4=p1*p2 = %s\ngot wrong p4 = %s' % \
          (p1, p2, p4_exact, p4)
    assert numpy.allclose(p4.coeff, p4_exact.coeff, rtol=1E-14), msg

    p5 = p2.derivative()
    p5_exact = Polynomial([1, 0, 0, -24, -5])
    msg = 'p2 = %s\np5 = p2.derivative() = %s\ngot wrong p5 = %s' % \
          (p2, p5_exact, p5)
    assert p5.coeff == p5_exact.coeff, msg

    p6 = Polynomial([0, 1, 0, 0, -6, -1])  # p2
    p6.differentiate()
    p6_exact = p5_exact
    msg = 'p6 = %s\p6.differentiate() = %s\ngot wrong p6 = %s' % \
          (p2, p6_exact, p6)
    assert p6.coeff == p6_exact.coeff, msg


if __name__ == '__main__':
    test_polynomial()
