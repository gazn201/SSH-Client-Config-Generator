import sqlite3

conn = sqlite3.connect('ssh-conf.db')
cursor = conn.cursor()

def updaete_field(field, value, id):
    cursor.execute(f"UPDATE Hosts SET {field} = ? WHERE ID = ?", (value, id))