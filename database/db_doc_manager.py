from database.db_manager import connect_bd

def get_all_documents(doc_type_id: int):
    conn = connect_bd()
    if conn:
        try:
            cur = conn.cursor()
            # Выбираем номер, дату и время создания для типа 1
            query = f"""
                SELECT doc_number, doc_date, created_at 
                FROM Documents 
                WHERE doc_type_id = {doc_type_id}  
                ORDER BY created_at DESC
            """
            cur.execute(query)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(f"Ошибка при получении накладных: {e}")
            return []
    return []

def get_contractors(self):
    rows = self.db_manager.get_any_table("contractors") # Или спец. метод
    self.contractor_map = {row[1]: row[0] for row in rows}
    return list(self.contractor_map.keys())

def get_employees(self):
    rows = self.db_manager.get_any_table("employees")
    self.employee_map = {row[1]: row[0] for row in rows}
    return list(self.employee_map.keys())