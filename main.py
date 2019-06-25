import gc

from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, pyqtSlot
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

import parse_input
import parsers
import regex

from copy import deepcopy
from grammar import Grammar, Symbol, Terminal, NonTerminal
from tools import DerivationTree
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

    def _load_grammar(self, file_name: str):
        self.current_filename = file_name
        with open(file_name, "r") as file:
            try:
                if file_name.endswith(".grm"):
                    self.grammar = Grammar.from_json(file.read())
                    self.textEditGrammar.setPlainText(self.grammar.plain_productions)
                else:
                    self.textEditGrammar.setPlainText(file.read())
                    
                if self.tabs_automatons:
                    self._close_all_automatons()

            except:
                self.dialog_warning("Ocurrió un error al cargar el archivo.")
        return

    def load_grammar(self):
        import os

        grm_path, _ = QFileDialog.getOpenFileName(
            self.root, "Cargar gramática...", "./", "gramáticas (*.grm *.txt )"
        )
        if not grm_path or not os.path.exists(grm_path):
            return
        # print(grm_path)
        self._load_grammar(grm_path)

    def _save_grammar_at(self, file_name):
        if self.grammar is None:
            if not self.textEditGrammar.toPlainText():
                return
            raw_grammar = str(self.textEditGrammar.toPlainText())
            self.grammar = parse_input.parse_to_grammar(raw_grammar.split("\n"))
        if self.grammar:
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
        word = self.textEdit_input_belongs.toPlainText().strip("\n \t").split(" ")
        _word = "" if not self.grammar else self.grammar.tokenize(word)
        res_belongs, derivation = self.get_belongs_info(_word)
        self.label_belong_result.setText(res_belongs)
        if derivation:
            derivation = derivation._repr_svg_()
            if derivation:
                self.create_svg_slot(f"Derivación({','.join(word)})", derivation)

    def get_belongs_info(self, word):
        if not self.grammar:
            return "Gramática no entrada o sin analizar...", None
        res = "RESULTADOS:\n"
        parser, name, _type = (
            (None, None, None) if self.lalr.parse_corrupted else (self.lalr, "LALR", "Right")
        )
        parser, name, _type = (
            (parser, name, _type) if self.lr.parse_corrupted else (self.lr, "LR1", "Right")
        )
        parser, name, _type = (
            (parser, name, _type) if self.slr.parse_corrupted else (self.slr, "SLR1", "Right")
        )
        parser, name, _type = (
            (parser, name, _type) if self.ll1.parse_corrupted else (self.ll1, "LL1", "Left")
        )

        if not _type:
            return "Ninguno de los parsers esta disponible...", None
        recognized, derivation, verbosity = parser(word, True)
        derivation = DerivationTree.get_tree(derivation, _type) if derivation else None

        res += name + "\n"
        res += "La cadena fue reconocida.\n\n" if recognized else "La cadena no fue reconocida.\n"
        res += verbosity
        return res, derivation

    ############## End Word Belongs ##############

    ############## Parser Results ##############
    def get_results(self):
        if not self.grammar:
            return "Sintáxis de gramática incorrecta..."
        res = "RESULTADOS:\n\n"

        res += "GRAMÁTICA:\n" + str(self.grammar) + "\n\n"

        # reducciones de gramaticas, firsts and follows
        res += self._get_metainfo()

        self.svg_imgs = []

        # info and automatons for every parser method who match
        for meth_name in GramarUI.__dict__:
            if meth_name.endswith("_parser_results") and callable(getattr(GramarUI, meth_name)):
                _info, _aut = GramarUI.__dict__[meth_name](self)
                name = meth_name.split("_parser_results")[0].strip("_")
                res += "\n" + (25 * "=") + " " + name.upper() + " " + (25 * "=") + "\n"
                res += _info
                if _aut:
                    self.svg_imgs.append((name, _aut))

        # reductions for the grammar and evolution through them
        res += "\n" + (60 * "=") + "\n"
        res += (
            "\nReducciones de gramática:\n "
            + "(Recursividad Izquierda, Producciones lambda, Producciones Unitarias y Producciones Innecesarias)\n"
        )
        G = deepcopy(self.grammar)
        res += f"ORIGINAL:\n{str(G)}\n\n"
        
        parse_input.lambda_productions(G)
        res += f"Sin producciones lambda:\n{str(G)}\n\n"
        
        parse_input.unit_productions(G)
        res += f"Sin producciones unitarias:\n{str(G)}\n\n"
        
        parse_input.remove_left_rec(G)
        res += f"Sin producciones recursividad izquierda:\n{str(G)}\n\n"
        
        parse_input.useless_productions(G)
        res += f"Sin producciones innecesarias:\n{str(G)}\n"

        return res

    def _get_metainfo(self):
        firsts = parsers.compute_firsts(self.grammar)
        follows = parsers.compute_follows(self.grammar, firsts)

        res = (
            "FIRSTS: \n  No Terminales:\n\t"
            + "\n\t".join(
                str(w) + "    " + str(f) for w, f in firsts.items() if isinstance(w, NonTerminal)
            )
            + "\n  Terminales:\n\t"
            + "\n\t".join(
                str(w) + "    " + str(f) for w, f in firsts.items() if isinstance(w, Terminal)
            )
            + "\n  Alpha:\n\t"
            + "\n\t".join(
                str(w) + "    " + str(f) for w, f in firsts.items() if not isinstance(w, Symbol)
            )
            + "\n"
        )

        res += (
            "FOLLOWS: \n  No Terminales:\n\t"
            + "\n\t".join(
                str(w) + "    " + str(f) for w, f in follows.items() if isinstance(w, NonTerminal)
            )
            # + "\n Terminales:\n\t"
            # + "\n\t".join(str(w) + "   " + str(f) for w, f in follows.items() if isinstance(w, Terminal))
            # + "\n Alpha:\n\t"
            # + "\n\t".join(str(w) + "   " + str(f) for w, f in follows.items() if not isinstance(w, Symbol))
            + "\n"
        )
        return res

    def _regex_parser_results(self):  # ??? is the same as ll1
        is_reg = parse_input.is_regular_grammar(self.grammar)
        res = "Es Regular:\n" if is_reg else "No es Regular.\n"
        if is_reg:
            self.regex_nfa = regex.convert_to_nfa(self.grammar)
            self.regex = regex.regex_from_nfa(self.regex_nfa)
            res += str(self.regex) + "\n"
            return res, self.regex_nfa._repr_svg_()
        return res, None

    def _ll1_parser_results(self):
        self.ll1 = parsers.LL1(self.grammar)
        return str(self.ll1), None  # has no graph

    def _slr_parser_results(self):
        self.slr = parsers.SLR(self.grammar)
        return str(self.slr), None if self.slr.parse_corrupted else self.slr.automaton._repr_svg_()

    def _lr_parser_results(self):
        self.lr = parsers.LR1(self.grammar)
        return str(self.lr), None if self.lr.parse_corrupted else self.lr.automaton._repr_svg_()

    def _lalr_parser_results(self):
        self.lalr = parsers.LALR(self.grammar)
        return (
            str(self.lalr),
            None if self.lalr.parse_corrupted else self.lalr.automaton._repr_svg_(),
        )

    ############## End Parser Results ##############


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = GramarUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
