# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

import gc

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSvg import QSvgRenderer, QSvgWidget
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.WindowModal)
        MainWindow.resize(1280, 728)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/Qt.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.tabWidget.setFont(font)
        self.tabWidget.setMouseTracking(False)
        self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tabWidget.setObjectName("tabWidget")
        self.tabGrammar = QtWidgets.QWidget()
        self.tabGrammar.setObjectName("tabGrammar")
        self.gridLayout = QtWidgets.QGridLayout(self.tabGrammar)
        self.gridLayout.setObjectName("gridLayout")
        self.textEditGrammar = QtWidgets.QPlainTextEdit(self.tabGrammar)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(28)
        font.setBold(True)
        font.setWeight(75)
        self.textEditGrammar.setFont(font)
        self.textEditGrammar.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.textEditGrammar.setPlainText("")
        self.textEditGrammar.setObjectName("textEditGrammar")
        self.gridLayout.addWidget(self.textEditGrammar, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabGrammar, "")
        self.tabBelongs = QtWidgets.QWidget()
        self.tabBelongs.setObjectName("tabBelongs")
        self.gridLayout_1 = QtWidgets.QGridLayout(self.tabBelongs)
        self.gridLayout_1.setObjectName("gridLayout_1")
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(28)
        font.setBold(True)
        font.setWeight(75)
        self.textEdit_input_belongs = QtWidgets.QTextEdit(self.tabBelongs)
        self.textEdit_input_belongs.setFont(font)
        self.textEdit_input_belongs.setObjectName("textEdit_input_belongs")
        self.gridLayout_1.addWidget(self.textEdit_input_belongs, 0, 0, 1, 1)
        self.buttonAskBelongs = QtWidgets.QPushButton(self.tabBelongs)
        self.buttonAskBelongs.setObjectName("buttonAskBelongs")
        self.gridLayout_1.addWidget(self.buttonAskBelongs, 1, 0, 1, 1)
        # self.textResults = QtWidgets.QTextBrowser(self.tabResults)
        # self.textResults.setObjectName("textResults")
        self.label_belong_result = QtWidgets.QTextBrowser(self.tabBelongs)
        self.label_belong_result.setInputMethodHints(QtCore.Qt.ImhMultiLine)
        self.label_belong_result.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_belong_result.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_belong_result.setLineWidth(1)
        self.label_belong_result.setText("")
        # self.label_belong_result.setTextFormat(QtCore.Qt.PlainText)
        self.label_belong_result.setObjectName("label_belong_result")
        self.gridLayout_1.addWidget(self.label_belong_result, 2, 0, 1, 1)
        self.svgDerivation = QtWidgets.QWidget(self.tabBelongs)
        self.svgDerivation.setObjectName("svgDerivation")
        self.gridLayout_1.addWidget(self.svgDerivation, 3, 0, 1, 1)
        self.tabWidget.addTab(self.tabBelongs, "")
        self.tabResults = QtWidgets.QWidget()
        self.tabResults.setObjectName("tabResults")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tabResults)
        self.gridLayout_2.setObjectName("gridLayout_2")
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(15)
        self.textResults = QtWidgets.QTextBrowser(self.tabResults)
        self.textResults.setObjectName("textResults")
        self.textResults.setFont(font)
        self.gridLayout_2.addWidget(self.textResults, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabResults, "")
        # self.tabAutomaton = QtWidgets.QWidget()
        # self.tabAutomaton.setObjectName("tabAutomaton")
        # self.gridLayout_4 = QtWidgets.QGridLayout(self.tabAutomaton)
        # self.gridLayout_4.setObjectName("gridLayout_4")
        # self.tabWidget.addTab(self.tabAutomaton, "")
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.statusbar.setFont(font)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolBar.sizePolicy().hasHeightForWidth())
        self.toolBar.setSizePolicy(sizePolicy)
        self.toolBar.setMinimumSize(QtCore.QSize(795, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.toolBar.setFont(font)
        self.toolBar.setMovable(False)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionNewGrammar = QtWidgets.QAction(MainWindow)
        self.actionNewGrammar.setObjectName("actionNewGrammar")
        self.actionSaveGrammar = QtWidgets.QAction(MainWindow)
        self.actionSaveGrammar.setObjectName("actionSaveGrammar")
        self.actionLoadGrammar = QtWidgets.QAction(MainWindow)
        self.actionLoadGrammar.setObjectName("actionLoadGrammar")
        self.actionExit = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/arrow-000.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExit.setIcon(icon1)
        self.actionExit.setObjectName("actionExit")
        self.actionSaveGrammarAs = QtWidgets.QAction(MainWindow)
        self.actionSaveGrammarAs.setObjectName("actionSaveGrammarAs")
        self.actionAnalyse = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.actionAnalyse.setObjectName("actionAnalyse")
        self.toolBar.addAction(self.actionAnalyse)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionNewGrammar)
        self.toolBar.addAction(self.actionLoadGrammar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSaveGrammar)
        self.toolBar.addAction(self.actionSaveGrammarAs)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        # my vars
        self.tabs_automatons = {}
        #

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Proyecto de Compilación I"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabGrammar), _translate("MainWindow", "Gramática")
        )
        self.buttonAskBelongs.setText(_translate("MainWindow", "Es reconocido?"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabBelongs), _translate("MainWindow", "Cadenas")
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabResults), _translate("MainWindow", "Resultados")
        )
        # self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAutomaton), _translate("MainWindow", "Autómatas"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "Herramientas"))
        self.actionNewGrammar.setText(_translate("MainWindow", "Nueva Gramática"))
        self.actionNewGrammar.setStatusTip(_translate("MainWindow", "Nueva Gramática"))
        self.actionNewGrammar.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionSaveGrammar.setText(_translate("MainWindow", "&Guardar Gramática"))
        self.actionSaveGrammar.setStatusTip(_translate("MainWindow", "Guardar Gramática"))
        self.actionSaveGrammar.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionLoadGrammar.setText(_translate("MainWindow", "&Cargar Gramática"))
        self.actionLoadGrammar.setStatusTip(_translate("MainWindow", "Cargar Gramática"))
        self.actionLoadGrammar.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionExit.setText(_translate("MainWindow", "&Salir"))
        self.actionExit.setShortcut(_translate("MainWindow", "Ctrl+F4"))
        self.actionSaveGrammarAs.setText(_translate("MainWindow", "Guardar Gramática Como ..."))
        self.actionSaveGrammarAs.setStatusTip(_translate("MainWindow", "Guardar Gramática Como"))
        self.actionSaveGrammarAs.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionAnalyse.setText(_translate("MainWindow", "Analizar"))
        self.actionAnalyse.setToolTip(_translate("MainWindow", "Analizar"))
        self.actionAnalyse.setStatusTip(_translate("MainWindow", "Analizar"))
        self.actionAnalyse.setShortcut(_translate("MainWindow", "F5"))

    # utils funcs
    def _dialog(self, s, icon):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(icon)
        dlg.show()

    def dialog_critical(self, s):
        self._dialog(s, QMessageBox.Critical)

    def dialog_warning(self, s):
        self._dialog(s, QMessageBox.Warning)

    def show_svg(self, svg_img: str, widget: QtWidgets.QWidget, size=None):
        svg_bytes = bytearray(svg_img, encoding="utf-8")
        svgWidget = QSvgWidget(widget)
        svgWidget.renderer().load(svg_bytes)
        width = int(svg_img.split('width="', 1)[1].split("pt", 1)[0])
        height = int(svg_img.split('height="', 1)[1].split("pt", 1)[0])
        px_xy = width / height

        wwidth = widget.width() if not size else size[0]
        wheight = widget.height() if not size else size[1]

        # width = wwidth
        # height = wheight

        if width > wwidth or height > wheight:
            if width > wwidth and height > wheight:
                if width / wwidth > height / wheight:
                    diff_width = width - wwidth
                    width = wwidth
                    height -= (diff_width) * 1 / (px_xy)
                else:
                    diff_height = height - wheight
                    height = wheight
                    width -= (diff_height) * (px_xy)
            elif width > wwidth:
                diff_width = width - wwidth
                width = wwidth
                height -= (diff_width) * 1 / (px_xy)
            else:
                diff_height = height - wheight
                height = wheight
                width -= (diff_height) * (px_xy)

        svgWidget.setGeometry(0, 0, width, height)
        svgWidget.show()

    def create_svg_slot(self, name, svg_str):
        _translate = QtCore.QCoreApplication.translate
        # create tab
        tab = QtWidgets.QWidget()
        tab.setObjectName(f"tab{name}")
        grid = QtWidgets.QGridLayout(tab)
        grid.setObjectName(f"grid{name}")
        self.tabWidget.addTab(tab, "")

        # add tab
        self.tabs_automatons[name] = (tab, grid)
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabResults) + len(self.tabs_automatons),
            _translate("MainWindow", name),
        )

        self.show_svg(svg_str, tab, size=(1122, 600))

    def _close_all_automatons(self):
        count = len(self.tabs_automatons)
        while count:
            self.tabWidget.removeTab(self.tabWidget.indexOf(self.tabResults) + count)
            count -= 1

        for tab, _ in self.tabs_automatons.values():
            # grid.close()
            # grid.deleteLater()
            # del grid

            tab.close()
            tab.deleteLater()
            del tab

        del self.tabs_automatons
        gc.collect()
        self.tabs_automatons = {}


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
