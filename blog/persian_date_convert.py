from persiantools.jdatetime import JalaliDate, JalaliDateTime

months_dict = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند"
}

persian_to_english = {
    '۰': '0',
    '۱': '1',
    '۲': '2',
    '۳': '3',
    '۴': '4',
    '۵': '5',
    '۶': '6',
    '۷': '7',
    '۸': '8',
    '۹': '9'
}


def convert_date(date):
    time = str(JalaliDate.to_jalali(date)).split("-")
    month = months_dict[int(time[1])]
    persian_date = f"{time[2]} {month} {time[0]}"
    return persian_date


def convert_date_time(date_time):
    date_time_obj = str(JalaliDateTime.to_jalali(date_time)).split(" ")[0].split("-")
    month = months_dict[int(date_time_obj[1])]
    persian_time = f"{date_time_obj[2]}  {month} {date_time_obj[0]}"
    return persian_time


def convert_date_persian_numbers(date):
    time = str(JalaliDate.to_jalali(date)).split("-")
    month = months_dict[int(time[1])]
    year = ""
    for i in time[0]:
        for key, val in persian_to_english.items():
            if i == val:
                year += key
    day = ""
    for index,i in enumerate(time[2]):
        if index == 0 and i == "0":
                pass
        else:
            for key,val in persian_to_english.items():
                if i == val:
                    day += key

    persian_date = f"{day} {month} {year}"
    return persian_date