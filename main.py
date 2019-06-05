from tkinter import (
    DISABLED, END, NORMAL, Button, E, Entry, Label, StringVar, Tk, W)

import cairo
import core
import im
import imageTk
import rsvg


class GramarUI:
    def __init__(self, root):
        self.root = root
        root.geometry("800x600")
        root.title("Proyecto de Compilacion I")

        self.error_message = ""
        self.message = "Entre Su gramatica"
        self.label_text = StringVar()
        self.label_text.set(self.message)
        self.label = Label(root, textvariable=self.label_text)

        vcmd = root.register(self.validate) # we have to wrap the command
        self.entry = Entry(root, validate="key", validatecommand=(vcmd, '%P'))

        self.guess_button = Button(root, text="Guess", command=self.guess_number)
        self.reset_button = Button(root, text="Play again", command=self.reset, state=DISABLED)

        self.label.grid(row=0, column=0, columnspan=2, sticky=W+E)
        self.entry.grid(row=1, column=0, columnspan=2, sticky=W+E)
        self.guess_button.grid(row=2, column=0)
        self.reset_button.grid(row=2, column=1)

    
    def svgPhotoImage(self, file_path_name):
        "Returns a ImageTk.PhotoImage object represeting the svg file" 
        # Based on pygame.org/wiki/CairoPygame and http://bit.ly/1hnpYZY        
        svg = rsvg.Handle(file=file_path_name)
        width, height = svg.get_dimension_data()[:2]
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
        context = cairo.Context(surface)
        #context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        svg.render_cairo(context)
        tk_image=ImageTk.PhotoImage('RGBA')
        image=Image.frombuffer('RGBA',(width,height),surface.get_data(),'raw','BGRA',0,1)
        tk_image.paste(image)
        return (tk_image)



    def validate(self, new_text):
        if not new_text: # the field is being cleared
            self.guess = None
            return True

        try:
            guess = int(new_text)
            if 1 <= guess <= 100:
                self.guess = guess
                return True
            else:
                return False
        except ValueError:
            return False

    def guess_number(self):
        pass

    def reset(self):
        self.entry.delete(0, END)
        self.label_text.set(self.message)

        self.guess_button.configure(state=NORMAL)
        self.reset_button.configure(state=DISABLED)

if __name__ == "__main__":
    root = Tk()
    my_gui = GuessingGame(root)
    root.mainloop()

# from tkinter import *
# from tkinter.scrolledtext import ScrolledText

# root = Tk()
# ScrolledText(root).pack()
# root.mainloop()

# from tkinter import *

# root = Tk()
# text = Text(root)
# text.pack()
# root.mainloop()

# from tkinter import *
# import sys


# def doNothing():
#     print("Test")


# root = Tk()
# root.title("TextEditor")
# root.geometry("800x600")
# menu = Menu(root)
# root.config(menu=menu)

# subMenu = Menu(menu)
# menu.add_cascade(label="File", menu=subMenu)
# subMenu.add_command(label="New Project...", command =doNothing)
# subMenu.add_command(label="Save", command=doNothing)
# subMenu.add_separator()

# editMenu = Menu(menu)
# menu.add_cascade(label="Edit", menu=editMenu)
# editMenu.add_command(label="Undo",command=doNothing)

# root.mainloop()
