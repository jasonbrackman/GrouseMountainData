import account
import tkinter as tk
import tkinter.ttk as ttk

class GUI:
    def __init__(self, parent):
        # Build main container
        self.main_container = tk.Frame(parent, background="bisque")
        self.main_container.pack(side="top", fill="both", expand=True)

        # Top Frame
        self.top_frame = tk.Frame(self.main_container, background="green")
        self.top_frame.pack(side="top", fill="x", expand=False)

        # Bottom Frame
        self.bottom_frame = tk.Frame(self.main_container, background="yellow")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)


class Grind(GUI):
    def __init__(self, parent):
        self.gui = GUI.__init__(self, parent)
        parent.title("Grouse Grind App 0.2b")

        # get grind info
        self.grinders = account.load_json_data()
        names = self.get_grouse_grind_names()
        names.sort()
        self.listbox_names = self.create_listbox(self.bottom_frame, items=names, column=0)
        self.listbox_names.bind("<<ListboxSelect>>", self.display_grinds_for_tree)

        self.headers = ["Date", "Start", "End", "Time"]
        self.tree_grind = self.create_treeview(self.bottom_frame, self.headers, [], column=3, weight=1)

    def create_listbox(self, master, items=None, column=0):
        listbox = tk.Listbox(master, height=30, width=35)
        listbox.grid(column=column, row=0, stick='news')
        master.grid_columnconfigure(column, weight=0)

        s = ttk.Scrollbar(master, orient=tk.VERTICAL, command=listbox.yview)
        s.grid(column=column+1, row=0, sticky='ns')
        listbox['yscrollcommand'] = s.set

        for item in items:
            listbox.insert('end', item)

        for i in range(0, len(items), 2):
            listbox.itemconfigure(i, background='#f0f0ff')

        return listbox

    def create_treeview(self, master, columns, rows, column=0, weight=0):
        tree = ttk.Treeview(master, columns=columns, show="headings")
        vsb = ttk.Scrollbar(orient=tk.VERTICAL, command=tree.yview)

        tree.configure(yscrollcommand=vsb.set)
        tree.grid(column=column, row=0, sticky='nsew', in_=master)
        vsb.grid(column=column+1, row=0, sticky='nsew', in_=master)

        master.grid_columnconfigure(0, weight=weight)
        master.grid_rowconfigure(0, weight=weight)

        self._build_treeview(tree, columns, rows)

        return tree

    def _build_treeview(self, tree, columns, rows):
        width = 82
        for i in tree.get_children():
            tree.delete(i)

        for col in columns:
            tree.heading(col, text=col.title(), command=lambda c=col: self.sortby(tree, c, 0))
            # adjust the column's width to the header string
            tree.column(col, width=width)  # tkFont.Font().measure(col.title()))

        for row in rows:
            tree.insert('', 'end', values=row)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(row):
                # col_w = tkFont.Font().measure(val)
                col_w = width
                if tree.column(columns[ix], width=None) < col_w:
                    tree.column(columns[ix], width=col_w)

    def get_grouse_grind_names(self, clean_data_only=True):
        names = [data['name'] for uuid, data in self.grinders.items()]

        if clean_data_only:
            names = [name for name in names if "Not Found" not in name and "Service Unavailable" not in name]

        return names

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

    def sortby(self, tree, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        # if the data to be sorted is numeric change to float
        #data =  change_numeric(data)
        # now sort the data in place
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not descending)))

def my_grind_app_attempt_02():
    root = tk.Tk()
    my_gui = Grind(root)
    root.mainloop()

if __name__ == "__main__":
    my_grind_app_attempt_02()
