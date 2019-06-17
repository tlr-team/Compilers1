# from tkinter import DISABLED, END, NORMAL, Button, E, Entry, Label, StringVar, Tk, W
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from mainwindow import Ui_MainWindow
import core


class GramarUI(Ui_MainWindow):
    def __init__(self, root):
        Ui_MainWindow.__init__(root)
        self.root = root
        self.setupUi(root)
        # vars
        self.grammar = None
        self.current_filename = None
        self.svg_img = None
        #
        self.associate_actions()

    def _dialog(self, s, icon):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(icon)
        dlg.show()

    def dialog_critical(self, s):
        self._dialog(s, QMessageBox.Critical)

    def dialog_warning(self, s):
        self._dialog(s, QMessageBox.Warning)

    def associate_actions(self):
        self.actionLoadGrammar.triggered.connect(self.load_grammar)
        self.actionNewGrammar.triggered.connect(self.new_grammar)
        self.actionSaveGrammar.triggered.connect(self.save_grammar)
        self.actionSaveGrammarAs.triggered.connect(self.save_grammar_as)
        self.actionAnalyse.triggered.connect(self.analyse)
        self.buttonAskBelongs.clicked.connect(self.ask_belongs)
        # self.actionExit.triggered.connect(None)

    def ask_belongs(self):
        self.label_belong_result.setText("Pertenece")  # porque si XD

    def show_svg(self, widget: QtWidgets.QWidget = None):
        svg_bytes = bytearray(self.svg_img, encoding="utf-8")
        svgWidget = QSvgWidget(widget if widget else self.tabAutomaton)
        svgWidget.renderer().load(svg_bytes)
        width = int(self.svg_img.split('width="', 1)[1].split('"', 1)[0])
        height = int(self.svg_img.split('height="', 1)[1].split('"', 1)[0])
        width = min(widget.width(), width)
        height = min(widget.height(), height)
        svgWidget.setGeometry(0, 0, width, height)
        svgWidget.show()

    def _load_grammar(self, file_name: str):
        self.current_filename = file_name
        with open(file_name, "r") as file:
            try:
                self.grammar = core.Grammar.from_json(file.read())
                self.textEditGrammar.setPlainText(self.grammar.plain_productions)
            except:
                self.dialog_warning("Ocurrió un error al cargar el archivo.")
        return

    def load_grammar(self):
        import os

        grm_path, _ = QFileDialog.getOpenFileName(
            self.root, "Cargar gramática...", "./", "gramáticas (*.grm)"
        )
        if not grm_path or not os.path.exists(grm_path):
            return
        print(grm_path)
        self._load_grammar(grm_path)

    def _save_grammar_at(self, file_name):
        print(file_name)
        if self.grammar is None:
            self.analyse()
        if not self.grammar is None:
            with open(file_name, "w") as file:
                file.write(self.grammar.to_json)
        return

    def save_grammar_as(self):
        if self.grammar is None and not self.textEditGrammar.toPlainText():
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self.root, "Salvar gramática...", "./", "gramáticas (*.grm)"
        )

        if not file_name:
            # If dialog is cancelled, will return ''
            return

        self.current_filename = file_name
        return self._save_grammar_at(self.current_filename)

    def save_grammar(self):
        if self.grammar is None and not self.textEditGrammar.toPlainText():
            return

        if self.current_filename is None:
            self.save_grammar_as()
        else:
            self._save_grammar_at(self.current_filename)

    def new_grammar(self):
        self.grammar = None
        self.svg_img = None
        self.current_filename = None
        # clear results and grammar
        self.textResults.setPlainText("")
        self.textEdit_input_belongs.setPlainText("")
        self.textEditGrammar.setPlainText("")
        self.label_belong_result.setText("")
        return

    def analyse(self):
        if not self.textEditGrammar.toPlainText():
            return
        raw_grammar = str(self.textEditGrammar.toPlainText())
        self.grammar = core.parse_to_grammar(raw_grammar.split("\n"))
        res = self.get_results()  # processing grammar stuff
        self.tabWidget.setCurrentIndex(2)
        self.textResults.setPlainText(res)
        if self.svg_img:
            self.show_svg()

    def get_results(self):
        res = "resultados:\n"
        res += str(self.grammar) if self.grammar else "Wrong Sintax..."
        # set or unset svg str
        # self.svg_img = ""
        return res


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = GramarUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
