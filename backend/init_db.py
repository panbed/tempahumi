import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

db_file = os.getenv('DB_FILE')
connection = sqlite3.connect(db_file)

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

connection.commit()
connection.close()
