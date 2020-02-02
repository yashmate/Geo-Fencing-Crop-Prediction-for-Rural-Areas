import sqlite3
def get_survey_number():
    cases_dict=dict()
    conn=sqlite3.connect('agriculture.db')
    c=conn.cursor()
    c.execute('SELECT survey_no FROM land_records')
    data = c.fetchall()
    return data[-1][0]
print(get_survey_number())
