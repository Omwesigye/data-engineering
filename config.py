import os
from dotenv import load_dotenv

# Load local .env only for local development
load_dotenv()

# Try Railway variable names
MYSQL_URL = (
    (os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL") or os.getenv("MYSQL_PRIVATE_URL"))
    .strip()
    if os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL") or os.getenv("MYSQL_PRIVATE_URL")
    else None
)

print("Raw MYSQL_URL:", MYSQL_URL)

if MYSQL_URL:
    # Ensure driver prefix for SQLAlchemy
    if MYSQL_URL.startswith("mysql://"):
        MYSQL_URL = MYSQL_URL.replace("mysql://", "mysql+pymysql://", 1)
    print("Fixed MYSQL_URL:", MYSQL_URL)
else:
    raise EnvironmentError(
        "Database URL not found. Please set MYSQL_URL (or DATABASE_URL) in your environment or .env file."
    )

# --- LOCAL FILE PATHS ---
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
CHUNK_SIZE = 25000
DEV_MODE_LIMIT = 4

# --- TABLE NAMES ---
TABLE_PATENTS = "patents"
TABLE_INVENTORS = "inventors"
TABLE_COMPANIES = "companies"
TABLE_PATENT_INVENTORS = "patent_inventors"
TABLE_PATENT_COMPANIES = "patent_companies"