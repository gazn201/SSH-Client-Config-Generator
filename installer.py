#!/bin/python3
import sqlite3
import os
from os import environ
import sys
from pathlib import Path

USER_HOME = Path.home()

SSH_OLD = f"{USER_HOME}/.ssh"
if os.path.exists(f"{SSH_OLD}/config"):
    PROMPT = input(f"found config in {SSH_OLD}, is it actual config?[y/n]: ")
    if PROMPT in ['y', 'Y','yes','Yes']:
        print("Working with this...")
    elif PROMT in ['n','N','no','No']:
        SSH_OLD = input("Absolute path to yours ssh config directory[If not exist will be created]: ")

SCRIPT_HOME = f"{USER_HOME}/.ssh-manager"

if os.path.exists(f"{SSH_OLD}"):
    while True:
        BACK_BOOL = input("Backup your existing .ssh directory?[y/n]: ")
        if BACK_BOOL in ['y','Y','Yes','yes']:
            print(f"Backupin' {SSH_OLD} to {USER_HOME}/.ssh-before-manager")
            Path(f"{USER_HOME}/.ssh_before_manager").mkdir(parent=True, exits_ok=True)
            os.system("cp {SSH_OLD}/* {USER_HOME}/.ssh_before_manager")
        elif BACK_BOOL in ['n','N','no','No']:
            print("Skippin' backup")
            break
        else:
            print("Unexpected answer!")
else:
    print("Creating .ssh directory")
    os.mkdirs(f"{USER_HOME}/.ssh, mode=700, exist_ok=True")

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

        #Create .env
        with open(f"{SCRIPT_HOME}/.env", "w") as env:
            env.write(f"SCRIPT_HOME='{SCRIPT_HOME}' \n
                        SSH_CONFIG='{USER_HOME}/.ssh/config' \n
                        ")

USER_SHELL = environ['SHELL']

if USER_SHELL == 'bash':
    with open(f"{USER_HOME}/.bashrc", "a") as shell:
        shell.write(f"export PATH=$PATH:{SCRIPT_HOME}")
elif USER_SHELL == 'zsh':
    with open(f"{USESR_HOME}/.zshrc", "a") as shell:
        shell.write(f"export PATH=$PATH:{SCRIPT_HOME}")
else:
    print(f"Sorry! Uknown shell, add this to yours .[$SHELL]rc file: \n export PATH=$PATH:{SCRIPT_HOME}")
