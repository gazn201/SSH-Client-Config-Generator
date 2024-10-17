import sqlite3
import sys
import ipaddress
import readline
import os
from lib.db import *


def complete_path(text, state):
    line = readline.get_line_buffer()
    path = os.path.expanduser(text)
    if os.path.isdir(path):
        files = os.listdir(path)
        matches = [os.path.join(path, f) + '/' if os.path.isdir(os.path.join(path, f)) else os.path.join(path, f) for f in files]
    else:
        dirname, basename = os.path.split(path)
        if not dirname:
            dirname = "."
        try:
            files = os.listdir(dirname)
        except FileNotFoundError:
            files = []
        matches = [os.path.join(dirname, f) for f in files if f.startswith(basename)]
    return matches[state] if state < len(matches) else None


def input_with_completion(prompt):
    readline.set_completer(complete_path)
    readline.set_completer_delims('')
    readline.parse_and_bind("bind ^I rl_complete")
    return input(prompt)


#Hostaname
def get_hostname():
    hostname = input(f"Enter hostname: ")
    query_hostname = "SELECT HOSTNAME FROM Hosts WHERE HOSTNAME = ?"
    cursor.execute(query_hostname, (hostname,))
    result = cursor.fetchone()
    if result:
        sys.exit(f"Hostname {result} already exist!")
    else:
        return hostname


#IP Address
def valid_address():
    address = input(f"Enter IP address: ")
    try:
        ip = ipaddress.ip_address(address)
        return address
    except ValueError:
        print(f"IP address not valid!")
        sys.exit(2)


def get_address():
    while True:
        print(f"IP address or Domain? (Default IP address)\n[1] IP Address\n[2] Domain")
        x = input(f"Choose an option: ")
        if x == '1' or x == '':
            address = valid_address()
            return address
        elif x == '2':
            domain = input(f"Enter domain: ")
            address = domain
            return address
        else:
            print(f"Incorrect input, try again.")



#USERNAME
def get_username():
    username = input(f"Enter username: ")
    return username


#PORT
def get_port():
    while True:
        choice = input(f"Using default port? [Y/n]")
        if choice.lower() == 'y' or choice == '':
            port = '22'
            return port
        elif choice.lower() == 'n':
            port = input(f"Enter port: ")
            return port
        else:
            print(f"Incorrect input, try again.")


#KEY
def list_keys():
    cursor.execute("SELECT KEYID, KEYNAME FROM KEYS")
    rows = cursor.fetchall()
    for row in rows:
        print(f"[{row[0]}] {row[1]}")

def get_keypath_by_id(record_id):
    cursor.execute("SELECT KEYPATH FROM KEYS WHERE KEYID = ?", (record_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        print(f"{record_id} not found.")
        return None


def key_definition():
    while True:
        key_choice = input(f"Key ID (l for list, a for add new key): ")
        if key_choice.isdigit():
            record_id = int(key_choice)
            path = get_keypath_by_id(record_id)
            if path:
                key = record_id
                return key
            break
        elif key_choice == 'l':
            list_keys()
        elif key_choice == 'a':
            addNewKey()
        else:
            print(f"Incorrect input, try again.")


def get_additional():
    while True:
        i = input(f"Do you want to add additional parameters? [y/N]: ")
        if i.lower() == 'y':
            additional = True
            parametr = input(f"Enter additional parametr: ")
            value = input(f"Enter value: ")
            return additional, parametr, value
        elif i.lower() == 'n' or i == '':
            additional = False
            return [additional]
        else:
            print(f"Incorrect input, try again.")

def createBaseConfig(*args, **kwargs):
    hostname = get_hostname()
    address = get_address()
    username = get_username()
    port = get_port()
    key = key_definition()
    additional = get_additional()
    print(f"\n")
    print(f"Hostname = {hostname}")
    print(f"Address = {address}")
    print(f"Username = {username}")
    print(f"Port = {port}")
    print(f"Key = {key}")
    if additional[0]:
        print(f"Parametr = {additional[1]}")
        print(f"Value = {additional[2]}")
    else:
        pass
    choice = input(f"\nIs config correct? [Y/n]")
    if choice.lower() == 'y' or choice == '':
        cursor.execute("SELECT MAX(ID) FROM Hosts")
        last_id = cursor.fetchone()[0]
        new_id = (last_id + 1) if last_id else 1
        cursor.execute("INSERT INTO Hosts (ID, HOSTNAME, ADDRESS, USERNAME, KEY, PORT) VALUES (?, ?, ?, ?, ?, ?)", (new_id, hostname, address, username, key, port))
        if additional[0]:
            cursor.execute("INSERT INTO ADDITIONALPARAMS (ID, PARAMETR, VALUE) VALUES (?, ?, ?)", (new_id, additional[1], additional[2]))
        else:
            pass
        conn.commit()
    elif choice.lower() == 'n':
        sys.exit(0)
    else:
        print(f"Incorrect input, try again.")


def generateSSHConfig():
    cursor.execute("SELECT ID, HOSTNAME, ADDRESS, USERNAME, KEY, PORT FROM Hosts")
    rows = cursor.fetchall()
    with open('config', 'w') as file:
        for row in rows:
            id, hostname, address, user, key, port = row
            cursor.execute("SELECT KEYPATH FROM KEYS WHERE KEYID = ?", (key,))
            keypath = cursor.fetchone()
            file.write(f"Host {hostname}\n")
            file.write(f"\tHostName {address}\n")
            file.write(f"\tUser {user}\n")
            file.write(f"\tPort {port}\n")
            file.write(f"\tIdentityFile {keypath[0]}")
            file.write(f"\n")


def addNewKey():
    keypath = input_with_completion(f"Enter path: ")
    keyname = input(f"Enter visible name for key: ")
    cursor.execute("SELECT MAX(KEYID) FROM KEYS")
    last_id = cursor.fetchone()[0]
    new_id = (last_id + 1) if last_id else 1
    cursor.execute("INSERT INTO KEYS (KEYID, KEYNAME, KEYPATH) VALUES (?, ?, ?)", (new_id, keyname, keypath))
    conn.commit()
    print(f"Key have been added: [{new_id}] {keyname}")
