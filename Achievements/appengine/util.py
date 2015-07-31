from datetime import date

def date2String(date):
    return date.strftime('%m/%d/%Y')

def string2Date(string):
    string = string.replace('-', '/')
    strings = string.split('/')
    return date(int(strings[2]),int(strings[0]),int(strings[1]))
