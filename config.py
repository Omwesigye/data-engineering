import os
from dotenv import load_dotenv

# Load local .env only for local development
load_dotenv()

# Try Railway variable names
MYSQL_URL = (
    os.getenv("MYSQL_URL")
    or os.getenv("DATABASE_URL")
    or os.getenv("MYSQL_PRIVATE_URL")
)

print("Raw MYSQL_URL:", MYSQL_URL)

if MYSQL_URL:
    # Railway compatibility fix
    if MYSQL_URL.startswith("mysql://"):
        MYSQL_URL = MYSQL_URL.replace(
            "mysql://",
            "mysql+pymysql://",
            1
        )

    print("Fixed MYSQL_URL:", MYSQL_URL)

else:
    raise Exception(
        "No database URL found. "
        "Check Railway environment variables."
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