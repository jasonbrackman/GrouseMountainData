import account
import collections
import tkinter as tk
from tkinter import ttk

grind = collections.namedtuple('grind', 'date, start, end, time')

class App(tk.Frame):
    def __init__(self, master=None):
        self.grinders = account.load_json_data()

        tk.Frame.__init__(self, master, width=800, height=600)
        #self.grid(sticky=tk.N+tk.S+tk.W+tk.E)
        self.grid_propagate(0)

        self.master = master
        self.master.title("Grouse Grind App 0.1")

        # <create the rest of your GUI here>
        names = self.get_grouse_grind_names()
        names.sort()

        self.listbox_names = self.create_listbox(self.master, names, column=0)
        self.listbox_names.bind("<<ListboxSelect>>", self.display_grinds)
        self.listbox_grind = self.create_listbox(self.master, [], column=3)

        tk.Label(self.master, text="Age:").grid(column=2)
        tk.Label(self.master, text="Sex:").grid(column=2)

    def display_grinds(self, event):
        widget = event.widget
        value = widget.get(widget.curselection()[0])
        print(value)
        self.listbox_grind.delete(0, tk.END)  # clear

        def get_grinds(value):
            for uuid, data in self.grinders.items():
                if value in data['name']:
                    return data['grinds']

        grinds = get_grinds(value)
        for grind in grinds:
            self.listbox_grind.insert('end', "{}, {}".format(grind['date'], grind['time']))

    def get_grouse_grind_names(self, clean_data_only=True):
        names = [data['name'] for uuid, data in self.grinders.items()]

        if clean_data_only:
            names = [name for name in names if "Not Found" not in name and "Service Unavailable" not in name]

        return names

    def create_listbox(self, master, items=None, column=0):
        listbox = tk.Listbox(master, height=30, width=35)
        listbox.grid(column=column, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        master.grid_columnconfigure(column, weight=1)
        #master.grid_rowconfigure(0, weight=1)

        s = ttk.Scrollbar(master, orient=tk.VERTICAL, command=listbox.yview)
        s.grid(column=column+1, row=0, sticky=(tk.N, tk.S))
        listbox['yscrollcommand'] = s.set

        for item in items:
            listbox.insert('end', item)

        for i in range(0, len(items), 2):
            listbox.itemconfigure(i, background='#f0f0ff')

        return listbox

if __name__ == "__main__":
    root = tk.Tk()
    my_gui = App(root)
    root.mainloop()
