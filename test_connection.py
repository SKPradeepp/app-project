import mysql.connector
from config import DB_CONFIG

try:
    con = mysql.connector.connect(**DB_CONFIG)

    if con.is_connected():
        print("MySQL Connected Successfully!")
        print("Database:", DB_CONFIG["database"])

    con.close()

except mysql.connector.Error as e:
    print("Connection Failed:", e)