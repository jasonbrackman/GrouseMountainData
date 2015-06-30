import account
import collections
import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk

# grind = collections.namedtuple('grind', 'date, start, end, time')

class App(tk.Frame):
    def __init__(self, master=None):
        self.grinders = account.load_json_data()

        self.container = tk.Frame.__init__(self, master, width=300, height=200)
        self.grid(sticky=(tk.N, tk.W, tk.E, tk.S))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_propagate(0)

        self.master = master
        self.master.title("Grouse Grind App 0.1")

        # <create the rest of your GUI here>
        names = self.get_grouse_grind_names()
        names.sort()

        self.listbox_names = self.create_listbox(self.master, names, column=0)
        self.listbox_names.bind("<<ListboxSelect>>", self.display_grinds_for_tree)

        # self.listbox_grind = self.create_listbox(self.master, [], column=3)
        self.headers = ["Date", "Start", "End", "Time"]
        margin = 20
        self.rows = [(" "*margin,
                      " "*margin,
                      " "*margin,
                      " "*margin)]

        self.tree_grind = self.create_treeview(self.headers, self.rows, column=3)
        # tk.Label(self.master, text="Age:").grid(column=2)
        # tk.Label(self.master, text="Sex:").grid(column=2)

    def _get_grinds(self, value):
        for uuid, data in self.grinders.items():
            if value in data['name']:
                return data['grinds']

    def display_grinds_for_tree(self, event):
        widget = event.widget
        value = widget.get(widget.curselection()[0])
        # self.tree_grind.delete(0, tk.END)  # clear

        grinds = self._get_grinds(value)
        collector = [[grind['date'],
                      grind['start'],
                      grind['end'],
                      grind['time']] for grind in grinds]

        self._build_treeview(self.tree_grind, self.headers, collector)
    """
    def display_grinds(self, event):
        widget = event.widget
        value = widget.get(widget.curselection()[0])
        print(value)
        self.listbox_grind.delete(0, tk.END)  # clear

        grinds = self._get_grinds(value)
        for grind in grinds:
            self.listbox_grind.insert('end', "{}, {}".format(grind['date'], grind['time']))
    """

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

    def create_treeview(self, columns, rows, column=0):

        tree = ttk.Treeview(columns=columns, show="headings")
        tree.grid(column=column, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self._build_treeview(tree, columns, rows)

        return tree

    def _build_treeview(self, tree, columns, rows):
        for i in tree.get_children():
            tree.delete(i)

        for col in columns:
            tree.heading(col, text=col.title(), command=lambda c=col: (tree, c, 0))
            # adjust the column's width to the header string
            tree.column(col, width=tkFont.Font().measure(col.title()))

        for row in rows:
            tree.insert('', 'end', values=row)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(row):
                # col_w = tkFont.Font().measure(val)
                col_w = 82
                if tree.column(columns[ix], width=None) < col_w:
                    tree.column(columns[ix], width=col_w)


if __name__ == "__main__":
    root = tk.Tk()
    my_gui = App(root)
    root.mainloop()

