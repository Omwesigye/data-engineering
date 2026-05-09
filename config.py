import os
from dotenv import load_dotenv

# Load environment variables (SUPABASE_URL, etc.)
load_dotenv()

# MySQL configuration
MYSQL_URL = os.getenv('MYSQL_URL')
if MYSQL_URL and MYSQL_URL.startswith('mysql://'):
    MYSQL_URL = MYSQL_URL.replace('mysql://', 'mysql+pymysql://', 1)

# --- LOCAL FILE PATHS ---
# We point to the 'raw' folder in your project root
RAW_DATA_DIR = "raw"
OUTPUT_DIR = "output"

FILES = {
    "patents": os.path.join(RAW_DATA_DIR, "g_patent.tsv.zip"),
    "inventors": os.path.join(RAW_DATA_DIR, "g_inventor_disambiguated.tsv.zip"),
    "companies": os.path.join(RAW_DATA_DIR, "g_assignee_not_disambiguated.tsv.zip"),
    "patent_inventors": os.path.join(RAW_DATA_DIR, "g_inventor_disambiguated.tsv.zip"),
    "patent_companies": os.path.join(RAW_DATA_DIR, "g_assignee_not_disambiguated.tsv.zip")
}

# --- PIPELINE SETTINGS ---
CHUNK_SIZE = 50000
DEV_MODE_LIMIT = 40  # Set to None for full load, or a number for max chunks (40 = 2,000,000 rows)

# Table names matching your Supabase schema
TABLE_PATENTS = "patents"
TABLE_INVENTORS = "inventors"
TABLE_COMPANIES = "companies"
TABLE_PATENT_INVENTORS = "patent_inventors"
TABLE_PATENT_COMPANIES = "patent_companies"