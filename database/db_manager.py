import psycopg

def connect_bd():
    try:
        conn = psycopg.connect(
            host="localhost",
            port="5432",
            dbname="PP_DB",
            user="postgres",
            password="1234",
            connect_timeout=2
        )
        return conn
    except Exception:
        return None

def get_any_table(table_name):
    conn = connect_bd()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY id ASC")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return []
        finally:
            conn.close()
    return []