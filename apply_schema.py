import sqlalchemy
from sqlalchemy import text
import config
import logging
import re

logging.basicConfig(level=logging.INFO)

# Connect without database to create it
server_url = 'mysql+pymysql://root:@localhost:3306/'
server_engine = sqlalchemy.create_engine(server_url)

with server_engine.connect() as conn:
    logging.info("Creating fresh database 'patent_db'...")
    conn.execute(text("CREATE DATABASE IF NOT EXISTS patent_db"))
    conn.commit()

# Connect to the new database
engine = sqlalchemy.create_engine(config.MYSQL_URL)
with open('schema.sql', 'r') as f:
    sql_script = f.read()

# Remove SQL comments
sql_script = re.sub(r'--.*', '', sql_script)

with engine.connect() as conn:
    for statement in sql_script.split(';'):
        stmt = statement.strip()
        if stmt:
            logging.info(f"Executing: {stmt[:50]}...")
            conn.execute(text(stmt))
    conn.commit()
    print("Schema applied successfully to patent_db!")
