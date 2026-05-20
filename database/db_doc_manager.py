# database/db_doc_manager.py
from database.db_manager import connect_bd
from datetime import datetime
import psycopg


def get_all_documents(doc_type_id: int):
    """Получить все документы определенного типа"""
    conn = connect_bd()
    if conn:
        try:
            cur = conn.cursor()
            query = """
                SELECT d.id, d.doc_number, d.doc_date, d.created_at,
                       c.name as contractor_name, e.name as employee_name
                FROM documents d
                LEFT JOIN contractors c ON d.contractor_id = c.id
                LEFT JOIN employees e ON d.employee_id = e.id
                WHERE d.doc_type_id = %s  
                ORDER BY d.created_at DESC
            """
            cur.execute(query, (doc_type_id,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(f"Ошибка при получении накладных: {e}")
            return []
    return []


def get_document_items(document_id: int):
    """Получить все позиции документа"""
    conn = connect_bd()
    if conn:
        try:
            cur = conn.cursor()
            query = """
                SELECT di.id, di.product_id, p.name, di.quantity, di.price_at_moment,
                       (di.quantity * di.price_at_moment) as total
                FROM document_items di
                JOIN products p ON di.product_id = p.id
                WHERE di.document_id = %s
            """
            cur.execute(query, (document_id,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(f"Ошибка получения позиций документа: {e}")
            return []
    return []


def get_document_by_id(document_id: int):
    """Получить документ по ID"""
    conn = connect_bd()
    if conn:
        try:
            cur = conn.cursor()
            query = """
                SELECT d.id, d.doc_number, d.doc_date, d.created_at,
                       d.doc_type_id, d.contractor_id, d.employee_id,
                       c.name as contractor_name, e.name as employee_name
                FROM documents d
                LEFT JOIN contractors c ON d.contractor_id = c.id
                LEFT JOIN employees e ON d.employee_id = e.id
                WHERE d.id = %s
            """
            cur.execute(query, (document_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            return row
        except Exception as e:
            print(f"Ошибка получения документа: {e}")
            return None
    return None


def get_document_by_id_old(document_id: int):  # Алиас для обратной совместимости
    return get_document_by_id(document_id)


def get_next_doc_number(doc_type_id: int):
    """Сгенерировать следующий номер документа"""
    conn = connect_bd()
    if conn:
        try:
            cur = conn.cursor()
            year = datetime.now().year
            prefix = "П" if doc_type_id == 1 else "Р"

            query = """
                SELECT doc_number FROM documents 
                WHERE doc_type_id = %s AND doc_number LIKE %s
                ORDER BY id DESC LIMIT 1
            """
            cur.execute(query, (doc_type_id, f"{prefix}-{year}-%"))
            last = cur.fetchone()

            if last:
                last_num = int(last[0].split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1

            cur.close()
            conn.close()
            return f"{prefix}-{year}-{new_num:04d}"
        except Exception as e:
            print(f"Ошибка генерации номера: {e}")
            return f"{'П' if doc_type_id == 1 else 'Р'}-{datetime.now().year}-0001"
    return None


def create_document(doc_type_id: int, doc_date: str, contractor_id: int, employee_id: int, items: list):
    """
    Создать новый документ с позициями
    items: [(product_id, quantity, price_at_moment), ...]
    Возвращает: (success, message, document_id)
    """
    conn = connect_bd()
    if not conn:
        return False, "Ошибка подключения к БД", None

    try:
        cur = conn.cursor()

        # Генерируем номер документа
        doc_number = get_next_doc_number(doc_type_id)

        # Создаем документ
        query_doc = """
            INSERT INTO documents (doc_number, doc_date, doc_type_id, contractor_id, employee_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """
        cur.execute(query_doc, (doc_number, doc_date, doc_type_id, contractor_id, employee_id, datetime.now()))
        doc_id = cur.fetchone()[0]

        # Добавляем позиции и обновляем остатки
        for product_id, quantity, price in items:
            # Добавляем позицию
            query_item = """
                INSERT INTO document_items (document_id, product_id, quantity, price_at_moment)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(query_item, (doc_id, product_id, quantity, price))

            # Обновляем остатки товара
            if doc_type_id == 1:  # Приход
                query_update = "UPDATE products SET count = count + %s WHERE id = %s"
            else:  # Расход
                # Проверяем достаточно ли товара для расхода
                cur.execute("SELECT count FROM products WHERE id = %s", (product_id,))
                current_count = cur.fetchone()[0]
                if current_count < quantity:
                    conn.rollback()
                    return False, f"Недостаточно товара! Доступно: {current_count}, запрошено: {quantity}", None
                query_update = "UPDATE products SET count = count - %s WHERE id = %s"

            cur.execute(query_update, (quantity, product_id))

        conn.commit()
        cur.close()
        conn.close()

        return True, doc_number, doc_id

    except psycopg.Error as e:
        conn.rollback()
        return False, f"Ошибка БД: {e}", None
    except Exception as e:
        conn.rollback()
        return False, f"Ошибка: {e}", None
    finally:
        if conn:
            conn.close()


def delete_document(document_id: int, doc_type_id: int):
    """Удалить документ и восстановить остатки"""
    conn = connect_bd()
    if not conn:
        return False, "Ошибка подключения к БД"

    try:
        cur = conn.cursor()

        # Получаем все позиции документа
        items = get_document_items(document_id)

        # Восстанавливаем остатки
        for item in items:
            product_id = item[1]
            quantity = item[3]

            if doc_type_id == 1:  # Приход - вычитаем
                query_update = "UPDATE products SET count = count - %s WHERE id = %s"
            else:  # Расход - прибавляем
                query_update = "UPDATE products SET count = count + %s WHERE id = %s"

            cur.execute(query_update, (quantity, product_id))

        # Удаляем позиции
        cur.execute("DELETE FROM document_items WHERE document_id = %s", (document_id,))

        # Удаляем документ
        cur.execute("DELETE FROM documents WHERE id = %s", (document_id,))

        conn.commit()
        cur.close()
        conn.close()

        return True, "Документ успешно удален!"

    except Exception as e:
        conn.rollback()
        return False, f"Ошибка: {e}"
    finally:
        if conn:
            conn.close()


def check_product_availability(product_id: int, quantity: int):
    """Проверить наличие товара на складе"""
    conn = connect_bd()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT count FROM products WHERE id = %s", (product_id,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result:
                return result[0] >= quantity, result[0]
            return False, 0
        except Exception as e:
            print(f"Ошибка проверки: {e}")
            return False, 0
    return False, 0


def get_available_products():
    """Получить список товаров с остатками"""
    conn = connect_bd()
    if conn:
        try:
            cur = conn.cursor()
            query = """
                SELECT p.id, p.name, p.price, p.count, pt.name as type_name
                FROM products p
                LEFT JOIN product_types pt ON p.type_id = pt.id
                ORDER BY p.name
            """
            cur.execute(query)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(f"Ошибка: {e}")
            return []
    return []