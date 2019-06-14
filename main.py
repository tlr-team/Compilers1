# from tkinter import DISABLED, END, NORMAL, Button, E, Entry, Label, StringVar, Tk, W
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from mainwindow import Ui_MainWindow
import core


class GramarUI(Ui_MainWindow):
    def __init__(self, root):
        Ui_MainWindow.__init__(root)
        self.root = root
        self.setupUi(root)
        self.grammar = None
        self.associate_actions()
    
    def associate_actions(self):

        # self.actionAnalyse
        self.buttonAskBelongs.clicked.connect(self.analyse)#FIXME: changed
        pass
    
    @pyqtSlot()
    def ask_belongs(self):
        print("ask_belongs")
        pass

    def show_svg(self, svg_img: str, widget: QtWidgets.QWidget=None):
        svg_bytes = bytearray(svg_img, encoding='utf-8')
        svgWidget = QSvgWidget(widget if widget else self.tabAutomaton)
        svgWidget.renderer().load(svg_bytes)
        width = int(svg_img.split("width=\"", 1)[1].split("\"", 1)[0])
        height = int(svg_img.split("height=\"", 1)[1].split("\"", 1)[0])
        width = min(widget.width(), width) 
        height = min(widget.height(), height) 
        svgWidget.setGeometry(0, 0, width, height)
        svgWidget.show()

    
    def load_grammar(self, file_name: str):
        self.current_filename = file_name
        with open(file_name, 'r') as file:
            self.grammar = core.Grammar.from_json(file.read())
            self.textEditGrammar.setPlainText(self.grammar.plain_productions)

    @pyqtSlot()
    def load_grammar_get(self):
        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', filter="grm(*.grm)")
        if name[0]:
            return
        self.load_grammar(name[0])

    def save_grammar(self, file_name: str=None):
        if not file_name is None:
            self.current_filename = file_name
        if self.current_filename is None:
            from random import randint
            self.current_filename = __file__[:-3] + "_0.grm"

        with open(file_name, 'w') as file:
            file.write(self.grammar.to_json)

    def new_grammar(self):
        self.grammar = None
        self.current_filename = None
        # clear results and grammar

    @pyqtSlot()
    def analyse(self):#TODO: how to bind correctly
        print(self.gridLayout, self.gridLayout_1,self.gridLayout_2,self.gridLayout_3,self.gridLayout_4,)
        raw_grammar = self.textEditGrammar.toPlainText()
        self.grammar = core.parse_to_grammar(raw_grammar.split("\n"))
        self.tabWidget.setCurrentIndex(1)
        # process
        res = "resultados"
        res += str(self.grammar)
        self.textResults.setPlainText(res)
        return 1

    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = GramarUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

