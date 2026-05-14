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

def add_record(table_name, columns, values):
    conn = connect_bd()
    cursor = conn.cursor()

    placeholders = ", ".join(["%s"] * len(values))
    cols_str = ", ".join(columns)

    query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"

    try:
        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        print(f"Ошибка вставки: {e}")
    finally:
        conn.close()

def update_record(table_name, columns, values, record_id):
    conn = connect_bd()
    if not conn: return
    try:
        cursor = conn.cursor()
        set_clause = ", ".join([f"{col} = %s" for col in columns])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
        cursor.execute(query, tuple(values) + (record_id,))
        conn.commit()
    except Exception as e:
        print(f"Ошибка обновления записи: {e}")
    finally:
        conn.close()

def delete_record(table_name, record_id):
    conn = connect_bd()
    cursor = conn.cursor()

    try:
        cursor.execute(f"DELETE FROM {table_name} WHERE id = {record_id}")
        conn.commit()
    except Exception as e:
        print(f"Ошибка удаления: {e}")
    finally:
        conn.close()