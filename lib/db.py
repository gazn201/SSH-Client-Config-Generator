import sqlite3

conn = sqlite3.connect('ssh-conf.db')
cursor = conn.cursor()

def update_field_hosts(field, value, id):
    cursor.execute(f"UPDATE Hosts SET {field} = ? WHERE ID = ?", (value, id))
def update_field_additional(id, additional):
    cursor.execute(f"UPDATE ADDITIONALPARAMS SET PARAMETR = ?, VALUE = ? WHERE ID = ?", (additional[0], additional[1], id))
def insert_additioanl(id, additional):
    print(f"{additional}")
    cursor.execute("INSERT INTO ADDITIONALPARAMS (ID, PARAMETR, VALUE) VALUES (?, ?, ?)", (id, additional[1], additional[2]))