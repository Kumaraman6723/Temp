import pymysql
from config import DB_CONFIG

def get_db_connection():
    return pymysql.connect(
        host=DB_CONFIG["HOST"],
        user=DB_CONFIG["USER"],
        password=DB_CONFIG["PASSWORD"],
        database=DB_CONFIG["DATABASE"],
        port=DB_CONFIG["PORT"]
    )

def fetch_email():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT Email FROM auth")
    output = cur.fetchall()
    conn.close()
    return [i[0] for i in output]

def recover_passkey(new_password, email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE auth SET Password = %s WHERE Email = %s", (new_password, email))
    conn.commit()
    conn.close()

def fetch_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT Email, Password FROM auth")
    output = cur.fetchall()
    conn.close()
    return output
