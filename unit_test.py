import unittest
import string
import random as rnd
import datetime as dt
import pandas as pd
import Db
import main as fe

data = pd.read_csv("Victoria.csv", parse_dates=["ACCIDENT_DATE"], sep=",")


class Mytest(unittest.TestCase):

    def test1(self):  # generateColors: n is string instead of integer
        n = "number"  # supposed to be number
        lst = []
        used_colors = []
        if type(n) != int: n = 0
        for e in range(n):
            new_color = False
            while not new_color:
                c = Db.getRandomRGB()
                if c in used_colors: continue
                lst.append(c)
                used_colors.append(c)
                new_color = True
        self.assertEqual([], lst)

    def test2(self):  # getNumberOfDays: date_from is later than date_to
        date_from = "2021-02-01"  # date
        date_to = "2020-05-23"  # date
        d_f = date_from.split("-")
        d_t = date_to.split("-")
        if len(d_f) == 1 or len(d_t) == 1:
            return_val = 0
        else:
            if int("".join(d_f)) >= int("".join(d_t)):
                return_val = 0
            else:
                a = dt.date(int(d_f[0]), int(d_f[1]), int(d_f[2]))
                b = dt.date(int(d_t[0]), int(d_t[1]), int(d_t[2]))
                return_val = (b - a).days
        self.assertEqual(0, return_val)

    def test3(self):  # getNumberOfDays: date format is wrong
        date_from = "2021/02/01"  # date
        date_to = "2020/05/23"  # date
        d_f = date_from.split("-")
        d_t = date_to.split("-")
        if len(d_f) == 1 or len(d_t) == 1:
            return_val = 0
        else:
            if int("".join(d_f)) >= int("".join(d_t)):
                return_val = 0
            else:
                a = dt.date(int(d_f[0]), int(d_f[1]), int(d_f[2]))
                b = dt.date(int(d_t[0]), int(d_t[1]), int(d_t[2]))
                return_val = (b - a).days
        self.assertEqual(0, return_val)

    def test4(self):  # queryTime: classification column name doesn’t exist
        try:
            q = {
                1: "2021-02-01",
                2: "2022-05-23",
                0: '@q[1] <= ACCIDENT_DATE <= @q[2]'}
            cols = ['ACCIDENT_DATE', 'ACCIDENT_TYPE', 'REGION_NAME', 'ALCOHOLTIME', 'ACCIDENT_TIME']
            condition = 'hello'
            classification = 'ACCIDENT_RANDOM'

            if classification not in cols and condition != '': cols.append(classification)
            d = data.query(q[0])[cols]
            if condition == '':
                pass  # return d
            else:
                d = d[d[classification].str.contains(pat=condition, na=False, case=False)]
        except Exception as e:
            print("ERROR!:", e)
            error_message = e
        self.assertEqual(KeyError, type(error_message))

    def test5(self):  # periodByAccident: show_all is an integer instead of boolean
        condition = ''
        classification = 'ACCIDENT_TYPE'
        show_all = 2
        if show_all:
            col_names = list(data.columns)
        else:
            col_names = ['ACCIDENT_DATE', 'ACCIDENT_TYPE', 'REGION_NAME', 'ALCOHOLTIME', 'ACCIDENT_TIME']
        d = Db.queryTime({
            1: "2021-02-01",
            2: "2022-05-23",
            0: '@q[1] <= ACCIDENT_DATE <= @q[2]'
        }, col_names, condition, classification)
        self.assertEqual(pd.DataFrame, type(d))

    def test6(self):  # getNumberOfAccidentsInHours: DataFrame is empty
        a = "2021-02-21"
        b = "2022-06-25"
        d = Db.queryTime({
            1: a,
            2: b,
            0: '@q[1] <= ACCIDENT_DATE <= @q[2]'
        }, ['ACCIDENT_TIME'], '', 'ACCIDENT_TYPE')
        reference = d['ACCIDENT_TIME'].to_dict()
        output = {}  # output dictionary
        num_days = Db.getNumberOfDays(a, b)
        for i in range(24): output[i] = 0  # initialization
        for row in reference: output[int(reference[row][:2])] += 1
        for e in output:
            output[e] = round(output[e] / num_days, 3)
        x = list(output.keys())
        y = list(output.values())
        self.assertEqual(dict, type(output))

    def test7(self):  # visualize:  value is a string instead of VisualizeChart class instance
        values = "Hello"
        if type(values) == list or type(values) == Db.VisualizeChart:
            pass
        else:
            e = "Error! Type list or VisualizeChart is expected!"
        self.assertEqual(str, type(e))

    def test8(self):  # getAccidentNumberOfAlcohol. The user-selected period does not have any matching information.
        try:
            a = "2019-08-15"
            b = "2019"
            d = Db.queryTime({
                1: a,
                2: b,
                0: '@q[1] <= ACCIDENT_DATE <= @q[2]'
            }, ['SEVERITY', 'ALCOHOLTIME'], '', 'ACCIDENT_TYPE')

            alcohol = sorted(d['ALCOHOLTIME'].values)
            severity = d.groupby(['SEVERITY', 'ALCOHOLTIME']).groups
            keys = [('Fatal accident', 'No'), ('Fatal accident', 'Yes'), ('Serious injury accident', 'No'),
                    ('Serious injury accident', 'Yes')]
            for k in keys:
                if k not in severity:
                    severity[k] = []
            output = {
                'Alcohol (A)': len(alcohol) - alcohol.index('Yes'),
                'Non-Alcohol (B)': alcohol.index('Yes'),
                'Serious A': len(severity['Serious injury accident', 'Yes']),
                'Serious B': len(severity['Serious injury accident', 'No']),
                'Fatal A': len(severity['Fatal accident', 'Yes']),
                'Fatal B': len(severity['Fatal accident', 'No'])
            }  # output dictionary
        except Exception as e:
            print("ERROR!:", e)
            error_message = e
        self.assertEqual(ValueError, type(error_message))

    def test9(self):  # button pressed, If there is no matching information with the keyword

        date_from = fe.format_date(dt.date(2019, 9, 2))
        date_to = fe.format_date(dt.date(2021, 9, 2))
        keyword = "awiudwaokijdwsaokijsaoijwa"
        classification = 'ACCIDENT_TYPE'
        fromCheck = int(date_from.replace('-', ''))
        toCheck = int(date_to.replace('-', ''))
        # Check if date to is behind date from
        if fromCheck >= toCheck:
            print("Error! Date to can't be behind date from")# fe.wx.MessageBox("date to can't be behind date from", "Checker")
        else:
            result = Db.VisualizeChart(
                values=Db.getNumberOfAccidentsInHours(date_from, date_to, keyword, classification),
                title="Average number of accidents in each hour of the day",
                xlabel="Each hour",
                ylabel="Average number of accidents",
                dtype='pie'
            )
            self.assertEqual(Db.VisualizeChart, type(result))

    def test10(self):  # buttonPressed, Pressing search button with no matching the keyword
        date_from = fe.format_date(dt.date(2019, 9, 2))
        date_to = fe.format_date(dt.date(2021, 9, 2))
        keyword = "awiudwaokijdwsaokijsaoijwa"
        classification = 'ACCIDENT_TYPE'
        fromCheck = int(date_from.replace('-', ''))
        toCheck = int(date_to.replace('-', ''))
        # Check if date to is behind date from
        if fromCheck >= toCheck:
            fe.wx.MessageBox("date to can't be behind date from", "Checker")
        # if Search
        show_all = False
        data = Db.periodByAccident(date_from, date_to, keyword, classification, show_all)
        self.assertEqual(True, data.empty)

    def test11(self):  #ButtonPressed, Visualize button pressed without selecting visualization option.
            date_from = fe.format_date(dt.date(2019, 9, 2))
            date_to = fe.format_date(dt.date(2021, 9, 2))
            keyword = "awiudwaokijdwsaokijsaoijwa"
            classification = 'ACCIDENT_TYPE'
            fromCheck = int(date_from.replace('-', ''))
            toCheck = int(date_to.replace('-', ''))
            # Check if date to is behind date from
            if fromCheck >= toCheck:
                print("Error! Date to can't be behind date from")
            else:
                user_selection = ''
                if user_selection == 'alcohol': pass
                elif user_selection in ['line', 'pie', 'bar']: pass
                else: error_message = "Please select the visualization option first!"
                self.assertEqual(str, type(error_message))


if __name__ == '__main__':
    unittest.main()


