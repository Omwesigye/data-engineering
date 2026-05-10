import sqlalchemy
from sqlalchemy import text
import config
import logging
import re

logging.basicConfig(level=logging.INFO)

# Connect to the database using the URL from config
engine = sqlalchemy.create_engine(config.DATABASE_URL)

logging.info(f"Connecting to database to apply schema...")

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
