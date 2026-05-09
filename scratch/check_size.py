import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('MYSQL_URL')
if db_url and db_url.startswith('mysql://'):
    db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)

engine = create_engine(db_url)
with engine.connect() as conn:
    query = """
    SELECT table_name, 
           round(((data_length + index_length) / 1024 / 1024), 2) as size_mb 
    FROM information_schema.TABLES 
    WHERE table_schema = 'railway';
    """
    res = conn.execute(text(query))
    for row in res:
        print(f"{row[0]}: {row[1]} MB")
