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

def check_input(prompt):
    user_input = input(prompt).strip()
    if user_input:
        return user_input
    else:
        print(f"String is empty!")
        return None

#Hostaname
def get_hostname():
    while True:
        hostname = check_input(f"Enter hostname: ")
        if hostname:
            query_hostname = "SELECT HOSTNAME FROM Hosts WHERE HOSTNAME = ?"
            cursor.execute(query_hostname, (hostname,))
            result = cursor.fetchone()
            if result:
                print(f"Hostname {result[0]} already exist!")
            else:
                return hostname
        else:
            pass

#IP Address
def valid_address():
    while True:
        address = input(f"Enter IP address: ")
        try:
            ip = ipaddress.ip_address(address)
            return address
        except ValueError:
            print(f"IP address not valid!")

def get_address():
    while True:
        print(f"IP address or Domain? (Default IP address)\n[1] IP Address\n[2] Domain")
        x = input(f"Choose an option: ")
        if x == '1' or x == '':
            address = valid_address()
            return address
        elif x == '2':
            domain = check_input(f"Enter domain: ")
            if domain:
                address = domain
                return address
            else:
                pass
        else:
            print(f"Incorrect input, try again.")



#USERNAME
def get_username():
    while True:
        username = check_input(f"Enter username: ")
        if username:
            return username
        else:
            pass

#PORT
def get_port():
    while True:
        choice = input(f"Using default port? [Y/n]: ")
        if choice.lower() == 'y' or choice == '':
            port = '22'
            return port
        elif choice.lower() == 'n':
            while True:
                port = check_input(f"Enter port: ")
                if port:
                    return port
                else:
                    pass
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

def define_additional():
    while True:
        i = input(f"Do you want to add additional parameters? [y/N]: ")
        if i.lower() == 'y':
            additional = True
            while True:
                parametr = check_input(f"Enter additional parametr: ")
                if parametr:
                    break
                else:
                    pass
            value = input(f"Enter value: ")
            return additional, parametr, value
        elif i.lower() == 'n' or i == '':
            additional = False
            return [additional]
        else:
            print(f"Incorrect input, try again.")

def edit_additional(id):
    while True:
        parametr = check_input(f"Enter additional parametr: ")
        if parametr:
            break
        else:
            pass
    value = input(f"Enter value: ")
    cursor.execute("SELECT PARAMETR FROM ADDITIONALPARAMS WHERE ID = ?", (id,))
    additional_parametr = cursor.fetchone()
    if additional_parametr:
        additional = [parametr, value]
        update_field_additional(id, additional)
    else:
        additional = [True, parametr, value]
        insert_additioanl(id, additional)

def createBaseConfig(*args, **kwargs):
    hostname = get_hostname()
    address = get_address()
    username = get_username()
    port = get_port()
    key = key_definition()
    additional = define_additional()
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
            insert_additioanl(new_id, additional)
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


def searchHosts(arg):
    searchObject = f"%{arg}%"
    cursor.execute("SELECT ID, HOSTNAME, ADDRESS FROM Hosts WHERE HOSTNAME OR ADDRESS LIKE ?", (searchObject,))
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            id, hostname, address = row
            print(f"ID {id} ;; Hostname {hostname} ;; Address {address}")
    else:
        print(f"No matches found")


def parse_values(value_str):
    values = []
    HostIDs = value_str.split(',')
    for part in HostIDs:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            start, end = int(start), int(end)
            values.extend(range(start, end + 1))
        else:
            values.append(int(part))
    return values
def deleteHosts(arg):
    value_str = arg
    hostIDs = parse_values(value_str)
    success_count = 0
    unsuccess_count = 0
    id_found = []
    id_not_found = []
    for host in hostIDs:
        cursor.execute("SELECT ID FROM Hosts WHERE ID = ?", (host,))
        id = cursor.fetchone()
        if id:
            id_found.append(host)
            success_count += 1
        else:
            id_not_found.append(host)
            unsuccess_count += 1
    for host in id_not_found:
        print(f"{host} can't be removed. Not found!")
    print(f"\n")
    for host in id_found:
        cursor.execute("SELECT HOSTNAME FROM Hosts WHERE ID = ?", (host,))
        hostname = cursor.fetchone()
        print(f"ID: {host} ;; Hostname {hostname[0]} can be deleted!")
    print(f"\n")
    while True:
        i = input(f"Remove {success_count} hosts? [yes/no]: ")
        if i.lower() == 'yes':
            for host in id_found:
                cursor.execute("DELETE FROM Hosts where ID = ?", (host,))
                cursor.execute("SELECT ID FROM ADDITIONALPARAMS WHERE ID = ?", (host,))
                additional_id = cursor.fetchone()
                if additional_id:
                    cursor.execute("DELETE FROM ADDITIONALPARAMS WHERE ID = ?", (host,))
                else:
                    pass
            break
        elif i.lower() == 'no':
            sys.exit(f"Operation was canceled.")
        else:
            print(f"Incorrect input, try again.")
    conn.commit()
    print(f"{success_count} was successfully removed / {unsuccess_count} was not removed.")

def is_integer(int_value):
    try:
        int(int_value)
        return True
    except ValueError:
        return False


def editHosts(arg, *args, **kwargs):
    int_value = arg
    id = arg
    if is_integer(int_value):
        cursor.execute("SELECT ID, HOSTNAME, ADDRESS, USERNAME, KEY, PORT FROM Hosts WHERE ID = ?", (id,))
        config = cursor.fetchone()
        if config:
            id, hostname, address, username, keyid, port = config
            cursor.execute("SELECT KEYNAME FROM KEYS WHERE KEYID = ?", (keyid,))
            key = cursor.fetchone()
            cursor.execute("SELECT PARAMETR, VALUE FROM ADDITIONALPARAMS WHERE ID = ?", (id,))
            additional = cursor.fetchone()
            print(f"\nID: {id}\nHostname: {hostname}\nAddress: {address}\nUsername: {username}\nKey: {key[0]}\nPort: {port}")
            if additional:
                print(f"Parametr = {additional[0]}")
                if additional[1]:
                    print(f"Value = {additional[1]}\n")
            print(f"What do you want to edit?")
            options = {
                'h': lambda: update_field_hosts('HOSTNAME', get_hostname(), id),
                'a': lambda: update_field_hosts('ADDRESS', get_address(), id),
                'u': lambda: update_field_hosts('USERNAME', get_username(), id),
                'k': lambda: update_field_hosts('KEY', key_definition(), id),
                'p': lambda: update_field_hosts('PORT', get_port(), id),
                'ad': lambda: edit_additional(id),
                'all': lambda: (deleteHosts(arg), createBaseConfig()),
                'c': lambda: sys.exit(f"Operation was canceled.")
            }
            while True:
                print(f"You can select next options:")
                print(f"hostname (h), address (a), username (u), key (k), port (p), additional (ad)")
                print(f"all (all) or cancel (c)")
                choice = input(f"Please enter your option: ")
                if choice in options:
                    options[choice]()
                    break
                else:
                    print(f"Incorrect input, try again.")
            conn.commit()
        else:
            sys.exit(f"Config not found!")
    else:
        sys.exit(f"Config with ID {id} does not exist!")


