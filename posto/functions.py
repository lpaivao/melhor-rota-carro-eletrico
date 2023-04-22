import datetime


def format_time():
    t = datetime.datetime.now()
    s = t.strftime('%d-%m-%Y %H:%M:%S%f')
    return s[:-6]
