import sqlite3
import os

def parse_ssh_config(ssh_config_path):
    configs = []
    with open(ssh_config_path, 'r') as f:
        config = {}
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('   '):
                # Если строка начинается с пробела, добавляем ее к предыдущему значению
                if 'host' in config:
                    config.setdefault('port', '22')
                    config.setdefault('identityfile', '')  # добавим пустое значение для identityfile
                    config.setdefault('proxyjump', '')  # добавим пустое значение для proxyjump
                    key, value = line.split(None, 1)
                    config[key.lower()] += ' ' + value
            else:
                # Если строка не начинается с пробела, это новый блок конфигурации
                if config:
                    configs.append(config)
                config = {}
                key, value = line.split(None, 1)
                config[key.lower()] = value
        # Добавляем последний блок конфигурации, если он был
        if config:
            config.setdefault('port', '22')
            config.setdefault('identityfile', '')  # добавим пустое значение для identityfile
            config.setdefault('proxyjump', '')  # добавим пустое значение для proxyjump
            configs.append(config)
    return configs

def create_ssh_config_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS ssh_config (
                        id INTEGER PRIMARY KEY,
                        host TEXT,
                        hostname TEXT,
                        user TEXT,
                        port INTEGER,
                        identityfile TEXT,
                        proxyjump TEXT
                    )''')

def insert_ssh_config(cursor, configs):
    current_config = None
    for config in configs:
        if 'host' in config:
            # Если это новый хост, добавляем предыдущий хост, если он существует
            if current_config:
                cursor.execute('''INSERT INTO ssh_config (host, hostname, user, port, identityfile, proxyjump)
                                  VALUES (?, ?, ?, ?, ?, ?)''',
                               (current_config.get('host'), current_config.get('hostname'), current_config.get('user'),
                                current_config.get('port'), current_config.get('identityfile'), current_config.get('proxyjump')))
            current_config = config
        else:
            # Если это продолжение предыдущего хоста, добавляем данные к текущему хосту
            if current_config:
                for key, value in config.items():
                    if key in ['hostname', 'user', 'port', 'identityfile', 'proxyjump']:
                        current_config[key] = value

    # Добавляем последний хост, если он существует
    if current_config:
        cursor.execute('''INSERT INTO ssh_config (host, hostname, user, port, identityfile, proxyjump)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (current_config.get('host'), current_config.get('hostname'), current_config.get('user'),
                        current_config.get('port'), current_config.get('identityfile'), current_config.get('proxyjump')))

def main():
    ssh_config_path = os.path.expanduser('~/SSH-Client-Config-Generator/config')
    if not os.path.isfile(ssh_config_path):
        print("SSH config file not found.")
        return

    configs = parse_ssh_config(ssh_config_path)
    
    db_path = os.path.join(os.path.expanduser('~'), 'SSH-Client-Config-Generator', 'ssh_config.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    create_ssh_config_table(cursor)
    insert_ssh_config(cursor, configs)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()