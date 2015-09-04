import os
import matplotlib

# note that the 'TKAgg' is telling matplotlib to work with Tkinter
matplotlib.use('TkAgg')

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # , NavigationToolbar2TkAgg
from matplotlib.dates import date2num, num2date

import random
import time
import datetime
import account
import tkinter as tk
import tkinter.ttk as ttk


class GUI:
    """
    This is the skeleton for the GUI layout.  It pretty much just packs a bunch of boxes together to create the
    following:

    ######################
    #        top         #
    ######################
    #                    #
    #        mid         #
    #                    #
    #                    #
    ######################
    #      bottom        #
    ######################

    There are some generic convenience functions as well, such as:
        - a status bar filler for the bottom box
        - a log command to fill the status bar
        - a func to add an app icon.
    """
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
        self.setup_app_icon()

    def log(self, message):
        self.status_bar.configure(text=message)

    def setup_app_icon(self):
        # setup the app icon
        head, tail = os.path.split(os.path.realpath(__file__))
        icon_path = os.path.join(head, 'assets', 'mountain.ico')
        self.parent.wm_iconbitmap(bitmap=icon_path)


class Grind(GUI):
    plot_attempts = False

    # http://tableaufriction.blogspot.ca/2012/11/finally-you-can-use-tableau-data-colors.html
    # These are the "Tableau 20" colors as RGB.
    # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
    tableau20 = [(r / 255., g / 255., b / 255.) for r, g, b in [(31, 119, 180), (174, 199, 232), (255, 127, 14),
                                                                (255, 187, 120), (44, 160, 44), (152, 223, 138),
                                                                (214, 39, 40), (255, 152, 150), (148, 103, 189),
                                                                (197, 176, 213), (140, 86, 75), (196, 156, 148),
                                                                (227, 119, 194), (247, 182, 210), (127, 127, 127),
                                                                (199, 199, 199), (188, 189, 34), (219, 219, 141),
                                                                (23, 190, 207), (158, 218, 229)]]

    def __init__(self, parent):
        # Expensive Operation: get grind info
        self.grinders = account.load_json_data()

        self.gui = GUI.__init__(self, parent)
        # file menu
        parent.config(menu=self.add_file_menu(parent))

        # Vars to be accessed elsewhere in the instance.
        self.var_plot = tk.StringVar()
        self.var_year = tk.StringVar()
        self.var_gender = tk.StringVar()
        self.var_min = tk.StringVar()
        self.var_max = tk.StringVar()
        self.var_search = tk.StringVar()

        # UI Presentation SETUP
        # self.setup_ui_plot(self.var_plot, column=0)
        self.setup_ui_gender(self.var_gender, column=1)
        self.setup_ui_year(self.var_year, column=2)
        self.sbx_grinds_min = self.setup_ui_spin(self.var_min, text="Min:", default=10, row=0, column=3)
        self.sbx_grinds_max = self.setup_ui_spin(self.var_max, text="Max:", default=110, row=0, column=4)
        self.setup_ui_search(column=5)

        # listbox UI and contents
        self.info_columns = ["UUID", "Name", "Age", "Sex"]
        info = self._get_grinders_based_on_criteria()
        self.tree_info = self.create_treeview(self.bottom_frame, self.info_columns, info,
                                              column=0, row=0, weight=0, _scrollbar=True)
        self.tree_info.bind("<<TreeviewSelect>>", self.display_grinds_for_tree)

        # setup Traces - callbacks for what the spinners will do.
        self.var_min.trace("w", lambda x, y, z: self.populate_treeview(self.tree_info, self.info_columns,
                                                                       self._get_grinders_based_on_criteria()))
        self.var_max.trace("w", lambda x, y, z: self.populate_treeview(self.tree_info, self.info_columns,
                                                                       self._get_grinders_based_on_criteria()))
        self.var_search.trace("w", lambda x, y, z: self.populate_treeview(self.tree_info, self.info_columns,
                                                                          self._get_grinders_based_on_criteria()))

        self.headers = ["Date", "Start", "End", "Time"]
        self.tree_grind = self.create_treeview(self.bottom_frame, self.headers, [], column=2, row=0, weight=1)

        # plot
        self.figure = plt.figure(facecolor='white', frameon=True)  # , tight_layout=True)
        self.figure.subplots_adjust(bottom=0.35, left=0.05, right=0.8, top=0.9)

        self.axes = plt.axes()

        self.ax = self.figure.add_subplot(111)
        # Where did the data come from?

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

        self.dataplot.get_tk_widget().grid(columnspan=4, sticky='nesw')
        # self._update_plot([], label=None)
        # self.dataplot.show()
        self.annotations = []

        self.log("[info] Total # of accounts: {}".format(len(self.grinders)))

    # Setup UI
    # def setup_ui_plot(self, var_plot, column=0):
    #     var_plot.set('Bar')
    #     lbl_plot = tk.Label(self.mid_frame, text="Plot Type:", anchor='w')
    #     lbl_plot.grid(row=0, column=column, sticky='wnse')
    #     choices = ['Bar Buckets', 'Plot Attempts', 'Plot Dates']
    #     option = tk.OptionMenu(self.mid_frame, var_plot, *choices)
    #     option.config(width=7)
    #     option.grid(row=1, column=column, sticky='ns', pady=0, padx=0)
    #     var_plot.trace("w", lambda x, y, z: print(x, y, z))
    #

    def setup_ui_gender(self, var_gender, column=0):
        """
        Sets up a drop down list of options with a corresponding callback (trace) depending on what is chosen.
        -- Gender Setup
        :param var_gender: a tkinter string variable
        :param column: what column should the drop down box be placed into.
        :return:
        """
        var_gender.set('None')
        lbl_gender = tk.Label(self.mid_frame, text="Gender:", anchor='w')
        lbl_gender.grid(row=0, column=column, sticky='wnse')
        choices = ['None', 'All', 'Males', 'Females', 'Unknowns']
        option = tk.OptionMenu(self.mid_frame, var_gender, *choices)
        option.config(width=7)
        option.grid(row=1, column=column, sticky='ns', pady=0, padx=0)
        var_gender.trace("w", lambda x, y, z: self._plot_grinds_completed_by_gender(
            show_males=(var_gender.get() == "Males" or var_gender.get() == 'All'),
            show_females=(var_gender.get() == "Females" or var_gender.get() == 'All'),
            show_unknowns=(var_gender.get() == "Unknowns" or var_gender.get() == 'All')))

    def setup_ui_year(self, var_year, column=0):
        var_year.set("All Time")
        lbl_year = tk.Label(self.mid_frame, text="Year:", anchor='w')
        lbl_year.grid(row=0, column=column, sticky='wnse')

        # setup combobox
        collector = []
        for uuid, data in self.grinders.items():
            if data['grinds'] is not None:
                try:
                    collector += [item['date'].split("-")[0] for item in data['grinds']]
                except TypeError as e:
                    print(data['name'])
                    print(data)

        years = list(set(collector))
        years.sort()
        years.insert(0, 'All Time')

        ddl_years = tk.OptionMenu(self.mid_frame, var_year, *years)
        ddl_years.config(width=7)
        ddl_years.grid(row=1, column=column, sticky='ns', pady=0, padx=0)
        var_year.trace("w", lambda x, y, z: self.populate_treeview(
            self.tree_info,
            self.info_columns,
            self._get_grinders_based_on_criteria()))

    def setup_ui_spin(self, var_spin, text="notset", default=0, row=0, column=0):
        var_spin.set(default)
        lbl_spin = tk.Label(self.mid_frame, text=text, anchor='w')
        lbl_spin.grid(row=row, column=column, sticky='wnse')

        spin_box = tk.Spinbox(self.mid_frame, from_=0, to=4000, textvariable=var_spin, width=5)
        spin_box.grid(row=(row+1), column=column, sticky='ns', pady=0, padx=0)

        return spin_box

    def setup_ui_search(self, column=0):
        lbl_search = tk.Label(self.mid_frame, text="Search:", anchor='w')
        lbl_search.grid(row=0, column=column, columnspan=2, sticky='wnse')

        search = tk.Entry(self.mid_frame, textvariable=self.var_search, width=60)
        search.grid(row=1, column=5, sticky='ns', pady=0, padx=0)

    # Bar Charts
    def autolabel(self, rects):
        # attach some text labels
        total = sum([rect.get_height() for rect in rects])
        for rect in rects:
            height = rect.get_height()
            if height != 0 and total != 0:
                self.ax.text(rect.get_x()+rect.get_width()/2.,
                             1.05*height,
                             '{0:.1%}'.format(height/total),
                             ha='center', va='bottom')

    def _display_bar_graph(self, x, y, width=2, color=(1, 0, 0), edgecolor='none', yerr=None, autolabel=False):
        # where something falls along the x-axis
        # y-axis (Height of each bar)
        bars = self.ax.bar(x, y, width, color=color, edgecolor=edgecolor, yerr=yerr)
        if autolabel:
            self.autolabel(bars)

    # Plots
    def _plot_grinds_completed_by_gender(self, show_males=False, show_females=False, show_unknowns=False):
        self._clear_plots()

        females = []
        males = []
        unknowns = []

        # Collect and bucket the data
        filter = None if not self.var_year.get().isdigit() else self.var_year.get()
        for uuid, data in self.grinders.items():
            if data['grinds'] is not None:
                sex = data['age']
                grinds = len(data['grinds'])

                if filter is not None:
                    grinds = [item for item in data['grinds'] if filter in item['date']]
                    grinds = len(grinds)

                if sex is None:
                    unknowns.append(grinds)
                elif 'Male' in sex:
                    males.append(grinds)
                elif 'Female' in sex:
                    females.append(grinds)

        keys = list(range(0, 100, 5))
        y_males = []
        y_females = []
        y_unknowns = []
        for index, key in enumerate(keys):
            if index == len(keys)-1:
                y_males.append(len([y for y in males if y >= keys[index]]))
                y_females.append(len([y for y in females if y >= keys[index]]))
                y_unknowns.append(len([y for y in unknowns if y >= keys[index]]))
            else:
                y_males.append(len([y for y in males if keys[index] < y < keys[index + 1]]))
                y_females.append(len([y for y in females if keys[index] < y < keys[index + 1]]))
                y_unknowns.append(len([y for y in unknowns if keys[index] < y < keys[index + 1]]))

        gender = 'Gender'
        _width = 5
        showlabel = not (show_males is show_females is show_unknowns is True)

        if show_males:
            gender = 'Males'
            self._display_bar_graph(keys, y_males,
                                    width=_width,
                                    color=self.tableau20[0],
                                    edgecolor="black",
                                    autolabel=showlabel)

        if show_females:
            gender = 'Females'
            self._display_bar_graph(keys, y_females,
                                    width=_width,
                                    color=self.tableau20[13],
                                    edgecolor="black",
                                    autolabel=showlabel)

        if show_unknowns:
            gender = 'Unknown Gender'
            self._display_bar_graph(keys, y_unknowns,
                                    width=_width,
                                    color=self.tableau20[15],
                                    edgecolor="black",
                                    autolabel=showlabel)

        if showlabel is False:
            gender = "Males, Females, and Unknown gender"

        self.ax.set_title('Breakdown of Grinds Completed by {} ({})'.format(gender, self.var_year.get()))
        self.ax.set_xlabel('# of Attempts')
        self.ax.set_ylabel('# of People')
        self.ax.text(0, -0.45, "Data source: https://www.grousemountain.com/grind_stats",
                     transform=self.ax.transAxes,
                     fontsize=11)
        # self.ax.locator_params(nbins=25)
        # self.ax.set_xticklabels(keys)
        self.dataplot.show()
        self.log("[info]  Males: {} // Females: {} // Unknowns: {}".format(len(males),
                                                                           len(females),
                                                                           len(unknowns)))

    def _get_grinders_based_on_criteria(self):
        _min = 0 if self.sbx_grinds_min.get() == '' else int(self.sbx_grinds_min.get())
        _max = 0 if self.sbx_grinds_max.get() == '' else int(self.sbx_grinds_max.get())
        _search = self.var_search.get()
        _year = self.var_year.get()
        _sex = self.var_gender.get()

        try:
            info = [(uuid, data['name'], data['sex'], data['age']) for uuid, data in self.grinders.items()
                    if data['grinds'] is not None and _min <= len(data['grinds']) <= _max and
                    (_sex == 'All' or str(data['age']) in _sex) and  # age and sex are reversed :(
                    (_year == "All Time" or any(date['date'].startswith(_year) for date in data['grinds'])) and
                    _search.lower() in data['name'].lower()]
        except TypeError as e:
            print(e)
            info = []
        return info

    # Plot annotations
    def annotate_plot_points(self, point, x, y, label, axes, annotations):
        for index_x, index_y in zip(x, y):
            current = self.convert_seconds_to_timedelta(index_y)
            best = self.convert_seconds_to_timedelta(min(y))
            mean = self.convert_seconds_to_timedelta(np.mean(y))
            annotation = axes.annotate("{}\nCurrent: {}\nBest: {}\nMean:{}".format(label, current, best, mean),
                                       xy=(index_x, index_y), xycoords='data',
                                       xytext=(index_x + 0.02, index_y + 0.1), textcoords='data',
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

    # Time converters
    @staticmethod
    def convert_timedelta_to_seconds(_time, second_breakdown=60):
        hours, minutes, seconds = _time.split(":")
        return (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) / second_breakdown

    @staticmethod
    def convert_seconds_to_timedelta(_time):
        return str(datetime.timedelta(seconds=_time * 60))

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
        # filemenu.add_command(label="Show Bar Graph of Men & Women Grind Totals", command=self._plot_grinds_completed_by_gender)

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
        item_id = self.tree_info.focus()
        value = str(self.tree_info.item(item_id)['values'][0])

        uuid, name, sex, age, grinds = account.collect_grind_data(value)
        self.grinders[value]['sex'] = sex
        self.grinders[value]['age'] = age
        if self.grinders[value]['grinds'] is None:
            self.grinders[value]['grinds'] = list()

        for grind in grinds:
            if grind not in self.grinders[value]['grinds']:
                self.grinders[value]['grinds'].append(grind)

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

    # -- TreeView --------------------------------------------------------------------------
    def create_treeview(self, master, columns, rows, column=0, row=0, weight=0, _scrollbar=True):
        tree = ttk.Treeview(master, height=15, columns=columns, show="headings")

        _row_span = 1

        if _scrollbar:
            vsb = ttk.Scrollbar(orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            vsb.grid(column=column + 1, row=row, sticky='nsew', in_=master)
            _row_span = 2

        tree.grid(column=column, row=row, rowspan=_row_span, sticky='nsew', in_=master)

        master.grid_columnconfigure(column, weight=weight)
        master.grid_rowconfigure(row, weight=weight)

        self.populate_treeview(tree, columns, rows)

        return tree

    def populate_treeview(self, tree, columns, rows):
        for i in tree.get_children():
            tree.delete(i)

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: self.sortby(tree, c, 0))
            _width = 140 if col == "Name" else 100
            if col == 'Date' or col == 'Start' or col == 'End' or col == 'Time':
                _width = None
            tree.column(col, width=_width)

        for index, row in enumerate(rows):
            if index % 2 == 0:
                tree.insert('', 'end', values=row, tags=('odd',))
            else:
                tree.insert('', 'end', values=row, tags=('even',))

        tree.tag_configure('odd', background='#f0f0ff')

    @staticmethod
    def change_numeric(data):
        new_data = []
        if (data[0][0]).isdigit():
            for child, col in data:
                new_data.append((float(child), col))
            return new_data
        return data

    def sortby(self, tree, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data = self.change_numeric(data)

        # now sort the data in place
        data.sort(reverse=descending)

        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not descending)))

    def display_grinds_for_tree(self, event):
        item_id = self.tree_info.focus()
        value = str(self.tree_info.item(item_id)['values'][0])

        self.log("[info] Name: {} -- UUID: {} -- Grinds: {}".format(self.grinders[value]['name'],
                                                                    value,
                                                                    len(self.grinders[value]['grinds'])))

        grinds = self.grinders[value]['grinds']
        year = self.var_year.get()
        if grinds is not None:
            collector = [[grind['date'],
                          self.convert_standard_to_military_time(grind['start']),
                          self.convert_standard_to_military_time(grind['end']),
                          grind['time']] for grind in grinds if year == 'All Time' or grind['date'].startswith(year)]
            collector = sorted(collector, key=lambda x: x[0])
            self.populate_treeview(self.tree_grind, self.headers, collector)
            self._update_plot(collector, label=self.grinders[value]['name'])

    def _update_plot(self, data, label=None, legend=True):
        # find out if current plot line is setup for dates:
        if self.var_gender.get() in ["Males", "Females", "Unknowns", "All"]:
            current_ticks = self.ax.get_xticks().tolist()
            if 0.0 in current_ticks:
                self._clear_plots()

        dates = [date2num(datetime.datetime.strptime(grind[0], "%Y-%m-%d")) for grind in data]
        times = [self.convert_timedelta_to_seconds(grind[3]) for grind in data]

        if label is not None:
            if self.plot_attempts:
                dates = [x for x, y in enumerate(dates)]
                point, = self.ax.plot(dates, times, '.-', label=label, color=self.tableau20[random.randint(0, 19)])
            else:
                point, = self.ax.plot(dates, times, '.-', label=label, color=self.tableau20[random.randint(0, 19)])
                # self.ax.scatter(dates, times)

                # matplotlib date format object
                hfmt = matplotlib.dates.DateFormatter('%Y-%m-%d')
                items = self.ax.get_xticks().tolist()

                if int(items[0]) > 1:
                    self.ax.set_xticklabels([num2date(item) for item in items], rotation=42, fontsize=11)
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
        self.ax.text(0, -0.45, "Data source: https://www.grousemountain.com/grind_stats",
                     transform=self.ax.transAxes,
                     fontsize=11)
        self.dataplot.show()


def grouse_grind_app():
    """
    Loads up the UI for the program.
    """
    root = tk.Tk()
    root.title("Grouse Grind App 0.5")
    # root.geometry("1040x720")
    Grind(root)
    root.mainloop()


if __name__ == "__main__":
    grouse_grind_app()
