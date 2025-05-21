import cx_Oracle
from config import DB_CONFIG
def get_db_connection():
    try:
        dsn = DB_CONFIG.get("dsn")
        if not dsn:
            raise ValueError("Missing 'dsn' in DB_CONFIG. Check config.py.")
        connection = cx_Oracle.connect(
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            dsn=dsn
        )
        print("Database connection established successfully!")
        return connection
    except cx_Oracle.DatabaseError as e:
        print(f"Database connection error: {e}")
        return None 
    except KeyError as e:
        print(f"Missing key in DB_CONFIG: {e}")
        return None
