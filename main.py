# from tkinter import DISABLED, END, NORMAL, Button, E, Entry, Label, StringVar, Tk, W
from PyQt5 import QtWidgets
from MainWindow import Ui_MainWindow
import cairo
import core
import im
import imageTk
import rsvg


class GramarUI(Ui_MainWindow):
    def __init__(self, root):
        self.root = root
        # root.geometry("800x600")
        # root.title("Proyecto de Compilacion I")
    
    def svgPhotoImage(self, file_path_name):
        "Returns a ImageTk.PhotoImage object represeting the svg file"
        # Based on pygame.org/wiki/CairoPygame and http://bit.ly/1hnpYZY
        svg = rsvg.Handle(file=file_path_name)
        width, height = svg.get_dimension_data()[:2]
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
        context = cairo.Context(surface)
        # context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        svg.render_cairo(context)
        tk_image = ImageTk.PhotoImage("RGBA")
        image = Image.frombuffer("RGBA", (width, height), surface.get_data(), "raw", "BGRA", 0, 1)
        tk_image.paste(image)
        return tk_image

    def validate(self, new_text):
        if not new_text:  # the field is being cleared
            return True

    def reset(self):
        pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


# from tkinter import *
# from tkinter.scrolledtext import ScrolledText

# root = Tk()
# ScrolledText(root).pack()
# root.mainloop()
