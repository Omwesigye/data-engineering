import pandas as pd
import zipfile
import os
from sqlalchemy import create_engine, text
import config
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PatentDataPipeline:
    """Handles ETL process specifically for local PatentsView ZIP files."""
    
    def __init__(self):
        self.engine = None
        self.setup_database_connection()
        
    def setup_database_connection(self):
        try:
            db_url = config.MYSQL_URL
            self.engine = create_engine(db_url)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def extract_and_load_file(self, table_key: str, file_path: str):
        """Opens local ZIP file and loads TSV in chunks to avoid memory issues."""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return

        logger.info(f"Processing {table_key} from local path: {file_path}")
        
        try:
            # Open local zip file
            with zipfile.ZipFile(file_path) as zip_ref:
                # Get the name of the TSV inside (usually matches zip name minus .zip)
                tsv_file_name = zip_ref.namelist()[0]
                logger.info(f"Reading TSV: {tsv_file_name}")
                
                with zip_ref.open(tsv_file_name) as f:
                    # Process in chunks to keep RAM usage low on your EliteBook
                    for i, chunk in enumerate(pd.read_csv(f, sep='\t', chunksize=config.CHUNK_SIZE, low_memory=False)):
                        if config.DEV_MODE_LIMIT and i >= config.DEV_MODE_LIMIT:
                            logger.info(f"Dev mode limit reached. Stopping after {i * config.CHUNK_SIZE} rows for {table_key}.")
                            break

                        clean_chunk = self.transform_logic(table_key, chunk)
                        self.load_chunk_to_db(table_key, clean_chunk, is_first=(i == 0))
                        
                        if i % 1 == 0: # Log every chunk for visibility
                            logger.info(f"Progress for {table_key}: Processed {(i+1) * config.CHUNK_SIZE} rows...")
                        
            logger.info(f"Completed loading for {table_key}")
            
        except Exception as e:
            logger.error(f"Failed to process {table_key}: {e}")
            raise

    def transform_logic(self, table_key: str, df: pd.DataFrame) -> pd.DataFrame:
        """Remaps PatentsView headers to match your database schema."""
        if table_key == "patents":
            # Map g_patent.tsv
            df = df.rename(columns={'patent_title': 'title', 'patent_date': 'filing_date'})
            df['abstract'] = ''
            
            # Convert to proper date objects
            df['filing_date'] = pd.to_datetime(df['filing_date'], errors='coerce')
            df['year'] = df['filing_date'].dt.year
            df['year'] = df['year'].fillna(0).astype(int)
            
            # Ensure only required columns are kept
            cols = ['patent_id', 'title', 'abstract', 'filing_date', 'year']
            return df[[c for c in cols if c in df.columns]].fillna({'abstract': '', 'title': ''})
        
        if table_key == "inventors":
            # Map g_inventor_disambiguated.tsv
            df['name'] = df['disambig_inventor_name_first'].astype(str) + ' ' + df['disambig_inventor_name_last'].astype(str)
            df['country'] = ''
            cols = ['inventor_id', 'name', 'country']
            df = df[[c for c in cols if c in df.columns]].drop_duplicates(subset=['inventor_id']).fillna('')
            return df
            
        if table_key == "companies":
            # Map g_assignee_not_disambiguated.tsv
            df = df.rename(columns={'assignee_id': 'company_id', 'raw_assignee_organization': 'name'})
            cols = ['company_id', 'name']
            df = df[[c for c in cols if c in df.columns]].drop_duplicates(subset=['company_id']).fillna('')
            return df
            
        if table_key == "patent_inventors":
            cols = ['patent_id', 'inventor_id']
            return df[[c for c in cols if c in df.columns]].drop_duplicates()
            
        if table_key == "patent_companies":
            df = df.rename(columns={'assignee_id': 'company_id'})
            cols = ['patent_id', 'company_id']
            return df[[c for c in cols if c in df.columns]].drop_duplicates()
            
        return df

    def load_chunk_to_db(self, table_key: str, df: pd.DataFrame, is_first: bool):
        """Helper to load chunks into MySQL with Conflict Handling."""
        table_name = getattr(config, f"TABLE_{table_key.upper()}")
        
        with self.engine.connect() as conn:
            # 1. Clear table if it's the first chunk
            if is_first:
                logger.info(f"Truncating table {table_name}...")
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
                conn.execute(text(f"TRUNCATE TABLE {table_name};"))
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
                conn.commit()

            # 2. Create a TEMPORARY table with the same schema (uses less persistent disk space)
            temp_table = f"temp_{table_name}"
            conn.execute(text(f"DROP TEMPORARY TABLE IF EXISTS {temp_table}"))
            conn.execute(text(f"CREATE TEMPORARY TABLE {temp_table} LIKE {table_name}"))
            
            # Load chunk into temporary table
            df.to_sql(temp_table, conn, if_exists='append', index=False)

            # 3. Perform UPSERT (Insert on conflict do nothing)
            cols = ", ".join(df.columns)
            
            if table_key in ["patents", "inventors", "companies"]:
                insert_sql = f"""
                    INSERT IGNORE INTO {table_name} ({cols})
                    SELECT {cols} FROM {temp_table}
                """
            elif table_key == "patent_inventors":
                insert_sql = f"""
                    INSERT IGNORE INTO {table_name} (patent_id, inventor_id)
                    SELECT t.patent_id, t.inventor_id 
                    FROM {temp_table} t
                    INNER JOIN patents p ON t.patent_id = p.patent_id
                    INNER JOIN inventors i ON t.inventor_id = i.inventor_id
                """
            elif table_key == "patent_companies":
                insert_sql = f"""
                    INSERT IGNORE INTO {table_name} (patent_id, company_id)
                    SELECT t.patent_id, t.company_id 
                    FROM {temp_table} t
                    INNER JOIN patents p ON t.patent_id = p.patent_id
                    INNER JOIN companies c ON t.company_id = c.company_id
                """
            else:
                insert_sql = f"""
                    INSERT IGNORE INTO {table_name} ({cols})
                    SELECT {cols} FROM {temp_table}
                """

            conn.execute(text(insert_sql))
            conn.execute(text(f"DROP TEMPORARY TABLE IF EXISTS {temp_table}"))
            conn.commit()

    def run_pipeline(self):
        """Iterates through files in the order required for Foreign Keys."""
        # Priority order: Patents -> Entities -> Links
        load_order = ["patents", "inventors", "companies", "patent_inventors", "patent_companies"]
        
        try:
            for table_key in load_order:
                if table_key in config.FILES:
                    file_path = config.FILES[table_key]
                    self.extract_and_load_file(table_key, file_path)
            
            logger.info("All local patent data successfully integrated.")
            
        except Exception as e:
            logger.error(f"PIPELINE TERMINATED: {e}")
            sys.exit(1)

if __name__ == "__main__":
    pipeline = PatentDataPipeline()
    pipeline.run_pipeline()