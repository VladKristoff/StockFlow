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


def validate_record_data(table_name, values, columns=None):
    """Валидация данных перед добавлением/обновлением"""
    errors = []

    if table_name == "products":
        # Проверяем цену (обычно 3-й параметр или ищем по колонке)
        if columns:
            try:
                price_idx = columns.index("price")
                price = float(values[price_idx])
                if price < 0:
                    errors.append("Цена не может быть отрицательной!")
                elif price == 0:
                    errors.append("Цена не может быть равна нулю!")
            except (ValueError, IndexError):
                errors.append("Некорректное значение цены!")

            try:
                count_idx = columns.index("count")
                count = int(values[count_idx])
                if count < 0:
                    errors.append("Количество не может быть отрицательным!")
            except (ValueError, IndexError):
                errors.append("Некорректное значение количества!")
        else:
            # Если columns не передан, пробуем по позициям (для продуктов: id, name, price, count, type_name)
            try:
                price = float(values[2])  # price на позиции 2
                if price < 0:
                    errors.append("Цена не может быть отрицательной!")
                elif price == 0:
                    errors.append("Цена не может быть равна нулю!")
            except (ValueError, IndexError):
                errors.append("Некорректное значение цены!")

            try:
                count = int(values[3])  # count на позиции 3
                if count < 0:
                    errors.append("Количество не может быть отрицательным!")
            except (ValueError, IndexError):
                errors.append("Некорректное значение количества!")

    elif table_name == "contractors":
        if columns:
            try:
                phone_idx = columns.index("phone")
                phone = str(values[phone_idx]).strip()
                if phone and len(phone) < 10:
                    errors.append("Телефон должен содержать минимум 10 символов!")
            except ValueError:
                pass

            try:
                inn_idx = columns.index("inn")
                inn = str(values[inn_idx]).strip()
                if inn and len(inn) not in [10, 12]:
                    errors.append("ИНН должен содержать 10 или 12 цифр!")
                if inn and not inn.isdigit():
                    errors.append("ИНН должен содержать только цифры!")
            except ValueError:
                pass

    return errors


def check_dependencies(table_name, record_id):
    """Проверка наличия зависимых записей перед удалением"""
    conn = connect_bd()
    if not conn:
        return True, "Ошибка подключения к базе данных!"

    try:
        cursor = conn.cursor()

        if table_name == "positions":
            # Проверяем, есть ли сотрудники с этой должностью
            cursor.execute("SELECT COUNT(*) FROM employees WHERE position_id = %s", (record_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                return False, f"Невозможно удалить должность! На нее ссылаются {count} сотрудник(ов). Сначала удалите или измените должность у сотрудников."

        elif table_name == "product_types":
            # Проверяем, есть ли товары этого типа
            cursor.execute("SELECT COUNT(*) FROM products WHERE type_id = %s", (record_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                return False, f"Невозможно удалить тип товара! Существует {count} товар(ов) этого типа. Сначала удалите или измените тип у товаров."

        elif table_name == "products":
            # Проверяем, есть ли товар в каких-либо документах (если есть таблицы документов)
            # Добавьте проверки для ваших документов
            pass

        return True, ""
    except Exception as e:
        return False, f"Ошибка проверки зависимостей: {e}"
    finally:
        conn.close()


def get_any_table(table_name):
    conn = connect_bd()
    if conn:
        try:
            cursor = conn.cursor()

            # Специальные запросы для таблиц с внешними ключами
            if table_name == "products":
                query = """
                    SELECT p.id, p.name, p.price, p.count, pt.name as type_name
                    FROM products p
                    LEFT JOIN product_types pt ON p.type_id = pt.id
                    ORDER BY p.id ASC
                """
            elif table_name == "employees":
                query = """
                    SELECT e.id, e.name, p.name as position_name
                    FROM employees e
                    LEFT JOIN positions p ON e.position_id = p.id
                    ORDER BY e.id ASC
                """
            else:
                query = f"SELECT * FROM {table_name} ORDER BY id ASC"

            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return []
        finally:
            conn.close()
    return []


def add_record(table_name, columns, values):
    conn = connect_bd()
    if not conn:
        return False, "Ошибка подключения к базе данных!"

    cursor = conn.cursor()

    # Валидация данных
    validation_errors = validate_record_data(table_name, values, columns)
    if validation_errors:
        return False, "\n".join(validation_errors)

    # Для products и employees нужно преобразовать названия в ID
    try:
        if table_name == "products" and "type_name" in columns:
            # Находим индекс type_name и преобразуем в type_id
            if "type_name" in columns:
                type_name_idx = columns.index("type_name")
                type_name = values[type_name_idx]

                # Получаем ID типа товара по названию
                cursor.execute("SELECT id FROM product_types WHERE name = %s", (type_name,))
                result = cursor.fetchone()
                if result:
                    # Заменяем название на ID
                    values = list(values)
                    values[type_name_idx] = result[0]
                    values = tuple(values)
                    # Меняем имя колонки в запросе
                    columns = list(columns)
                    columns[type_name_idx] = "type_id"
                    columns = tuple(columns)
                else:
                    return False, "Выбранный тип товара не найден в базе данных!"

        elif table_name == "employees" and "position_name" in columns:
            position_name_idx = columns.index("position_name")
            position_name = values[position_name_idx]

            # Получаем ID должности по названию
            cursor.execute("SELECT id FROM positions WHERE name = %s", (position_name,))
            result = cursor.fetchone()
            if result:
                values = list(values)
                values[position_name_idx] = result[0]
                values = tuple(values)
                columns = list(columns)
                columns[position_name_idx] = "position_id"
                columns = tuple(columns)
            else:
                return False, "Выбранная должность не найдена в базе данных!"

        placeholders = ", ".join(["%s"] * len(values))
        cols_str = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"

        cursor.execute(query, values)
        conn.commit()
        return True, "Запись успешно добавлена!"
    except psycopg.Error as e:
        conn.rollback()
        error_msg = str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            return False, "Запись с такими данными уже существует!"
        elif "foreign key constraint" in error_msg.lower():
            return False, "Нарушение ссылочной целостности! Проверьте правильность выбранных значений."
        else:
            return False, f"Ошибка базы данных: {error_msg}"
    except Exception as e:
        conn.rollback()
        return False, f"Ошибка при добавлении записи: {e}"
    finally:
        conn.close()


def update_record(table_name, columns, values, record_id):
    conn = connect_bd()
    if not conn:
        return False, "Ошибка подключения к базе данных!"

    try:
        cursor = conn.cursor()

        # Валидация данных
        validation_errors = validate_record_data(table_name, values, columns)
        if validation_errors:
            return False, "\n".join(validation_errors)

        # Для products и employees нужно преобразовать названия в ID
        if table_name == "products" and "type_name" in columns:
            type_name_idx = columns.index("type_name")
            type_name = values[type_name_idx]

            cursor.execute("SELECT id FROM product_types WHERE name = %s", (type_name,))
            result = cursor.fetchone()
            if result:
                values = list(values)
                values[type_name_idx] = result[0]
                values = tuple(values)
                columns = list(columns)
                columns[type_name_idx] = "type_id"
                columns = tuple(columns)
            else:
                return False, "Выбранный тип товара не найден в базе данных!"

        elif table_name == "employees" and "position_name" in columns:
            position_name_idx = columns.index("position_name")
            position_name = values[position_name_idx]

            cursor.execute("SELECT id FROM positions WHERE name = %s", (position_name,))
            result = cursor.fetchone()
            if result:
                values = list(values)
                values[position_name_idx] = result[0]
                values = tuple(values)
                columns = list(columns)
                columns[position_name_idx] = "position_id"
                columns = tuple(columns)
            else:
                return False, "Выбранная должность не найдена в базе данных!"

        set_clause = ", ".join([f"{col} = %s" for col in columns])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
        cursor.execute(query, tuple(values) + (record_id,))
        conn.commit()
        return True, "Запись успешно обновлена!"
    except psycopg.Error as e:
        conn.rollback()
        error_msg = str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            return False, "Запись с такими данными уже существует!"
        else:
            return False, f"Ошибка базы данных: {error_msg}"
    except Exception as e:
        conn.rollback()
        return False, f"Ошибка при обновлении записи: {e}"
    finally:
        conn.close()


def delete_record(table_name, record_id):
    conn = connect_bd()
    if not conn:
        return False, "Ошибка подключения к базе данных!"

    cursor = conn.cursor()

    try:
        # Проверяем зависимости перед удалением
        can_delete, message = check_dependencies(table_name, record_id)
        if not can_delete:
            return False, message

        cursor.execute(f"DELETE FROM {table_name} WHERE id = {record_id}")
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Запись с таким ID не найдена!"

        return True, "Запись успешно удалена!"
    except psycopg.Error as e:
        conn.rollback()
        return False, f"Ошибка базы данных при удалении: {e}"
    except Exception as e:
        conn.rollback()
        return False, f"Ошибка при удалении записи: {e}"
    finally:
        conn.close()


def search_records(table_name, search_term):
    """Поиск записей в таблице"""
    conn = connect_bd()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        search_pattern = f"%{search_term}%"

        # Разные запросы для разных таблиц
        if table_name == "products":
            query = """
                SELECT p.id, p.name, p.price, p.count, pt.name as type_name
                FROM products p
                LEFT JOIN product_types pt ON p.type_id = pt.id
                WHERE p.name ILIKE %s 
                   OR CAST(p.price AS TEXT) ILIKE %s 
                   OR CAST(p.count AS TEXT) ILIKE %s 
                   OR pt.name ILIKE %s
                ORDER BY p.id ASC
            """
            cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))

        elif table_name == "employees":
            query = """
                SELECT e.id, e.name, p.name as position_name
                FROM employees e
                LEFT JOIN positions p ON e.position_id = p.id
                WHERE e.name ILIKE %s OR p.name ILIKE %s
                ORDER BY e.id ASC
            """
            cursor.execute(query, (search_pattern, search_pattern))

        elif table_name == "contractors":
            query = f"""
                SELECT * FROM {table_name}
                WHERE name ILIKE %s 
                   OR phone ILIKE %s 
                   OR inn ILIKE %s 
                   OR address ILIKE %s
                ORDER BY id ASC
            """
            cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))

        else:
            # Для остальных таблиц
            cursor.execute(f"SELECT * FROM {table_name} WHERE name ILIKE %s ORDER BY id ASC", (search_pattern,))

        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка поиска: {e}")
        return []
    finally:
        conn.close()


def get_foreign_key_options(table_name, foreign_key_field):
    """Получить список доступных значений для внешнего ключа"""
    conn = connect_bd()
    if not conn:
        return []

    try:
        cursor = conn.cursor()

        if table_name == "products" and foreign_key_field == "type_id":
            cursor.execute("SELECT name FROM product_types ORDER BY name")
        elif table_name == "employees" and foreign_key_field == "position_id":
            cursor.execute("SELECT name FROM positions ORDER BY name")
        else:
            return []

        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Ошибка получения данных для combo box: {e}")
        return []
    finally:
        conn.close()