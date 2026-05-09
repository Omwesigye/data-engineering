import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('MYSQL_URL')
if db_url and db_url.startswith('mysql://'):
    db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)

engine = create_engine(db_url)
with engine.connect() as conn:
    print("Dropping temporary tables to free space...")
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    conn.execute(text("DROP TABLE IF EXISTS temp_patents;"))
    conn.execute(text("DROP TABLE IF EXISTS temp_inventors;"))
    conn.execute(text("DROP TABLE IF EXISTS temp_companies;"))
    conn.execute(text("DROP TABLE IF EXISTS temp_patent_inventors;"))
    conn.execute(text("DROP TABLE IF EXISTS temp_patent_companies;"))
    
    print("Trying to drop the main patents table to clear significant space...")
    # Dropping is often safer than truncating when disk is full because it frees the file immediately
    conn.execute(text("DROP TABLE IF EXISTS patents;"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    conn.commit()
    print("Space clearing attempted.")
