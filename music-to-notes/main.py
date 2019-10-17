import tkinter as tk
from tkinter import filedialog


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

        menubar = tk.Menu(root)
        menubar.add_command(label="Hello!", command=self.say_hi)
        menubar.add_command(label="Quit!", command=root.quit)
        root.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.say_hi)
        filemenu.add_command(label="Save", command=self.say_hi)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.say_hi)
        menubar.add_cascade(label="Help", menu=helpmenu)


    def say_hi(self):
        print("hi there, everyone!")


    def open_file_dialog(self):
        file = filedialog.askopenfile()


root = tk.Tk()
root.geometry("500x400+300+300")
app = Application(master=root)
app.mainloop()
