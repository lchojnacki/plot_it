"""
Module containing main window class.
"""

import sys
from PyQt4.QtGui import QAction, qApp
from PyQt4.QtGui import QApplication, QMainWindow, QMessageBox
from PyQt4.QtGui import QDialog, QTableView, QStandardItemModel, QStandardItem
from PyQt4.QtGui import QIcon, QStatusBar
from PyQt4.QtGui import QShortcut, QKeySequence
from PyQt4.QtCore import Qt, SIGNAL, QObject
import plotit.widget as widget


class TransformGraphsWindow(QMainWindow):
    def __init__(self):
        """
        Create main widget of the window and connect keyboard shortcuts.
        """
        super().__init__()
        self._init_ui()
        self.main_widget = widget.TransformGraphsWidget()
        self.setCentralWidget(self.main_widget)
        self.connect(QShortcut(QKeySequence(Qt.Key_Enter), self), SIGNAL('activated()'), self._show_graph)
        self.connect(QShortcut(QKeySequence(Qt.Key_Return), self), SIGNAL('activated()'), self._show_graph)

    def _init_ui(self):
        """
        Initiate the main window with menu.
        """

        # main menu

        view_history = QAction(QIcon('img/tasks.png'), '&Historia', self)
        view_history.setShortcut('Ctrl+H')
        view_history.setStatusTip('Zobacz historię wykonywanych przekształceń')
        QObject.connect(view_history, SIGNAL('triggered()'), self._show_history)

        view_about = QAction(QIcon('img/letter-i.png'), '&O programie', self)
        view_about.setShortcut('Ctrl+I')
        view_about.setStatusTip('O programie')
        QObject.connect(view_about, SIGNAL('triggered()'), self._show_about)

        exit_program = QAction(QIcon('img/power-button.png'), '&Wyjdź', self)
        exit_program.setShortcut('Ctrl+Q')
        exit_program.setStatusTip('Zamknij aplikację')
        QObject.connect(exit_program, SIGNAL('triggered()'), qApp.quit)

        menu_bar = self.menuBar()
        menu = menu_bar.addMenu('&Menu')
        menu.addAction(view_history)
        menu.addAction(view_about)
        menu.addAction(exit_program)

        # end of menu

        self.setGeometry(80, 100, 1200, 550)
        self.setWindowIcon(QIcon('img/sketch.png'))
        self.setWindowTitle('Plot it!')
        status_bar = QStatusBar()
        status_bar.showMessage('Copyright © 2017 Łukasz Chojnacki')
        self.setStatusBar(status_bar)
        self.show()

    def _show_history(self):
        """
        Show the history of transformations in a dialog.
        """

        history = QDialog()
        history.setWindowTitle('Historia przekształceń')

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Funkcja pierwotna', 'Wykonana operacja', 'Funkcja wynikowa'])

        for operation in self.main_widget.history:
            row = []
            for element in operation:
                item = QStandardItem(element)
                item.setEditable(False)
                row.append(item)
            model.appendRow(row)

        table_view = QTableView(history)
        table_view.setModel(model)
        table_view.resizeColumnsToContents()

        if table_view.verticalHeader().length() + 24 < 500:
            view_height = table_view.verticalHeader().length() + 26
        else:
            view_height = 500
        table_view.resize(table_view.horizontalHeader().length() + 42, view_height)

        table_view.show()

        history.setWindowIcon(QIcon('img/tasks.png'))
        if table_view.verticalHeader().length() + 26 < 500:
            window_height = table_view.verticalHeader().length() + 26
        else:
            window_height = 500
        if table_view.verticalHeader().length() + 26 < 500:
            window_width = table_view.horizontalHeader().length() + 16
        else:
            window_width = table_view.horizontalHeader().length() + 52
        history.resize(window_width, window_height)
        history.exec()

    def _show_graph(self):
        """
        Show graph in main widget.
        """
        self.main_widget.input_and_draw()

    def _show_about(self):
        QMessageBox.about(self, "O programie", "Plot It!\n\nPodaj wzór wielomianu, dokonaj potrzebnych przekształceń "
                                               "i zinterpretuj wynik swojej pracy!\n\n"
                                               "Wprowadzając wzór wielomianu, zachowaj format:\nax^n + bx^n-1 + "
                                               "... + cx + d\nUżywaj tylko potęg całkowitych. Współczynniki rzeczywiste"
                                               " mogą mieć postać ułamków (np. 1/2) albo liczb zmiennoprzecinkowych (0.5 "
                                               "lub 0,5)\n\nCopyright © 2017 Łukasz Chojnacki\nIcons made by Freepik "
                                               "from www.flaticon.com are licensed by CC 3.0 BY")


def main():
    app = QApplication(sys.argv)
    window = TransformGraphsWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
