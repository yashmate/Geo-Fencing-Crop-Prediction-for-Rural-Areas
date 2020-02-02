import sqlite3
def write_to_register(fname,lname,email,passw,addr,desg,con): 
    conn = sqlite3.connect('registration.db')
    c = conn.cursor()
    c.execute("INSERT INTO users(firstname, lastname, email, pass,address,designation,contact) VALUES (?, ?, ?, ?, ?, ?, ?)",
          (fname, lname, email, passw,addr,desg,con))

    conn.commit()
    c.close()
    conn.close()
write_to_register('Jim','Carrey','jimcarrey@gmail.com','jim@123','Beverely Hills','Actor','88761243')
