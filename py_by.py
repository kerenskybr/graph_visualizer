import csv
import sys

import matplotlib
import matplotlib.style
import numpy as np
import pandas as pd
import qtawesome as qta
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
matplotlib.style.use('bmh')
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import subprocess

class Color(QtWidgets.QWidget):
    # Coloring class
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(color))
        self.setPalette(palette)


class MplCanvas(FigureCanvas):
    # matplotlib canvas stuff
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.subplots_adjust(bottom=0.2)
        fig.set_tight_layout(True)
        #fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

    def __del__(self):
        print("Graph deleted")


class Window(QtWidgets.QMainWindow):
    """ Main window class
        Splitted in 3
    """
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.setWindowTitle("My App")
        self.setGeometry(0, 0, 1280, 768)
        self.setWindowTitle("Some app")
       
        self.invert_x = False
        self.cols_qnt = None
        self.data = None
        self.cols_names = None
        self.x_y_names = None

        self.layout1 = QtWidgets.QHBoxLayout()
        self.layout2 = QtWidgets.QVBoxLayout()
        #layout3 = QtWidgets.QHBoxLayout()
        
        self.graph_layout()

        self.model = QtGui.QStandardItemModel(self)

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.layout1.addLayout(self.layout2)

        # layout with data (the table)
        self.layout1.addWidget(self.tableView)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout1)
        self.setCentralWidget(widget)
        
        self.menu_bar()

        # Calling here cause the graph need to exist before change theme
        self.theme_options()

    def graph_layout(self):
        # layout with the graph
        self.canvas = MplCanvas(self, width=9, height=5, dpi=100)
        self.layout2.addWidget(self.canvas)

        # Layout with graph options
        self.mlp_toolbar = NavigationToolbar(self.canvas, self)
        self.layout2.addWidget(self.mlp_toolbar)#Color('gray')) 

    def check_buttons(self):
        # label = QtWidgets.QLabel(self)
        # label.setText("Columns Available")
        # self.layout2.addWidget(label)

        #self.process_wavelet = QtWidgets.QPushButton("Process")

        self.grid = QtWidgets.QGridLayout()
        self.grid.setColumnStretch(4, 4)
        self.horizontalGroupBox = QtWidgets.QGroupBox("Columns Available")

        for col in range(self.cols_qnt):
            # Get name of column each iteration and display with a check box
            self.col = QtWidgets.QCheckBox(self.x_y_names[col], parent=self.tableView)
            self.col.setGeometry(QtCore.QRect(5, 5, 10, 10))
            #self.layout2.addWidget(self.col)
            self.grid.addWidget(self.col)
            self.col.setCheckable(True)
            #self.layout2.addWidget(self.process_wavelet, j)

        self.horizontalGroupBox.setLayout(self.grid)
        # Add the grid to layout
        self.layout2.addWidget(self.horizontalGroupBox)

        self.update_button = QtWidgets.QPushButton("Update Graph")
        self.update_button.clicked.connect(self._update)
        self.layout2.addWidget(self.update_button)

        self.clean_button = QtWidgets.QPushButton("Clean Graph")
        self.clean_button.clicked.connect(self._clean)
        self.layout2.addWidget(self.clean_button)

        self.invert_button = QtWidgets.QPushButton("Invert X/Y")
        self.invert_button.clicked.connect(self._invert)
        self.layout2.addWidget(self.invert_button)

    def _invert(self):
        """ Invert x and y
        """
        if self.invert_x:
            self.invert_x = False
        else:
            self.invert_x = True
        print(self.invert_x)

    def _clean(self):
        self.canvas.axes.clear()
        self.canvas.draw()

    def _update(self):
        """ The update button in the interface
            Updates the graph with x/y selected
        """
        self.checked_items = []
        # starting at 3, skipping previous widgets.
        # Checkbox widget starts from 3
        for i in range(self.grid.count()):
            self.ch_box = self.grid.itemAt(i).widget()
            if self.ch_box.isChecked():
                print("check", self.ch_box.text())
                self.checked_items.append(self.ch_box.text())

        self.display_graph()

    # def _update(self):
    #     """ The update button in the interface
    #         Updates the graph with x/y selected
    #     """
    #     self.checked_items = []
    #     # starting at 3, skipping previous widgets.
    #     # Checkbox widget starts from 3
    #     for i in range(3, self.layout2.count()):
    #         self.ch_box = self.layout2.itemAt(i).widget()
    #         if self.ch_box.isChecked():
    #             print("check", self.ch_box.text())
    #             self.checked_items.append(self.ch_box.text())

    #     self.display_graph()

    def load_csv(self):
        """Read the csv file from disk and display
        """
        self.file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')

        # Fail fast
        if self.file_name == ('', ''):
            return
        
        self.data = pd.read_csv(self.file_name[0]) 

        self._load_info()
        
        with open(self.file_name[0], "r") as file:
            for row in csv.reader(file):
                items = [
                    QtGui.QStandardItem(field)
                    for field in row
                    ]
                self.model.appendRow(items)

        self.check_buttons()
        #self.display_graph()

    # def restart(self):
    #     self.close()
    #     subprocess.call("python" + "py_by.py  ", shell=True)

    def _load_info(self):
        # Name of columns
        self.x_y_names = list(self.data.columns.values)
        print(self.x_y_names)

        self.cols_qnt = (len(self.data.columns))
        # #self.data = pd.read_csv(self.file_name[0], names=['col1', 'col2'], header=0)
        self.cols_names = ['col'.join(str(i)) for i in range(self.cols_qnt)]
        #print(self.cols_names)
        print(">>> ", self.cols_names)

        self.data = pd.read_csv(self.file_name[0], names=self.x_y_names, header=0) 
        self.data = self.data.sample(n=50)
    
    def display_graph(self):
        
        x = 0 if self.invert_x else 1
        y = 1 if self.invert_x else 0

        self.canvas.axes.plot(self.data[self.checked_items[x]], self.data[self.checked_items[y]])
        
        self.canvas.axes.set_xlabel(self.checked_items[x])
        self.canvas.axes.set_xticklabels(self.data[self.checked_items[x]], rotation=90,)
        self.canvas.axes.set_ylabel(self.checked_items[y])
        
        self.canvas.draw()
        self.canvas.flush_events()

    def _save_as_png(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        
        # Fail fast
        if file_name == ('', ''):
            return

        img = np.array(self.canvas.buffer_rgba())
        img = Image.fromarray(img)
        img.save(file_name[0] + '.png')

    def theme_options(self):
        """Show a combo box with theme options
        """
        self.cb = QtWidgets.QComboBox()
        self.cb.addItems(matplotlib.style.available)
        self.toolBar.addWidget(self.cb)
        self.cb.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):            
        print("Theme selected: ", self.cb.currentText())
        matplotlib.style.use(self.cb.currentText())
        self.canvas.draw()
        self.canvas.flush_events()

    def menu_bar(self):
        # Menu bar items
        exit_action = QtWidgets.QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit app")
        exit_action.triggered.connect(self.close_aplication)

        load_csv_file = QtWidgets.QAction("Open", self)
        load_csv_file.setShortcut("Ctrl+O")
        load_csv_file.setStatusTip("Open csv file from disk")
        load_csv_file.triggered.connect(self.load_csv)

        main_menu = self.menuBar()

        # File menu
        file_menu = main_menu.addMenu("&File")
        file_menu.addAction(exit_action)
        file_menu.addAction(load_csv_file)

        # Icons bellow menu bar
        exit_icon = qta.icon("fa5s.sign-out-alt")
        quit_action = QtWidgets.QAction(QtGui.QIcon(exit_icon), "Exit App", self)
        quit_action.triggered.connect(self.close_aplication)

        open_icon = qta.icon("fa5s.folder-open")
        open_action = QtWidgets.QAction(QtGui.QIcon(open_icon), "Open csv file", self)
        open_action.triggered.connect(self.load_csv)

        save_icon = qta.icon("fa5s.file-image")
        save_action = QtWidgets.QAction(QtGui.QIcon(save_icon), "Save graph to disk", self)
        save_action.triggered.connect(self._save_as_png)

        self.toolBar = self.addToolBar("Main Toolbar")
        self.toolBar.addAction(open_action)
        self.toolBar.addAction(save_action)
        self.toolBar.addAction(quit_action)
        
    def close_aplication(self):
        choice = QtWidgets.QMessageBox.question(self, 
            "Exit Aplication?", 
            "Are You Sure?", 
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #gui = Window()
    # Temporary
    #gui.show()
    w = Window()
    w.show()
    sys.exit(app.exec_())

