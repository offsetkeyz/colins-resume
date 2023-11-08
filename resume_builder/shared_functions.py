from datetime import datetime

def get_year(date):
    if date == 'Present':
        return date
    return datetime.strptime(date, '%Y-%m-%d').strftime('%Y')

def get_month_and_year(date):
    if date == 'Present':
        return date
    return datetime.strptime(date, '%Y-%m-%d').strftime('%b %Y')