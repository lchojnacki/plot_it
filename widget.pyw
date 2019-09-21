"""
Module containing main widget class.
"""

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel, QGridLayout
from PyQt4.QtGui import QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QScrollArea
from PyQt4.QtGui import QMessageBox, QInputDialog, QCheckBox
from PyQt4.QtCore import SIGNAL
from plotit.polynomial import Polynomial, string_to_polynomial
import plotit.functions as functions
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
import matplotlib.pyplot as plt
import numpy
import re


class NavigationToolbar(NavigationToolbar2QT):
    """
    Custom toolbar class used to customize matplotlib navigation toolbar.
    """

    def __init__(self, canvas_, parent_):
        self.toolitems = (
            ('Home', 'Przywróć widok początkowy', 'home', 'home'),
            ('Back', 'Wróć do poprzedniego widoku', 'back', 'back'),
            ('Forward', 'Przejdź do kolejnego widoku', 'forward', 'forward'),
            ('Zoom', 'Przybliż fragment wykresu', 'zoom_to_rect', 'zoom'),
            ('Save', 'Zapisz wykres', 'filesave', 'save_figure'),
        )
        NavigationToolbar2QT.__init__(self, canvas_, parent_)

    def zoom(self):
        """
        Override NavigationToolbar2QT method to translate text.
        """
        NavigationToolbar2QT.zoom(self)
        self.mode = "wybierz prostokąt"
        self.set_message(self.mode)

    def _update_buttons_checked(self):
        """
        Override NavigationToolbar2QT method to prevent KeyError.
        """
        self._actions['zoom'].setChecked(self._active == 'ZOOM')


class TransformGraphsWidget(QWidget):
    def __init__(self):
        """
        Creates default polynomial, empty list for transformations history and initiates the interface.
        """
        super().__init__()
        self.history = []
        self.input_polynomial_box = QLineEdit()
        self.scroll_area = QScrollArea()
        self._x_lim = []
        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111)
        self.points = []
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self._interface()

    def _interface(self):
        """
        Build interface of the widget with input, buttons and checkboxes on the left and graph on the right.
        """

        # labels

        main_label = QLabel('Podaj wzór wielomianu w formacie ax^n + bx^n-1 + ... + cx + d: ')
        input_label = QLabel('P(x) = ')

        # buttons

        reflection_x_button = QPushButton('Symetria OX\nP(x) = -P(x)', self)
        QPushButton.connect(reflection_x_button, SIGNAL('clicked()'), self._do_a_reflection_about_x)
        reflection_y_button = QPushButton('Symetria OY\nP(x) = P(-x)', self)
        QPushButton.connect(reflection_y_button, SIGNAL('clicked()'), self._do_a_reflection_about_y)
        translation_button = QPushButton('&Przesunięcie o wektor\nP(x) = P(x-p)+q', self)
        QPushButton.connect(translation_button, SIGNAL('clicked()'), self._do_a_translation)
        derivative_button = QPushButton('&Różniczkowanie\nP(x) = P(x) = P\'(x)', self)
        QPushButton.connect(derivative_button, SIGNAL('clicked()'), self._calculate_derivative)
        multiply_y_by_k_button = QPushButton('P&owinowactwo OX\nP(x) = k*P(x)', self)
        QPushButton.connect(multiply_y_by_k_button, SIGNAL('clicked()'), self._do_multiplication_by_k)
        multiply_x_by_k_button = QPushButton('Po&winowactwo OY\nP(x) = P(k*x)', self)
        QPushButton.connect(multiply_x_by_k_button, SIGNAL('clicked()'), self._do_multiplication_x_by_k)
        draw_button = QPushButton('Rysuj [Enter]', self)
        QPushButton.connect(draw_button, SIGNAL('clicked()'), self.input_and_draw)
        refresh_button = QPushButton('Wyczyść wykres', self)
        QPushButton.connect(refresh_button, SIGNAL('clicked()'), self._refresh_graph)

        # add widgets to left grid

        main_grid = QHBoxLayout()
        left_grid = QGridLayout()
        left_grid.addWidget(main_label, 0, 0)

        input_box = QHBoxLayout()
        input_box.addWidget(input_label)
        input_box.addWidget(self.input_polynomial_box)
        left_grid.addLayout(input_box, 1, 0, 1, 3)

        left_grid.addWidget(QLabel('Lista wielomianów:'), 2, 0)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_widget = QWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_area_widget)

        self.scroll_layout = QVBoxLayout(self.scroll_area_widget)

        left_grid.addWidget(self.scroll_area, 3, 0)

        buttons_first_line = QHBoxLayout()
        buttons_first_line.addWidget(reflection_x_button)
        buttons_first_line.addWidget(reflection_y_button)
        left_grid.addLayout(buttons_first_line, 4, 0, 1, 3)

        buttons_second_line = QHBoxLayout()
        buttons_second_line.addWidget(translation_button)
        buttons_second_line.addWidget(derivative_button)
        left_grid.addLayout(buttons_second_line, 5, 0, 1, 3)

        buttons_third_line = QHBoxLayout()
        buttons_third_line.addWidget(multiply_y_by_k_button)
        buttons_third_line.addWidget(multiply_x_by_k_button)
        left_grid.addLayout(buttons_third_line, 6, 0, 1, 3)

        draw_buttons_layout = QHBoxLayout()
        draw_buttons_layout.addWidget(draw_button)
        draw_buttons_layout.addWidget(refresh_button)
        left_grid.addLayout(draw_buttons_layout, 7, 0, 1, 3)

        main_grid.addLayout(left_grid)

        # add widgets to right grid

        self.ax.grid(True)
        self.ax.axhline(linewidth=0.5, color='black')
        self.ax.axvline(linewidth=0.5, color='black')

        right_grid = QGridLayout()
        right_grid.addWidget(self.canvas)
        right_grid.addWidget(self.toolbar)
        main_grid.addLayout(right_grid)

        # assign grid layout to window

        self.setLayout(main_grid)
        self.show()

    def _add_checkbox(self, text):
        """
        Add new checkbox.

        :param text: text to new checkbox
        """
        cb = QCheckBox('P(x) = ' + text)
        cb.setChecked(True)
        QCheckBox.connect(cb, SIGNAL('clicked()'), self._checkbox_state_changed)
        self.scroll_layout.addWidget(cb)

    def _checkbox_state_changed(self):
        """
        Get signal from checkbox and remove polynomial from plot if checkbox is unchecked, otherwise add it.
        """

        my_text = self.sender().text()[7:]
        is_checked = self.sender().isChecked()
        if is_checked:
            self._draw(string_to_polynomial(my_text))
        else:
            i = -2
            for item in self.ax.lines:
                if item.get_label() == my_text:
                    self.points[i].remove()
                    del(self.points[i])
                    break
                i += 1
            self.ax.lines.remove(item)
            if len(self.ax.lines) > 2:
                self.ax.legend(loc='upper left')
            else:
                self.ax.legend_ = None
            if len(self.ax.lines) < 3:
                self._clear_ax()
            self.canvas.draw()

    def _input_polynomial(self):
        """
        Get the string from the user, verify, and create a polynomial object.
        """

        message = str(self.input_polynomial_box.text())
        if message == '':
            pass
        elif functions.check_string(message):
            self.tmp_polynomial = string_to_polynomial(message)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowIcon(QIcon('img/rybka.ico'))
            msg.setText("Niepoprawny zapis funkcji.")
            msg.setInformativeText("Użyj formatu: ax^n+bx^n-1+...+cx+d")
            msg.setWindowTitle("Błąd!")
            msg.exec_()
            try:
                del(self.tmp_polynomial)
            except AttributeError:
                pass

    def _do_a_reflection_about_x(self):
        """
        Execute reflection_about_x polynomial method.
        Add operation to the transformations history.
        """

        self._input_polynomial()
        tmp1 = str(self.tmp_polynomial)
        self.tmp_polynomial = self.tmp_polynomial.reflection_about_x()
        tmp2 = str(self.tmp_polynomial)
        self.input_polynomial_box.setText(str(self.tmp_polynomial).replace(' ', ''))
        self.history.append((tmp1, 'Symetria OX', tmp2))

    def _do_a_reflection_about_y(self):
        """
        Execute reflection_about_y polynomial method.
        Add operation to the transformations history.
        """

        self._input_polynomial()
        tmp1 = str(self.tmp_polynomial)
        self.tmp_polynomial = self.tmp_polynomial.reflection_about_y()
        tmp2 = str(self.tmp_polynomial)
        self.input_polynomial_box.setText(str(self.tmp_polynomial).replace(' ', ''))
        self.history.append((tmp1, 'Symetria OY', tmp2))

    def _do_a_translation(self):
        """
        Get p and q parameters from the user and execute translation polynomial method.
        Add operation to the transformations history.
        """

        self._input_polynomial()
        tmp1 = str(self.tmp_polynomial)
        p, first_step = QInputDialog.getText(self, 'Przesunięcie o wektor', 'Podaj p:')
        pattern = '^-?\d*([.]|[,]|[/])?\d+$'
        try:
            if first_step:
                if re.match(pattern, p):
                    q, second_step = QInputDialog.getText(self, 'Przesunięcie o wektor', 'Podaj q:')
                    if second_step:
                        if re.match(pattern, q):
                            p = p.replace(',', '.')
                            q = q.replace(',', '.')
                            self.tmp_polynomial = self.tmp_polynomial.translation(float(eval(p)), (float(eval(q))))
                            tmp2 = str(self.tmp_polynomial)
                            self.input_polynomial_box.setText(str(self.tmp_polynomial).replace(' ', ''))
                            self.history.append((tmp1, 'Translacja: p=' + p + ', q=' + q, tmp2))
                    else:
                        raise ValueError
                else:
                    raise ValueError
        except ValueError:
            self._param_error()
            self._do_a_translation()

    def _calculate_derivative(self):
        """
        Execute differentiate polynomial method.
        Add operation to the transformations history.
        """

        self._input_polynomial()
        tmp1 = str(self.tmp_polynomial)
        self.tmp_polynomial.differentiate()
        tmp2 = str(self.tmp_polynomial)
        self.input_polynomial_box.setText(str(self.tmp_polynomial).replace(' ', ''))
        self.history.append((tmp1, 'Różniczkowanie', tmp2))

    def _do_multiplication_by_k(self):
        """
        Get the parameter k from the user and execute multiply_function_by_k polynomial method.
        Add operation to the transformations history.
        """

        self._input_polynomial()
        tmp1 = str(self.tmp_polynomial)
        k, check = QInputDialog.getText(self, 'Powinowactwo OX', 'Podaj k:')
        if check:
            pattern = '^-?\d*([.]|[,]|[/])?\d+$'
            if re.match(pattern, k):
                k = k.replace(',', '.')
                self.tmp_polynomial = self.tmp_polynomial.multiply_function_by_k(float(eval(k)))
                tmp2 = str(self.tmp_polynomial)
                self.input_polynomial_box.setText(str(self.tmp_polynomial).replace(' ', ''))
                self.history.append((tmp1, 'Powinowactwo OX: k=' + k, tmp2))
            else:
                self._param_error()
                self._do_multiplication_by_k()

    def _do_multiplication_x_by_k(self):
        """
        Get the parameter k from the user and execute multiply_x_by_k polynomial method.
        Add operation to the transformations history.
        """

        self._input_polynomial()
        tmp1 = str(self.tmp_polynomial)
        k, check = QInputDialog.getText(self, 'Powinowactwo OY', 'Podaj k:')
        if check:
            pattern = '^-?\d*([.]|[,]|[/])?\d+$'
            if re.match(pattern, k):
                k = k.replace(',', '.')
                self.tmp_polynomial = self.tmp_polynomial.multiply_x_by_k(float(eval(k)))
                tmp2 = str(self.tmp_polynomial)
                self.input_polynomial_box.setText(str(self.tmp_polynomial).replace(' ', ''))
                self.history.append((tmp1, 'Powinowactwo OY: k=' + k, tmp2))
            else:
                self._param_error()
                self._do_multiplication_x_by_k()

    @staticmethod
    def _param_error():
        """
        Show an error dialog box.
        """

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowIcon(QIcon('img/rybka.ico'))
        msg.setText("Wprowadź poprawną liczbę.")
        msg.setWindowTitle("Wystąpił błąd!")
        msg.exec_()

    @staticmethod
    def test_dialog(message):
        """
        Show an error dialog box.
        """

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowIcon(QIcon('img/rybka.ico'))
        msg.setText(message)
        msg.setWindowTitle("Test!")
        msg.exec_()

    def input_and_draw(self):
        """
        Take a polynomial from the user, draw it, and add new checkbox.
        """

        
        self._input_polynomial()
        try:
            self._add_checkbox(str(self.tmp_polynomial))
            self._draw(self.tmp_polynomial)
        except AttributeError:
            pass

    def _draw(self, polynomial):
        """
        Draw polynomial within the range found by the find_range function in the main widget.

        :param polynomial: polynomial to draw
        """

        x_range = polynomial.find_range_newton()
        points_x = polynomial.find_points()
        points_x.extend(polynomial.newton_roots())
        points_y = []
        for x in points_x:
            points_y.append(polynomial(x))
        x_range_changed = False
        if self._x_lim:
            if x_range[0] < self._x_lim[0]:
                self._x_lim[0] = x_range[0]
                x_range_changed = True
            if x_range[1] > self._x_lim[1]:
                self._x_lim[1] = x_range[1]
                x_range_changed = True
        else:
            self._x_lim.append(x_range[0])
            self._x_lim.append(x_range[1])

        x_values = numpy.linspace(self._x_lim[0], self._x_lim[1], 10000)
        if x_range_changed:
            for i in range(2, len(self.ax.lines)):
                y = []
                tmp_poly = string_to_polynomial(self.ax.lines[i].get_label())
                for x in x_values:
                    y.append(tmp_poly(x))
                self.ax.lines[i].set_data(x_values, y)
        y = []
        for x in x_values:
            y.append(polynomial(x))
        self.ax.plot(x_values, y, label=str(polynomial))
        self.points.append(self.ax.scatter(points_x, points_y, s=20))
        self.ax.legend(loc='upper left')
        self.ax.set_xlim(x_values[0], x_values[-1])
        self.canvas.draw()

    def _clear_ax(self):
        self.ax.clear()
        self.ax.set_xlim(0, 1)
        self._x_lim = []
        self._y_lim = []
        self.ax.grid(True)
        self.ax.axhline(linewidth=0.5, color='black')
        self.ax.axvline(linewidth=0.5, color='black')

    def _refresh_graph(self):
        """
        Clear graph in the main widget and remove all the checkboxes.
        """

        self._clear_ax()
        self.points = []
        self.canvas.draw()
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)
        self.input_polynomial_box.setText('')
        
