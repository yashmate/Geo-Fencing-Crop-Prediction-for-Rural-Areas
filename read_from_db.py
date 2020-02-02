import sqlite3
def read_from_db():
    cases_dict=dict()
    conn=sqlite3.connect('agriculture.db')
    c=conn.cursor()
    c.execute('SELECT survey_no,name,area,district,phone FROM land_records')
    data = c.fetchall()
    return data
print(read_from_db())
