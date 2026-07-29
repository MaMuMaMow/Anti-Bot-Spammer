import sqlite3

def initialize_table():
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
    server_id INTEGER PRIMARY KEY,
    text_capacity INTEGER,
    text_strictness INTEGER,
    picture_capacity INTEGER,
    picture_strictness INTEGER,
    )""")
    conn.commit()
    conn.close()

def initialize_server(server_id:int):
    return 1

def update_settings(server_id:int, row:str, value:int) :
    return 1