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


class Window(QtWidgets.QMainWindow):
    """ Main window class
        Splitted in 3
    """
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.setWindowTitle("My App")
        self.setGeometry(0, 0, 1280, 768)
        self.setWindowTitle("Some app")
        self.canvas = MplCanvas(self, width=9, height=5, dpi=100)
        
        self.cols_qnt = None
        self.data = None
        self.cols_names = None
        self.x_y_names = None

        layout1 = QtWidgets.QHBoxLayout()
        self.layout2 = QtWidgets.QVBoxLayout()
        #layout3 = QtWidgets.QHBoxLayout()
        
        # layout with the graph
        self.layout2.addWidget(self.canvas)

        # Layout with graph options
        mlp_toolbar = NavigationToolbar( self.canvas, self)
        self.layout2.addWidget(mlp_toolbar)#Color('gray'))  

        self.model = QtGui.QStandardItemModel(self)

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        layout1.addLayout(self.layout2)

        # layout with data (the table)
        layout1.addWidget(self.tableView)
        
        #self.layout2.addWidget(self.checkBox_d)
        #layout3.addWidget(self.tableView2)
        
        widget = QtWidgets.QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)
        
        self.menu_bar()

    def check_buttons(self):
        label = QtWidgets.QLabel(self)
        label.setText("Columns Available")
        self.layout2.addWidget(label)
        for j in range(self.cols_qnt):
            # Get name of column each iteration and display with a check box
            self.j = QtWidgets.QCheckBox(self.x_y_names[j], parent=self.tableView)
            self.j.setGeometry(QtCore.QRect(5, 5, 50, 50))
            self.layout2.addWidget(self.j)
            self.j.setCheckable(True)

        self.update_button = QtWidgets.QPushButton("Update Graph")
        self.update_button.clicked.connect(self._update)
        self.layout2.addWidget(self.update_button)
    
    def _update(self):
    
        print("Click'n")
        self.checked_items = []
        for i in range(4, self.layout2.count()):
            ch_box = self.layout2.itemAt(i).widget()
            #print(i)
            #print(self.j.checkState())
            # if self.j.checkState() == QtCore.Qt.Checked:
            if ch_box.isChecked():

                print("check", ch_box.text())
                #self.j.setChecked(True)
                self.checked_items.append(i)

        print("TEst", ch_box.text())

        
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
        self.display_graph()

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
        #cols = [self.cols_names[i] for i in range(self.cols_qnt)]
        #a_list = [self.data[str(i)] for i in cols]
        #print(a_list)
        self.canvas.stop_event_loop()
        #self.canvas = MplCanvas(self, width=9, height=5, dpi=100)
        # Getting the column names to display in the graph (need to make it iterable)
        self.canvas.axes.plot(self.data[self.x_y_names[0]], self.data[self.x_y_names[1]])
        self.canvas.axes.set_xlabel(self.x_y_names[0])
        self.canvas.axes.set_xticklabels(self.data[self.x_y_names[0]], rotation=90,)
        self.canvas.axes.set_ylabel(self.x_y_names[1])
        
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

