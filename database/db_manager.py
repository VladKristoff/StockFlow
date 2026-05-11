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


def get_products():
    try:
        with psycopg.connect(
            host="localhost",
            port="5432",
            dbname="PP_DB",
            user="postgres",
            password="1234"
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, price, count, type_id FROM products")
                return cur.fetchall()
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return []