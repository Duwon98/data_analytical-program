import wx
import wx.adv
import wx.grid
import pandas
import Db
from openpyxl.utils.cell import get_column_letter


def format_date(date):
    lis = [date.year, date.month + 1, date.day]
    for d in range(len(lis)):
        if lis[d] < 10:
            lis[d] = "0" + str(lis[d])
        else:
            lis[d] = str(lis[d])
    return str(lis[0] + "-" + lis[1] + "-" + lis[2])


class UI(wx.Frame):
    grid: wx.grid.Grid

    def __init__(self, parent, s_id, ttl, sz):
        super(UI, self).__init__(parent, s_id, title=ttl, size=sz,
                                 style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)  # call parent __init__
        self.size = sz  # size of the original frame
        self.parent = parent  # store parent
        self.panels = [wx.Panel(self)]  # set panel
        self.initialize()  # initialize
        self.current_dataframe = 0  # database

    def initialize(self):
        self.initialize_components()
        self.initialize_table()
        self.Show(True)  # show self

    def initialize_components(self):
        # TITLE TEXTS
        sizer = wx.BoxSizer(wx.VERTICAL)
        title_text1 = self.createText(label="VICTORIAN TRANSPORT DEPARTMENT", font_size=18, bold=True)
        title_text2 = self.createText(label="DATA ANALYTIC TOOL", font_size=22, bold=True)
        sizer.Add(title_text1, flag=wx.ALIGN_CENTER | wx.TOP, border=10)
        sizer.Add(title_text2, flag=wx.ALIGN_CENTER | wx.TOP, border=-3)
        self.panels[0].SetSizer(sizer)

        # Show all column flag
        show_cols_flag_text = self.createText(label="Show all columns", pos=(self.size[0] - 360, 105), font_size=8,
                                              bold=True)
        show_cols_flag = self.createCheckBox(label="", pos=(self.size[0] - 270, 100), size=(24, 24), id=1)

        # Classifications
        lst = list(Db.getCols())
        classification_text = self.createText(label="Classification", pos=(self.size[0] - 245, 105), font_size=8,
                                              bold=True)
        classification = self.createComboBox(choices=lst, pos=(self.size[0] - 175, 100),
                                             size=(135, 24), default='ACCIDENT_TYPE', id=11)  # classifications

        # Dates
        date_from_text = self.createText(label="Date From", pos=(self.size[0] - 596, 132), font_size=8,
                                         bold=True)  # text of date_from
        date_from = self.createDatePicker(pos=(self.size[0] - 539, 126), size=(135, 24), id=21)  # date_from
        date_to_text = self.createText(label="Date To", pos=(self.size[0] - 402, 132), font_size=8, bold=True)
        date_to = self.createDatePicker(pos=(self.size[0] - 360, 126), size=(135, 24), id=22)  # date_to

        # Keywords
        keyword_text = self.createText(label="Keyword", pos=(self.size[0] - 223, 130), font_size=8, bold=True)
        keyword = self.createTextCtrl(pos=(self.size[0] - 175, 126), size=(135, 24), id=31)  # keyword

        # Visualization Options
        vo_text = self.createText(label="Visualization Options", pos=(self.size[0] - 596, 157), font_size=8, bold=True)
        vo_pie = self.createRadioButton(label="Pie", pos=(self.size[0] - 470, 157), font_size=8, bold=True, id=41)
        vo_bar = self.createRadioButton(label="Bar", pos=(self.size[0] - 430, 157), font_size=8, bold=True, id=42)
        vo_line = self.createRadioButton(label="Line", pos=(self.size[0] - 390, 157), font_size=8, bold=True, id=43)
        vo_alcohol = self.createRadioButton(label="Alcohol", pos=(self.size[0] - 345, 157), font_size=8, bold=True,
                                            id=44)
        # vo_histogram = self.createRadioButton(label="Histogram", pos=(self.size[0] - 346, 157), font_size=8, bold=True)

        # Buttons
        btn_reset = self.createButton(label="Reset", pos=(self.size[0] - 230, 152), size=(70, 24),
                                      func=self.ButtonReset, id=51)
        btn_visualize = self.createButton(label="Visualize", pos=(self.size[0] - 160, 152), size=(70, 24),
                                          func=self.ButtonPressed, id=52)
        btn_search = self.createButton(label="Search", pos=(self.size[0] - 90, 152), size=(70, 24),
                                       func=self.ButtonPressed, id=53)

    def ButtonPressed(self, e):
        date_from = format_date(self.FindWindowById(21).GetValue())
        date_to = format_date(self.FindWindowById(22).GetValue())
        keyword = str(self.FindWindowById(31).GetValue())
        classification = str(self.FindWindowById(11).GetValue())
        fromCheck = int(date_from.replace('-', ''))
        toCheck = int(date_to.replace('-', ''))
        # Check if date to is behind date from
        if fromCheck >= toCheck:
            wx.MessageBox("date to can't be behind date from", "Checker")
        else:
            # if Search
            if e.GetId() == 53:
                if self.FindWindowById(1).GetValue():
                    show_all = True
                else:
                    show_all = False
                data = Db.periodByAccident(date_from, date_to, keyword, classification, show_all)
                if data.empty:
                    wx.MessageBox("No Matching Information", "Checker")
                else:
                    self.create_table(data)
            # if Visualize
            elif e.GetId() == 52:
                user_selection = ''
                if self.FindWindowById(41).GetValue():
                    user_selection = 'pie'
                elif self.FindWindowById(42).GetValue():
                    user_selection = 'bar'
                elif self.FindWindowById(43).GetValue():
                    user_selection = 'line'
                elif self.FindWindowById(44).GetValue():
                    user_selection = 'alcohol'
                if user_selection == 'alcohol':
                    anoa = Db.getAccidentNumberOfAlcohol(date_from, date_to, keyword, classification)
                    Db.visualize(
                        [
                            Db.VisualizeChart(
                                values=(list(anoa.keys())[:2], list(anoa.values())[:2]),
                                title="Number of accidents by alcohol",
                                dtype='pie',
                                colors=['#ffaaaa', '#aaaaff']
                            ),
                            Db.VisualizeChart(
                                values=(list(anoa.keys())[2:], list(anoa.values())[2:]),
                                title="Number of accidents by alcohol / severity of injury",
                                dtype='bar',
                                colors=['#ffaaaa', '#aaaaff', '#ffaaaa', '#aaaaff']
                            )
                        ]
                    )
                elif user_selection in ['pie', 'bar', 'line']:
                    Db.visualize(Db.VisualizeChart(
                        values=Db.getNumberOfAccidentsInHours(date_from, date_to, keyword, classification),
                        title="Average number of accidents in each hour of the day",
                        xlabel="Each hour",
                        ylabel="Average number of accidents",
                        dtype=user_selection
                    ))
                else:
                    wx.MessageBox("Please select the visualization option first!")

    def ButtonReset(self, e):
        self.initialize_table(row=100, col=20)

    def create_table(self, data):
        # data initializations
        data_dict = data.to_dict()  # gets the dictionary version of the dataframe
        max_cols, col_names = len(data_dict), list(data_dict.keys())  # gets the maximum column num + column names
        max_rows = len(data_dict[col_names[0]])  # gets the maximum row num

        # clear
        change = self.initialize_table(row=max_rows, col=max_cols)

        for c in range(max_cols):
            self.grid.SetColLabelValue(c, col_names[c])
            self.grid.SetColSize(c, 250)
            for r in range(max_rows):
                if change: self.grid.SetCellRenderer(r, c, wx.grid.GridCellStringRenderer())
                row_lis = list(data_dict[col_names[c]].keys())
                d = data_dict[col_names[c]][row_lis[r]]
                if type(d) == pandas._libs.tslibs.timestamps.Timestamp:
                    d = str(d.day) + "/" + str(d.month) + "/" + str(d.year)
                elif col_names[c] == 'ACCIDENT_TIME':
                    d = d.replace('.', ':')
                self.grid.SetCellValue(r, c, str(d))

    grid_row = 100
    grid_col = 20

    def initialize_table(self, row: int = 0, col: int = 0):
        if row == 0: row = self.grid_row
        if col == 0: col = self.grid_col
        if len(self.panels) < 2:
            self.createPanel(pos=(0, 180), size=(self.size[0], self.size[1] - 180))
            static_box = wx.StaticBox(self.panels[1], wx.ID_ANY, 'Table will appear below',
                                      size=(self.size[0] - 10, self.size[1] - 220))
            static_sizer = wx.StaticBoxSizer(static_box, wx.HORIZONTAL)
            # TABLE
            self.grid = wx.grid.Grid(self.panels[1], 10, pos=(5, 15), size=(self.size[0] - 25, self.size[1] - 233))
            self.grid.CreateGrid(row, col)  # 100 rows / 10 columns
            for c in range(col):
                self.grid.SetColSize(c, 100)
            static_sizer.Add(self.grid)
            self.panels[1].SetSizer(static_sizer)
        else:
            increased = False
            self.grid.ClearGrid()
            if self.grid_row != row or self.grid_col != col:
                # change rows if different
                r_gap, c_gap = self.grid_row - row, self.grid_col - col
                if r_gap > 0:
                    self.grid.DeleteRows(pos=row, numRows=abs(r_gap))
                elif r_gap < 0:
                    self.grid.AppendRows(abs(r_gap));
                    increased = True
                # change cols if different
                if c_gap > 0:
                    self.grid.DeleteCols(pos=col, numCols=abs(c_gap))
                elif c_gap < 0:
                    self.grid.AppendCols(abs(c_gap));
                    increased = True
                self.grid_row, self.grid_col = row, col
            # reset size and label + render
            for c in range(col):
                self.grid.SetColSize(c, 100)
                self.grid.SetColLabelValue(c, get_column_letter(c + 1))
            if increased:
                return True
            else:
                return False
        pass

    def createCheckBox(self, parent=None, id=wx.ID_ANY, label='Check Box', pos=(0, 0), size=(-1, -1),
                       style=wx.CHK_3STATE):
        if parent is None: parent = self.panels[0]
        return wx.CheckBox(parent, id=id, label=label, pos=pos, size=size, style=style)

    def createComboBox(self, parent=None, default='Please Select', choices=('Default', 'None'), style=wx.CB_READONLY,
                       id=wx.ID_ANY, pos=(0, 0), size=(120, -1)):
        if parent is None: parent = self.panels[0]
        return wx.ComboBox(parent, id, default, choices=choices, style=style, pos=pos, size=size)

    def createRadioButton(self, parent=None, id=wx.ID_ANY, label="Radio Button", pos=(0, 0), size=(-1, 14), font_size=8,
                          bold=False):
        if parent is None: parent = self.panels[0]
        radio_btn = wx.RadioButton(parent, id=id, label=label, pos=pos, size=size)
        font = radio_btn.GetFont()  # get font
        font.PointSize = font_size  # set font size
        if bold: font = font.Bold()
        radio_btn.SetFont(font)
        return radio_btn

    def createDatePicker(self, parent=None, id=wx.ID_ANY, size=(120, -1), pos=(0, 0), style=wx.adv.DP_DROPDOWN):
        if parent is None: parent = self.panels[0]
        return wx.adv.DatePickerCtrl(parent, id=id, size=size, pos=pos, style=style)

    def createTextCtrl(self, parent=None, id=wx.ID_ANY, style=None, size=(120, -1), pos=(0, 0)):
        if parent is None: parent = self.panels[0]
        return wx.TextCtrl(parent, pos=pos, size=size, id=id)

    def createPanel(self, parent=None, pos=None, size=None):
        if parent is None: parent = self.panels[0]
        if pos is None and size is None:
            self.panels.append(wx.Panel(parent))
        elif pos is None:
            self.panels.append(wx.Panel(parent, size=size))
        elif size is None:
            self.panels.append(wx.Panel(parent, pos=pos))
        else:
            self.panels.append(wx.Panel(parent, pos=pos, size=size))

    def setBackgroundColour(self, colour, panel=0):
        self.panels[panel].SetBackgroundColour(colour)

    def createText(self, parent=None, font_size=12, bold=False, label="", pos=(0, 0)):
        if parent is None: parent = self.panels[0]
        text = wx.StaticText(parent, label=label, pos=pos)
        font = text.GetFont()  # get font
        font.PointSize = font_size  # set font size
        if bold: font = font.Bold()
        text.SetFont(font)
        return text

    def createButton(self, label="", pos=(0, 0), size=(120, -1), func=None, parent=None, id=wx.ID_ANY):
        if parent is None: parent = self.panels[0]
        button = wx.Button(parent, id=id, pos=pos, size=size, label=label)
        if func is not None: self.Bind(wx.EVT_BUTTON, func, button)
        return button


if __name__ == "__main__":
    app = wx.App()
    frame = UI(None, -1, ' ', (1400, 800))
    frame.Show()
    app.MainLoop()
