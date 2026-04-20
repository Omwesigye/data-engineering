

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Data source URL (PatentsView data)
DATA_URL = "https://bulkdata.uspto.gov/data/patent/grant/redbook/bibliographic/2024/pgbr_2024.zip"

# Chunk size for processing (rows per chunk)
CHUNK_SIZE = 50000

# Output directory
OUTPUT_DIR = "output"

# Table names
TABLE_PATENTS = "patents"
TABLE_INVENTORS = "inventors"
TABLE_COMPANIES = "companies"
TABLE_PATENT_INVENTORS = "patent_inventors"
TABLE_PATENT_COMPANIES = "patent_companies"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)