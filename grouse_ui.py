import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import datetime

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import account
import tkinter as tk
import tkinter.ttk as ttk

class GUI:
    def __init__(self, parent):
        # Build main container
        self.main_container = tk.Frame(parent, background="bisque")
        self.main_container.pack(side="top", fill="both", expand=True, anchor='center')

        # Top Frame
        self.top_frame = tk.Frame(self.main_container, background="green")
        self.top_frame.pack(side="top", fill="y", expand=False)

        # mid Frame
        self.mid_frame = tk.Frame(self.main_container, background="gray")
        self.mid_frame.pack(side="top", fill="x", expand=False)

        # Bottom Frame
        self.bottom_frame = tk.Frame(self.main_container, background="yellow")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)


class Grind(GUI):
    def __init__(self, parent):
        self.gui = GUI.__init__(self, parent)

        parent.title("Grouse Grind App 0.2b")
        # Expensive Operation: get grind info
        self.grinders = account.load_json_data()

        # search bar
        self.var_search = tk.StringVar()
        self.var_search.trace("w", lambda name, index, mode: self.update_list())
        self.entry_search = tk.Entry(self.mid_frame, textvariable=self.var_search, width=34)
        self.entry_search.grid(row=1, column=0, sticky='nsew', pady=2, padx=2)

        # list of grinders
        self.names = self.get_grouse_grind_names()
        self.names.sort()
        self.listbox_names = self.create_listbox(self.bottom_frame, items=self.names, column=0)
        self.listbox_names.bind("<<ListboxSelect>>", self.display_grinds_for_tree)

        self.headers_01 = ["Age", "Sex"]
        self.tree_info = self.create_treeview(self.mid_frame, self.headers_01, [],
                                              column=3, row=0, weight=1, _scrollbar=False)

        self.headers = ["Date", "Start", "End", "Time"]
        self.tree_grind = self.create_treeview(self.bottom_frame, self.headers, [], column=3, row=1, weight=1)
        # file menu
        parent.config(menu=self.add_file_menu(parent))

        # plot
        self.f = Figure(figsize=(4, 5), dpi=72, tight_layout=True)
        self.a = self.f.add_subplot(111)
        self.a.plot([])
        self.a.set_title('Grind Times')
        self.a.set_xlabel('Grind #')
        self.a.set_ylabel('Duration (minutes)')
        self.dataplot = FigureCanvasTkAgg(self.f, master=self.bottom_frame)
        self.dataplot.show()
        self.dataplot.get_tk_widget().grid(columnspan=5, sticky='nesw')

    @staticmethod
    def get_time(_time, second_breakdown=60):
        hours, minutes, seconds = _time.split(":")
        return (int(hours)*3600+int(minutes)*60+int(seconds))/second_breakdown

    def add_file_menu(self, parent):
        menubar = tk.Menu(parent, tearoff=1)
        filemenu = tk.Menu(menubar)
        filemenu.add_command(label="Update Account", command=self._update_account)
        filemenu.add_command(label="Save Changes", command=self._save_changes)
        menubar.add_cascade(label="File", menu=filemenu)

        return menubar

    def _save_changes(self):
        account.dump_json_data(self.grinders)

    def _update_account(self):
        selected = self.listbox_names.curselection()[0]
        value = self.listbox_names.get(selected)

        if value is not None:
            numbers = [uuid for uuid, data in self.grinders.items() if data['name'] == value]
            uuid, name, sex, age, grinds = account.get_grind_data(numbers[0])
            self.grinders[uuid]['sex'] = sex
            self.grinders[uuid]['age'] = age
            if self.grinders[uuid]['grinds'] is None:
                self.grinders[uuid]['grinds'] = list()

            for grind in grinds:
                if grind not in self.grinders[uuid]['grinds']:
                    self.grinders[uuid]['grinds'].append(grind)

    def update_list(self):
        search_term = self.var_search.get()
        self.listbox_names.delete(0, tk.END)
        items = [x for x in self.names if search_term.lower() in x.lower()]
        for item in items:
            self.listbox_names.insert('end', item)

        for i in range(0, len(items), 2):
            self.listbox_names.itemconfigure(i, background='#f0f0ff')

    def create_listbox(self, master, items=None, column=0):
        listbox = tk.Listbox(master, height=30, width=35)
        listbox.grid(column=column, row=0, rowspan=2, stick='news')
        master.grid_columnconfigure(column, weight=0)

        s = ttk.Scrollbar(master, orient=tk.VERTICAL, command=listbox.yview)
        s.grid(column=column+1, row=0, rowspan=2, sticky='ns')
        listbox['yscrollcommand'] = s.set

        for item in items:
            listbox.insert('end', item)

        for i in range(0, len(items), 2):
            listbox.itemconfigure(i, background='#f0f0ff')

        return listbox

    def create_treeview(self, master, columns, rows, column=0, row=0, weight=0, _scrollbar=True):
        tree = ttk.Treeview(master, height=1, columns=columns, show="headings")

        if _scrollbar:
            vsb = ttk.Scrollbar(orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            vsb.grid(column=column+1, row=row, sticky='nsew', in_=master)

        tree.grid(column=column, row=row, rowspan=2, sticky='nsew', in_=master)

        master.grid_columnconfigure(column, weight=weight)
        master.grid_rowconfigure(row, weight=weight)

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
                grinds = data['grinds']

                if grinds is not None and (len(grinds) > 0 and type(grinds[0]) != dict):
                    print("[{}] {}'s Grind format in unexpected format: {}".format(uuid, value, type(grinds[0])))
                    grinds = account.collect_grind_times([], uuid)
                    self.grinders[uuid]['grinds'] = grinds
                    dirty = True

                if data['age'] is None or data['sex'] is None:
                    print("[{}] Information was not up to date for: {}".format(uuid, value))
                    _, _, sex, age, grinds = account.get_grind_data(uuid)
                    self.grinders[uuid]['age'] = age
                    self.grinders[uuid]['sex'] = sex
                    # its possible for age and sex to be unknown if user did not complete any grinds yet.
                    if age is not None and sex is not None:
                        if self.grinders[uuid]['grinds'] is None:
                                self.grinders[uuid]['grinds'] = list()

                        # something was updated -- so might as well see if there are new grinds too.
                        for grind in grinds:
                            if grind not in self.grinders[uuid]['grinds']:
                                self.grinders[uuid]['grinds'].append(grind)

                return self.grinders[uuid]['age'], self.grinders[uuid]['sex'], self.grinders[uuid]['grinds']

    def display_grinds_for_tree(self, event):
        widget = event.widget
        value = widget.get(widget.curselection()[0])
        # self.tree_grind.delete(0, tk.END)  # clear

        age, sex, grinds = self._get_grinds(value)
        if age is None and sex is None:
            age, sex = ("Unknown", "Unknown")
        self._build_treeview(self.tree_info, self.headers_01, [(age, sex)])

        if grinds is not None:
            collector = [[grind['date'],
                          grind['start'],
                          grind['end'],
                          grind['time']] for grind in grinds]
            collector = sorted(collector, key=lambda x: x[0])
            self._build_treeview(self.tree_grind, self.headers, collector)
            times = [self.get_time(grind[3]) for grind in collector]
            self._update_plot(times)

    def _update_plot(self, times):
        self.a.clear()
        self.a.set_title('Grind Times')
        self.a.set_xlabel('Grind #')
        self.a.set_ylabel('Duration (minutes)')
        self.a.plot(times)
        self.dataplot.show()

    def sortby(self, tree, col, descending):
        """sort tree contents when a column header is clicked on"""

        # grab values to sort
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        # if the data to be sorted is numeric change to float
        # data =  change_numeric(data)
        # now sort the data in place
        data.sort(reverse=descending)

        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not descending)))

        times = [self.get_time(tree.set(child, "Time")) for child in tree.get_children('')]
        self._update_plot(times)


def my_grind_app_attempt_02():
    root = tk.Tk()
    my_gui = Grind(root)
    root.mainloop()

if __name__ == "__main__":
    my_grind_app_attempt_02()
