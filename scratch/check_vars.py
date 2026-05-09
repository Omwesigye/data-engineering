import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('MYSQL_URL')
if db_url and db_url.startswith('mysql://'):
    db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)

engine = create_engine(db_url)
with engine.connect() as conn:
    vars_to_check = ['innodb_data_file_path', 'innodb_file_per_table', 'max_heap_table_size', 'tmp_table_size', 'datadir']
    for v in vars_to_check:
        res = conn.execute(text(f"SHOW VARIABLES LIKE '{v}';"))
        for row in res:
            print(f"{row[0]}: {row[1]}")
    
    # Also check disk free space in MySQL if possible
    # SELECT @@innodb_data_file_path;
