import matplotlib
matplotlib.use('TkAgg')

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.dates import date2num, num2date

import random
import time
import datetime
import account
import tkinter as tk
import tkinter.ttk as ttk


class GUI:
    def __init__(self, parent):
        self.parent = parent
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

        # status bar
        self.status_msg = tk.StringVar()
        self.status_bar = tk.Label(parent, text=self.status_msg, bd=1, relief=tk.SUNKEN, anchor='w')
        self.status_bar.pack(side="bottom", fill="x")
        self.log("[info] Ready...")

    def log(self, message):
        self.status_bar.configure(text=message)


class Grind(GUI):
    internet_checks = False

    def __init__(self, parent):
        self.gui = GUI.__init__(self, parent)
        # file menu
        parent.config(menu=self.add_file_menu(parent))

        self.plot_attempts = False

        # required vars
        self.var_search = tk.StringVar()
        self.var_min = tk.StringVar()
        self.var_max = tk.StringVar()
        self.var_min.set("10")
        self.var_max.set("300")

        # labels
        self.lbl_min = tk.Label(self.mid_frame, text="Min:", anchor='w')
        self.lbl_min.grid(row=0, column=0, sticky='wnse')
        self.lbl_min = tk.Label(self.mid_frame, text="Max:", anchor='w')
        self.lbl_min.grid(row=0, column=1, sticky='wnse')
        self.lbl_min = tk.Label(self.mid_frame, text="Search:", anchor='w')
        self.lbl_min.grid(row=0, column=2, columnspan=2, sticky='wnse')
        # Expensive Operation: get grind info
        self.grinders = account.load_json_data()

        # list of grinders
        self.names_and_grinds = self.get_account_names_and_grinds()

        # setup spinboxes
        self.sbx_grinds_min = tk.Spinbox(self.mid_frame, from_=0, to=4000, textvariable=self.var_min, width=4)
        self.sbx_grinds_min.grid(row=1, column=0, sticky='ns', pady=0, padx=0)
        self.sbx_grinds_max = tk.Spinbox(self.mid_frame, from_=0, to=4000, textvariable=self.var_max, width=4)
        self.sbx_grinds_max.grid(row=1, column=1, sticky='ns', pady=0, padx=0)

        # search bar UI
        self.entry_search = tk.Entry(self.mid_frame, textvariable=self.var_search, width=20)
        self.entry_search.grid(row=1, column=2, sticky='ns', pady=0, padx=0)

        # listbox UI and contents
        self.listbox_names = self.create_listbox(self.bottom_frame, column=0)
        self.populate_listbox()
        self.listbox_names.bind("<<ListboxSelect>>", self.display_grinds_for_tree)

        # setup Traces - callbacks for what the spinners will do.
        self.var_min.trace("w", lambda x, y, z: self.populate_listbox())
        self.var_max.trace("w", lambda x, y, z: self.populate_listbox())
        self.var_search.trace("w", lambda x, y, z: self.populate_listbox())

        # Setup Treeviews
        self.headers_01 = ["Age", "Sex"]
        self.tree_info = self.create_treeview(self.mid_frame, self.headers_01, [],
                                              column=3, row=0, weight=1, _scrollbar=False)

        self.headers = ["Date", "Start", "End", "Time"]
        self.tree_grind = self.create_treeview(self.bottom_frame, self.headers, [], column=3, row=1, weight=1)

        # plot
        # These are the "Tableau 20" colors as RGB.
        self.tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                          (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                          (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                          (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                          (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

        # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
        for i in range(len(self.tableau20)):
            r, g, b = self.tableau20[i]
            self.tableau20[i] = (r / 255., g / 255., b / 255.)

        self.figure = plt.figure(figsize=(5, 6), dpi=70, facecolor='white', frameon=True)#, tight_layout=True)
        self.figure.subplots_adjust(bottom=0.35, left=0.05, right=0.8, top=0.9)

        self.axes = plt.axes()

        self.ax = self.figure.add_subplot(111)
        # Where did the data come from?
        self.ax.text(0, -0.45, "Data source: https://www.grousemountain.com/grind_stats",
                     transform=self.ax.transAxes,
                     fontsize=11)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["bottom"].set_color('grey')
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_color('grey')

        # ensure only the bottom and left ticks are visible
        self.ax.get_xaxis().tick_bottom()
        self.ax.get_yaxis().tick_left()

        self.dataplot = FigureCanvasTkAgg(self.figure, master=self.bottom_frame)

        # hover callback setup here.
        self.figure.canvas.mpl_connect('motion_notify_event', self.on_move)

        self.dataplot.show()
        self.dataplot.get_tk_widget().grid(columnspan=5, sticky='nesw')
        self._update_plot([], label=None)

        self.annotations = []

    def annotate_plot_points(self, point, x, y, label, axes, annotations):
        for index_x, index_y in zip(x, y):
            current = self.convert_seconds_to_timedelta(index_y)
            best = self.convert_seconds_to_timedelta(min(y))
            mean = self.convert_seconds_to_timedelta(np.mean(y))
            annotation = axes.annotate("{}\nCurrent: {}\nBest: {}\nMean:{}".format(label, current, best, mean),
                                       xy=(index_x, index_y), xycoords='data',
                                       xytext=(index_x+0.02, index_y+0.1), textcoords='data',
                                       horizontalalignment="left",
                                       # arrowprops=dict(arrowstyle="simple", connectionstyle="arc3,rad=-0.2"),
                                       bbox=dict(boxstyle="round", facecolor="w", edgecolor="0.5", alpha=0.8))
            annotation.set_visible(False)
            annotations.append([point, annotation])

    def on_move(self, event):
        counter = 0
        visibility_changed = False
        for point, annotation in self.annotations:
            should_be_visible = (point.contains(event)[0] is True)
            if should_be_visible:
                if counter != point.contains(event)[1]['ind'][0]:
                    should_be_visible = False
                counter += 1
            if should_be_visible != annotation.get_visible():
                visibility_changed = True
                annotation.set_visible(should_be_visible)

        if visibility_changed:
            # plt.draw()
            # plt.draw() is not enough using tkinter
            plt.gcf().canvas.draw()

    @staticmethod
    def convert_timedelta_to_seconds(_time, second_breakdown=60):
        hours, minutes, seconds = _time.split(":")
        return (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) / second_breakdown

    @staticmethod
    def convert_seconds_to_timedelta(_time):
        return str(datetime.timedelta(seconds=_time*60))

    @staticmethod
    def convert_standard_to_military_time(standard):
        struct_time = time.strptime(standard, '%I:%M:%S %p')
        military_time = "{0:02d}:{1:02d}:{2:02d}".format(struct_time.tm_hour,
                                                         struct_time.tm_min,
                                                         struct_time.tm_sec)
        return military_time

    # -- File Menu -------------------------------------------------------------------------
    def add_file_menu(self, parent):
        menubar = tk.Menu(parent, tearoff=1)
        filemenu = tk.Menu(menubar)
        filemenu.add_command(label="Update Account", command=self._update_account)
        # filemenu.add_command(label="Load Account", command=self._load_account)
        filemenu.add_command(label="Save Changes", command=self._save_changes)
        filemenu.add_command(label="Clear Plots", command=self._clear_plots)
        filemenu.add_command(label="Plot Everything", command=self._plot_everything)
        filemenu.add_command(label="Switch Plot Type", command=self._switch_plot)
        menubar.add_cascade(label="File", menu=filemenu)

        return menubar

    def _switch_plot(self):
        self.ax.clear()
        self.plot_attempts = not self.plot_attempts

    def _load_account(self):
        self.grinders = account.load_json_data()

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

    def _clear_plots(self):
        self.ax.clear()
        self.dataplot.show()

    def _plot_everything(self):
        for uuid, data in self.grinders.items():
            if data['name'] != "Not Found" and data['name'] != "Service Unavailable":
                grinds = self.grinders[uuid]['grinds']
                if grinds is not None and (len(grinds) > 0 and type(grinds[0]) == dict):
                    collector = [[grind['date'],
                                  self.convert_standard_to_military_time(grind['start']),
                                  self.convert_standard_to_military_time(grind['end']),
                                  grind['time']] for grind in grinds]
                    collector = sorted(collector, key=lambda x: x[0])
                    # times = [self.convert_timedelta_to_seconds(grind[3]) for grind in collector]
                    # times = [x for x in times if x < 150]
                    self._update_plot(collector, label=data['name'], legend=False)

    # -- ListBox ---------------------------------------------------------------------------
    def populate_listbox(self):
        _min = 0 if self.sbx_grinds_min.get() == '' else int(self.sbx_grinds_min.get())
        _max = 0 if self.sbx_grinds_max.get() == '' else int(self.sbx_grinds_max.get())

        try:
            names = [name for name, grinds in self.names_and_grinds
                     if grinds is not None and _min <= len(grinds) <= _max]
            names.sort()
            search_term = self.var_search.get()

            self.listbox_names.delete(0, tk.END)
            items = [x for x in names if search_term.lower() in x.lower()]
            for item in items:
                self.listbox_names.insert('end', item)

            for i in range(0, len(items), 2):
                self.listbox_names.itemconfigure(i, background='#f0f0ff')
        except Exception as e:
            print(e)

    def create_listbox(self, master, column=0):
        listbox = tk.Listbox(master, height=15, width=35)
        listbox.grid(column=column, row=0, rowspan=2, stick='news')
        master.grid_columnconfigure(column, weight=0)

        s = ttk.Scrollbar(master, orient=tk.VERTICAL, command=listbox.yview)
        s.grid(column=column + 1, row=0, rowspan=2, sticky='ns')
        listbox['yscrollcommand'] = s.set

        return listbox

    # -- TreeView --------------------------------------------------------------------------
    def create_treeview(self, master, columns, rows, column=0, row=0, weight=0, _scrollbar=True):
        tree = ttk.Treeview(master, height=1, columns=columns, show="headings")

        if _scrollbar:
            vsb = ttk.Scrollbar(orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            vsb.grid(column=column + 1, row=row, sticky='nsew', in_=master)

        tree.grid(column=column, row=row, rowspan=2, sticky='nsew', in_=master)

        master.grid_columnconfigure(column, weight=weight)
        master.grid_rowconfigure(row, weight=weight)

        self.populate_treeview(tree, columns, rows)

        return tree

    def populate_treeview(self, tree, columns, rows):
        for i in tree.get_children():
            tree.delete(i)

        for col in columns:
            tree.heading(col, text=col.title(), command=lambda c=col: self.sortby(tree, c, 0))
            tree.column(col)

        for index, row in enumerate(rows):
            if index % 2 == 0:
                tree.insert('', 'end', values=row, tags = ('odd',))
            else:
                tree.insert('', 'end', values=row, tags = ('even',))
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(row):
                tree.column(columns[ix])

        tree.tag_configure('odd', background='#f0f0ff')

    def sortby(self, tree, col, descending):
        """sort tree contents when a column header is clicked on"""

        # grab values to sort
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        # now sort the data in place
        data.sort(reverse=descending)

        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not descending)))

        # Update the plot line
        times = [self.convert_timedelta_to_seconds(tree.set(child, "Time")) for child in tree.get_children('')]
        if len(times) > 0:
            self._update_plot(times, label="")

    # -- Data Management
    def get_account_names_and_grinds(self, clean_data_only=True):
        info = [(data['name'], data['grinds']) for uuid, data in self.grinders.items()]
        print("Number of Accounts: {}".format(len(info)))

        service_unavailable = [name for name, grinds in info if "Service Unavailable" in name]
        print("Number of 'Service Unavailable Accounts: {}".format(len(service_unavailable)))

        if clean_data_only:
            info = [(name, grinds) for name, grinds in info
                    if "Not Found" not in name and "Service Unavailable" not in name]
        print("Number of valid accounts loaded: {}".format(len(info)))

        return info

    def _get_grinds(self, value):
        for uuid, data in self.grinders.items():
            if value in data['name']:
                grinds = data['grinds']

                if self.internet_checks is True:
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
        self.log("[info] UUID: {}".format(value))
        # self.tree_grind.delete(0, tk.END)  # clear

        age, sex, grinds = self._get_grinds(value)
        if age is None and sex is None:
            age, sex = ("Unknown", "Unknown")
        self.populate_treeview(self.tree_info, self.headers_01, [(age, sex)])

        if grinds is not None:
            collector = [[grind['date'],
                          self.convert_standard_to_military_time(grind['start']),
                          self.convert_standard_to_military_time(grind['end']),
                          grind['time']] for grind in grinds]
            collector = sorted(collector, key=lambda x: x[0])
            self.populate_treeview(self.tree_grind, self.headers, collector)
            times = [self.convert_timedelta_to_seconds(grind[3]) for grind in collector]
            self._update_plot(collector, label=value)
            #self._update_plot(times, label=value)

    def _update_plot(self, data, label=None, legend=True):
        # self.a.clear()
        dates = [date2num(datetime.datetime.strptime(grind[0], "%Y-%m-%d")) for grind in data]
        times = [self.convert_timedelta_to_seconds(grind[3]) for grind in data]
        if len(dates) > 0:
            pass

        if label is not None:
            if self.plot_attempts:
                dates = [x for x, y in enumerate(dates)]
                point, = self.ax.plot(dates, times, '.-', label=label, color=self.tableau20[random.randint(0, 19)])
            else:
                point, = self.ax.plot(dates, times, '.-', label=label, color=self.tableau20[random.randint(0, 19)])
                #self.ax.scatter(dates, times)

                # matplotlib date format object
                hfmt = matplotlib.dates.DateFormatter('%Y-%m-%d')
                items = self.ax.get_xticks().tolist()
                if items[0] > 1:
                    self.ax.set_xticklabels([num2date(item) for item in items if int(item) > 1], rotation=42, fontsize=11)
                    self.ax.xaxis.set_major_formatter(hfmt)

            self.annotate_plot_points(point, dates, times, label, self.axes, self.annotations)

            if legend:
                # Now add the legend with some customizations.
                legend = self.ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1), framealpha=0.0, shadow=False)

                # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
                frame = legend.get_frame()
                frame.set_facecolor('0.90')

                # Set the fontsize
                for label in legend.get_texts():
                    label.set_fontsize('large')

                for label in legend.get_lines():
                    label.set_linewidth(1.5)  # the legend line width
        plot_type = "Attempt" if self.plot_attempts else "Dates"
        self.ax.set_title('Minutes To Complete Grouse Grind Plotted By {}'.format(plot_type))
        self.ax.set_ylabel('Duration (minutes)')
        self.dataplot.show()


def grouse_grind_app():
    root = tk.Tk()
    root.title("Grouse Grind App 0.5")
    # root.geometry("720x500")
    Grind(root)
    root.mainloop()


if __name__ == "__main__":
    grouse_grind_app()
