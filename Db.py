import matplotlib.pylab as plt
import pandas as pd
import datetime as dt
import random as rnd
from wx import MessageBox
from numpy import ndarray

data = pd.read_csv("Victoria.csv", parse_dates=["ACCIDENT_DATE"], sep=",")
xValue = []


def getCols():
    return data.columns


def generateColors(n):
    lst = []
    used_colors = []
    if type(n) != int: n = 0
    for e in range(n):
        new_color = False
        while not new_color:
            c = getRandomRGB()
            if c in used_colors: continue
            lst.append(c)
            used_colors.append(c)
            new_color = True
    return lst


def getRandomRGB():
    rgb_values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    rgb = [
        rgb_values[int(rnd.random() * 15)] + rgb_values[int(rnd.random() * 15)]
        for i in range(3)
    ]
    return '#{}{}{}'.format(rgb[0], rgb[1], rgb[2])


def getNumberOfDays(date_from, date_to):
    try:
        d_f = date_from.split("-")
        d_t = date_to.split("-")
        if int("".join(d_f)) >= int("".join(d_t)):
            return 0
        else:
            a = dt.date(int(d_f[0]), int(d_f[1]), int(d_f[2]))
            b = dt.date(int(d_t[0]), int(d_t[1]), int(d_t[2]))
            return (b - a).days
    except Exception as e:
        print("ERROR:", e)
        return 0


def periodByAccident(a, b, condition='', classification='ACCIDENT_TYPE', show_all=False):
    if show_all:
        col_names = list(data.columns)
    else:
        col_names = ['ACCIDENT_DATE', 'ACCIDENT_TYPE', 'REGION_NAME', 'ALCOHOLTIME', 'ACCIDENT_TIME']
    d = queryTime({
        1: a,
        2: b,
        0: '@q[1] <= ACCIDENT_DATE <= @q[2]'
    }, col_names, condition, classification)
    return d


def queryTime(q, cols, condition='', classification='ACCIDENT_TYPE'):
    try:
        if classification not in cols and condition != '': cols.append(classification)
        d = data.query(q[0])[cols]
        if condition == '':
            return d
        else:
            return d[d[classification].str.contains(pat=condition, na=False, case=False)]
    except Exception as e:
        print("ERROR!:", e)
        return pd.DataFrame()


def getNumberOfAccidentsInHours(a, b, condition='', classification='ACCIDENT_TYPE'):
    try:
        d = queryTime({
            1: a,
            2: b,
            0: '@q[1] <= ACCIDENT_DATE <= @q[2]'
        }, ['ACCIDENT_TIME'], condition, classification)
        reference = d['ACCIDENT_TIME'].to_dict()
        output = {}  # output dictionary
        num_days = getNumberOfDays(a, b)
        for i in range(24): output[i] = 0  # initialization
        for row in reference: output[int(reference[row][:2])] += 1
        for e in output:
            output[e] = round(output[e] / num_days, 3)
        x = list(output.keys())
        y = list(output.values())
        return x, y
    except Exception as e:
        print("ERROR!:", e)
        return [], []


class VisualizeChart:
    def __init__(self, values, title: str = '', xlabel: str = '', ylabel: str = '', dtype: str = 'bar', colors=None):
        self.values = values
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.dtype = dtype
        if colors is None:
            if dtype == 'line':
                self.colors = getRandomRGB()
            else:
                self.colors = generateColors(len(values[1]))
        else:
            if type(colors) == list and dtype == 'line':
                self.colors = colors[0]
            else:
                self.colors = colors

    def run(self):
        do_not_show = False
        if self.dtype == 'bar':
            plt.bar(self.values[0], self.values[1], color=self.colors)
        elif self.dtype == 'line':
            plt.plot(self.values[0], self.values[1], color=self.colors)
        elif self.dtype == 'pie':
            plt.pie(self.values[1], labels=self.values[0], autopct='%1.1f%%', shadow=True, startangle=90,
                    colors=self.colors, normalize=True)
            plt.axis('equal')
        else:
            MessageBox("Please input a valid visualization option!"); do_not_show = True
        if not do_not_show:
            if self.title != '': plt.title(self.title)
            if self.xlabel != '': plt.xlabel(self.xlabel)
            if self.ylabel != '': plt.ylabel(self.ylabel)


def visualize(values):
    if type(values) == list or type(values) == VisualizeChart:
        plt.close()
        plt.figure(figsize=(10.0, 6.0))
        if type(values) == list:
            for i in range(1, len(values) + 1):
                if type(values[i - 1]) == VisualizeChart:
                    if len(values) > 1:
                        plt.subplot(1, len(values), i)
                    values[i - 1].run()
        else:
            values.run()
        plt.show()
    else:
        MessageBox("Please provide correct class!")


def getAccidentNumberOfAlcohol(a, b, condition='', classification='ACCIDENT_TYPE'):
    try:
        d = queryTime({
            1: a,
            2: b,
            0: '@q[1] <= ACCIDENT_DATE <= @q[2]'
        }, ['SEVERITY', 'ALCOHOLTIME'], condition, classification)

        alcohol = sorted(d['ALCOHOLTIME'].values)
        severity = d.groupby(['SEVERITY', 'ALCOHOLTIME']).groups
        keys = [('Fatal accident', 'No'), ('Fatal accident', 'Yes'), ('Serious injury accident', 'No'),
                ('Serious injury accident', 'Yes')]
        for k in keys:
            if k not in severity:
                severity[k] = ndarray(0)
        output = {
            'Alcohol (A)': len(alcohol) - alcohol.index('Yes'),
            'Non-Alcohol (B)': alcohol.index('Yes'),
            'Serious A': len(severity['Serious injury accident', 'Yes']),
            'Serious B': len(severity['Serious injury accident', 'No']),
            'Fatal A': len(severity['Fatal accident', 'Yes']),
            'Fatal B': len(severity['Fatal accident', 'No'])
        }  # output dictionary
    except Exception as e:
        MessageBox(e)
        output = {
            'Alcohol (A)': 0,
            'Non-Alcohol (B)': 0,
            'Serious A': 0,
            'Serious B': 0,
            'Fatal A': 0,
            'Fatal B': 0
        }
    return output
