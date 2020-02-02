import sqlite3
def verify_from_database(username,password):
    users=dict()
    conn=sqlite3.connect('registration.db')
    c=conn.cursor()
    var=False
    c.execute('SELECT * FROM users')
    data=c.fetchall()
    for row in data:
        users[row[2]]=row[3]
    for key,value in users.items():
        if username == key and password == value:
            var=True
    if var == False:
        return 'Invalid Username or password'
    else:
        return 'Login Successful!'
print(verify_from_database('2017.yash.mate@ves.ac.in','1234abcd'))
        
