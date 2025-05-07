def execute_sql_file(file_path, cur):
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    cur.execute(sql)
    print(f"Executed: {file_path}")