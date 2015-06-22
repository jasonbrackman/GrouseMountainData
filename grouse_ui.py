import os

import main
# import account
import collections
# from tkinter import *
import tkinter as tk
from tkinter import ttk

grind = collections.namedtuple('grind', 'date, start, end, time')

class App(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, width=640, height=480)
        self.master = master
        self.master.title("Grouse Grind App 0.1")
        self.grid_propagate()

        # <create the rest of your GUI here>
        names = self.get_grouse_grind_names()
        names.sort()
        self.create_listbox(self.master, names)

    @staticmethod
    def get_grouse_grind_names(clean_data_only=True):
        new_storage_path = os.path.expanduser("~/Documents/grinders.pickle")
        grinders = main.load_data(_storage_path=new_storage_path)

        names = [grinder.name for grinder in grinders]

        if clean_data_only:
            names = [name for name in names if "Not Found" not in name and "Service Unavailable" not in name]

        return names

    def create_listbox(self, master, items=None):
        self.listbox = tk.Listbox(master, height=20, width=35)
        self.listbox.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        s = ttk.Scrollbar(master, orient=tk.VERTICAL, command=self.listbox.yview)
        s.grid(column=1, row=0, sticky=(tk.N, tk.S))
        self.listbox['yscrollcommand'] = s.set
        # ttk.Sizegrip().grid(column=1, row=1, sticky=(tk.S, tk.E))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        for item in items:
            self.listbox.insert('end', item)

        for i in range(0, len(items), 2):
            self.listbox.itemconfigure(i, background='#f0f0ff')



if __name__ == "__main__":
    root = tk.Tk()
    my_gui = App(root)
    root.mainloop()
