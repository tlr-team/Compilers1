import gc

from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, pyqtSlot
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

import parse_input
import parsers
import regex

from grammar import Grammar
from UI import Ui_MainWindow


class GramarUI(Ui_MainWindow):
    def __init__(self, root):
        Ui_MainWindow.__init__(root)
        self.root = root
        self.setupUi(root)
        # vars
        self.grammar = None
        self.current_filename = None
        #
        self.associate_actions()

    def associate_actions(self):
        self.actionLoadGrammar.triggered.connect(self.load_grammar)
        self.actionNewGrammar.triggered.connect(self.new_grammar)
        self.actionSaveGrammar.triggered.connect(self.save_grammar)
        self.actionSaveGrammarAs.triggered.connect(self.save_grammar_as)
        self.actionAnalyse.triggered.connect(self.analyse)
        self.buttonAskBelongs.clicked.connect(self.ask_belongs)
        # self.actionExit.triggered.connect(None)

    def _load_grammar(self, file_name: str):
        self.current_filename = file_name
        with open(file_name, "r") as file:
            try:
                self.grammar = Grammar.from_json(file.read())
                self.textEditGrammar.setPlainText(self.grammar.plain_productions)
                if self.tabs_automatons:
                    self._close_all_automatons()

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
        # print(grm_path)
        self._load_grammar(grm_path)

    def _save_grammar_at(self, file_name):
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
        self.current_filename = None
        # clear results and grammar
        self.textResults.setPlainText("")
        self.textEdit_input_belongs.setPlainText("")
        self.textEditGrammar.setPlainText("")
        self.label_belong_result.setText("")

        self.tabWidget.setCurrentIndex(0)
        self._close_all_automatons()
        return

    def analyse(self):
        if not self.textEditGrammar.toPlainText():
            return
        if self.tabs_automatons:
            self._close_all_automatons()

        raw_grammar = str(self.textEditGrammar.toPlainText())
        self.grammar = parse_input.parse_to_grammar(raw_grammar.split("\n"))
        res = self.get_results()
        self.tabWidget.setCurrentIndex(2)
        self.textResults.setPlainText(res)

        for parser_name, svg_str in self.svg_imgs:
            assert isinstance(svg_str, str), parser_name
            self.create_svg_slot(parser_name, svg_str)

    ############## Word Belongs ##############
    def ask_belongs(self):
        word = self.textEdit_input_belongs.toPlainText().strip("\n \t").split(' ')
        if self.grammar:
            word.append(self.grammar.EOF.Name if self.grammar else "$")
        res_belongs = self.get_belongs_info(word)
        self.label_belong_result.setText(res_belongs)

    def get_belongs_info(self, word):
        if not self.grammar:
            return "Gramática no entrada o sin analizar..."
        res = "RESULTADOS:\n"

        for meth_name in GramarUI.__dict__:
            if meth_name.endswith("_belongs_results") and callable(getattr(GramarUI, meth_name)):
                valid, _info = GramarUI.__dict__[meth_name](self, word)
                res += str(_info) + "\n" if valid else ""  # TODO: fix format correctly
        return res

    def _regex_belongs_results(self, word):
        try:
            self.regex  # TODO: Pending to implementation
            assert not self.regex.parse_corrupted
        except:
            return False, None
        return True, self.regex(word)  # TODO: Pending to implementation

    def _ll1_belongs_results(self, word):
        try:
            self.ll1
            assert not self.ll1.parse_corrupted
        except:
            return False, None
        return True, self.ll1(word)

    def _lr_belongs_results(self, word):
        try:
            self.lr
            assert not self.lr.parse_corrupted
        except:
            return False, None
        return True, self.lr(word)

    def _lalr_belongs_results(self, word):
        try:
            self.lalr
            assert not self.lalr.parse_corrupted
        except:
            return False, None
        return True, self.lalr(word)

    def _slr_belongs_results(self, word):
        try:
            self.slr
            assert not self.slr.parse_corrupted
        except:
            return False, None
        return True, self.slr(word)

    ############## End Word Belongs ##############

    ############## Parser Results ##############
    def get_results(self):
        if not self.grammar:
            return "Sintáxis de gramática incorrecta..."
        res = "RESULTADOS:\n"

        res += str(self.grammar) + "\n"

        # reducciones de gramaticas, firsts and follows
        res += self._get_metainfo()

        self.svg_imgs = []

        # info and automatons for every parser method who match
        for meth_name in GramarUI.__dict__:
            if meth_name.endswith("_parser_results") and callable(getattr(GramarUI, meth_name)):
                _info, _aut = GramarUI.__dict__[meth_name](self)
                name = meth_name.split("_parser_results")[0].strip("_")
                res += "\n" + (20 * "-") + name + (20 * "-") + "\n"
                res += _info
                if _aut:
                    self.svg_imgs.append((name, _aut))
        return res

    def _get_metainfo(self):
        firsts = parsers.compute_firsts(self.grammar)
        follows = parsers.compute_follows(self.grammar, firsts)
        print(firsts, follows)
        res = (
            "firsts: \n\t" + "\n\t".join(str(w) + " > " + str(f) for w, f in firsts.items()) + "\n"
        )
        res += (
            "follows: \n\t"
            + "\n\t".join(str(w) + " > " + str(f) for w, f in follows.items())
            + "\n"
        )
        # TODO: add the reductions left rec, unit prod, lambda prod,etc
        return res

    def _regex_parser_results(self):  # ??? is the same as ll1
        is_reg = parse_input.is_regular_grammar(self.grammar)
        res = (
            "Es Regular:\n" if is_reg else "No es Regular.\n"
        )
        if is_reg:
            nfa = regex.convert_to_nfa(self.grammar)
            self.regex = regex.regex_from_nfa(nfa)
            res += str(self.regex) + "\n"
            return res, nfa._repr_svg_()
        return res, None

    def _ll1_parser_results(self):
        self.ll1 = parsers.LL1(self.grammar)
        return str(self.ll1), None  # has no graph

    def _lr_parser_results(self):
        self.lr = parsers.LR1(self.grammar)
        return str(self.lr), None if self.lr.parse_corrupted else self.lr.automaton._repr_svg_()

    def _lalr_parser_results(self):
        self.lalr = parsers.LALR(self.grammar)
        return str(self.lalr), None # if self.lalr.parse_corrupted else self.lalr.automaton._repr_svg_()
        return "", None

    def _slr_parser_results(self):
        self.slr = parsers.SLR(self.grammar)
        return str(self.slr), None if self.slr.parse_corrupted else self.slr.automaton._repr_svg_()

    ############## End Parser Results ##############


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = GramarUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
