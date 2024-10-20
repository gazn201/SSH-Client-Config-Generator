#!/bin/python3
import sqlite3
import os
import sys
from pathlib import Path

SSH_OLD = input("Absolute path to yours .ssh directory[If not exist will be created]: ")

USER_HOME = Path.home()

SCRIPT_HOME = f"{USER_HOME}/.ssh-manager"

if os.path.exists(f"{SSH_OLD}"):
    while True:
        BACK_BOOL = input("Backup your existing .ssh directory?[y/n]: ")
        if BACK_BOOL in ['y','Y','Yes','yes']:
            print(f"Backupin' {SSH_OLD}")
            Path(f"{USER_HOME}/.ssh_before_manager").mkdir(parent=True, exits_ok=True)
            os.system("cp {SSH_OLD}/* {USER_HOME}/.ssh_before_manager")
        elif BACK_BOOL in ['n','N','no','No']:
            break
        else:
            print("Unexpected answer!")
else:
    pass


if os.path.exists(SCRIPT_HOME) and os.path.exists(f"{SCRIPT_HOME}/ssh-conf.db"):
    print("ssh-manager directory already exists!")
    sys.exit(0)
else:
    #Create script home
    Path(SCRIPT_HOME).mkdir(parents=True, exist_ok=True)
    if os.path.exists(f"{SCRIPT_HOME}/ssh-conf.db"):
        print("ssh-conf database exists! Skipping the creation...")
        pass
    else:
        conn = sqlite3.connect(f'{SCRIPT_HOME}/ssh-conf.db')
        cursor = conn.cursor()
        #Create Hosts table
        cursor.execute("CREATE TABLE 'Hosts'(ID INT PRIMARY KEY NOT NULL,HOSTNAME TEXT NOT NULL,ADDRESS CHAR(15),USERNAME TEXT NOT NULL,KEY INT NOT NULL,PORT INTEGER)")
        #Create Keys table
        cursor.execute("CREATE TABLE 'KEYS'(KEYID INT PRIMARY KEY NOT NULL,KEYNAME TEXT NOT NULL,KEYPATH TEXT NOT NULL)")
        #Create Additional Parametres table
        cursor.execute("CREATE TABLE 'ADDITIONALPARAMS'(KEYID INT NOT NULL,PARAMETR TEXT NOT NULL,VALUE TEXT)")


