import csv
from os import error
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
from collections import defaultdict


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
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class Window(QtWidgets.QMainWindow):
    """ Main window class
        Splitted in 3
    """
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.setWindowTitle("My App")
        self.setGeometry(0, 0, 1280, 768)
        
        self.invert_x = False
        self.cols_qnt = None
        self.data = None
        self.cols_names = None
        self.x_y_names = None

        self.plot_curve = True
        self.plot_bar = False
        self.plot_scatter = False

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

        self.grid = QtWidgets.QGridLayout()
        self.grid.setColumnStretch(4, 4)
        self.horizontalGroupBox = QtWidgets.QGroupBox("Columns Available")

        for col in range(self.cols_qnt):
            # Get name of column each iteration and display with a check box
            self.col = QtWidgets.QCheckBox(self.x_y_names[col], parent=self.tableView)
            self.col.setGeometry(QtCore.QRect(5, 5, 5, 5))
           
            self.grid.addWidget(self.col)
            self.col.setCheckable(True)
        
            self.rbtn1 = QtWidgets.QRadioButton('Make it X axis')
            self.rbtn1.toggled.connect(self.swap_x)
            self.grid.addWidget(self.rbtn1)

        
        # Add the grid to layout with it's label
        self.horizontalGroupBox.setLayout(self.grid)
        self.layout2.addWidget(self.horizontalGroupBox)

        # Group for Update / Clean / Sort buttons
        self.layout_btn = QtWidgets.QHBoxLayout(self)

        # Group for kind of plot (bar, curve, etc)
        self.layout_btn2 = QtWidgets.QHBoxLayout(self)

        self.plot_curve = QtWidgets.QPushButton("Plot Curve")
        self.plot_curve.clicked.connect(self._plot_curve)
        self.layout_btn2.addWidget(self.plot_curve)

        self.plot_bar = QtWidgets.QPushButton("Plot Bar")
        self.plot_bar.clicked.connect(self._plot_bar)
        self.layout_btn2.addWidget(self.plot_bar)

        self.plot_scatter = QtWidgets.QPushButton("Plot Scatter")
        self.plot_scatter.clicked.connect(self._plot_scatter)
        self.layout_btn2.addWidget(self.plot_scatter)

        # Update / Clean / Sort buttons
        self.update_button = QtWidgets.QPushButton("Update Graph")
        self.update_button.clicked.connect(self._update)
        self.layout_btn.addWidget(self.update_button)

        self.clean_button = QtWidgets.QPushButton("Clean Graph")
        self.clean_button.clicked.connect(self._clean)
        self.layout_btn.addWidget(self.clean_button)

        self.invert_button = QtWidgets.QPushButton("Sort Data")
        self.invert_button.clicked.connect(self._sort_data)
        self.layout_btn.addWidget(self.invert_button)

        # Adding group buttons to layout
        self.layout2.addLayout(self.layout_btn)
        self.layout2.addLayout(self.layout_btn2)

    def _plot_curve(self):
        self.plot_curve = True
        self.plot_bar = False
        self.plot_scatter = False
        
        self._clean()
        self._update()

    def _plot_bar(self):
        self.plot_curve = False
        self.plot_bar = True
        self.plot_scatter = False
        self._clean()
        self._update()


    def _plot_scatter(self):
        self.plot_curve = False
        self.plot_bar = False
        self.plot_scatter = True


    def _sort_data(self):
        self.data.sort_index(axis=0, inplace=True)
        self._clean()
        self._update()

    # def _invert(self):
    #     """ Invert x and y
    #     """
    #     if self.invert_x:
    #         self.invert_x = False
    #     else:
    #         self.invert_x = True
    #     # print(self.invert_x)

    def _clean(self):
        self.canvas.axes.clear()
        self.canvas.draw()

    def _update(self):
        """ The update button in the interface
            Updates the graph with x/y selected
        """
        self._clean()
        self.checked_items = []
        
        # Getting the checkboxes
        for i in range(self.grid.count()):
            self.ch_box = self.grid.itemAt(i).widget()
            if self.ch_box.isChecked():
                self.checked_items.append(self.ch_box.text())

        self.display_graph()

    def load_csv(self):
        """Read the csv file from disk and display
        """
        self.file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')

        # Fail fast
        if self.file_name == ('', ''):
            return
        
        self.setWindowTitle(self.file_name[0])
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
 
    def _load_info(self):
        # Name of columns
        self.x_y_names = list(self.data.columns.values)
        # print("Column names",self.x_y_names)

        self.cols_qnt = (len(self.data.columns))

        self.data = pd.read_csv(self.file_name[0], names=self.x_y_names, header=0) 
        self.data = self.data.sample(n=60)
    
    def display_graph(self):

        # Showing error dialog if the user choose less than 2 columnns
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Warning)
        error_dialog.setText("Warning")
        error_dialog.setInformativeText("Select two columns at least!")
        error_dialog.setWindowTitle("Warning")

        error_not_x = QtWidgets.QMessageBox()
        error_not_x.setIcon(QtWidgets.QMessageBox.Warning)
        error_not_x.setText("Warning")
        error_not_x.setInformativeText("Select the X!")
        error_not_x.setWindowTitle("Warning")
        # x = 0 if self.invert_x else 1
        # y = 1 if self.invert_x else 0

        print("Checked items: ", self.checked_items)
        x_axis = None

        for i, j in enumerate(self.checked_items):
            if 'Make it X axis' in j:
                # print("X index", i)
                x_axis = i - 1

        # If user doesnt select a x axis
        if x_axis == None:
            error_not_x.exec_()
            return

        compare = defaultdict(list)

        # Getting indexes of selected columns
        for index, item in enumerate(self.x_y_names):
            compare[item].append(index)

        selected_axis = [index for item in self.checked_items for index in compare[item] if item in compare]

        # Inverting the list
        #selected_axis = selected_axis.reverse() if self.invert_x else selected_axis
        # if self.invert_x:
        #     selected_axis.reverse()
         
        if len(selected_axis) < 2:
            error_dialog.exec_()
            return

        # print("selected indexes",selected_axis)
        original_axis = self.checked_items
        original_axis.remove('Make it X axis')
        
        # Removing the X from the list to use it. 
        # Remaining will be Y
        selected_axis.pop(x_axis)
        canvas_labels = []
        
        for i in selected_axis:
            if self.plot_curve:
                self.canvas.axes.plot(self.data[original_axis[x_axis]], self.data[self.x_y_names[i]],label=self.x_y_names[i])
            if self.plot_bar:
                self.canvas.axes.bar(self.data[original_axis[x_axis]], self.data[self.x_y_names[i]],label=self.x_y_names[i])

            canvas_labels.append(self.x_y_names[i])
        
        #for i in canvas_labels:
        self.canvas.axes.set_ylabel(canvas_labels)
        self.canvas.axes.legend()
        self.canvas.axes.set_xlabel(original_axis[x_axis])
        self.canvas.axes.set_xticklabels(self.data[original_axis[x_axis]], fontsize=8, rotation=45,)
        self.canvas.axes.set_yticklabels(canvas_labels, fontsize=8)
        self.canvas.draw()
        self.canvas.flush_events()

    def swap_x(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            # print("Swap x")
            print()

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
        # print("Theme selected: ", self.cb.currentText())
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
    w = Window()
    w.show()
    sys.exit(app.exec_())

