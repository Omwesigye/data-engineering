import os
from dotenv import load_dotenv

# Load local .env only for local development
load_dotenv()

# Build a robust DB URL for SQLAlchemy
def normalize_db_url(raw_url: str) -> str:
    """Convert a raw DB URL into a SQLAlchemy‑compatible URL.
    Handles MySQL (Railway) and PostgreSQL (Render) formats.
    """
    from urllib.parse import urlparse, quote_plus, urlunparse

    raw_url = raw_url.strip()

    # Handle PostgreSQL (Render uses postgres://, SQLAlchemy requires postgresql://)
    if raw_url.startswith("postgres://") or raw_url.startswith("postgresql://"):
        if raw_url.startswith("postgres://"):
            raw_url = raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif not raw_url.startswith("postgresql+psycopg2://"):
            raw_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        
        # Safe Parse and Encode
        parsed = urlparse(raw_url)
        username = quote_plus(parsed.username) if parsed.username else ""
        password = quote_plus(parsed.password) if parsed.password else ""
        netloc = f"{username}:{password}@{parsed.hostname}" if username or password else parsed.hostname
        if parsed.port:
            netloc += f":{parsed.port}"
        return urlunparse(("postgresql+psycopg2", netloc, parsed.path, "", "", ""))

    # Handle MySQL
    if raw_url.startswith("mysql://") or raw_url.startswith("mysql+pymysql://"):
        if raw_url.startswith("mysql://"):
            raw_url = raw_url.replace("mysql://", "mysql+pymysql://", 1)
        
        parsed = urlparse(raw_url)
        username = quote_plus(parsed.username) if parsed.username else ""
        password = quote_plus(parsed.password) if parsed.password else ""
        netloc = f"{username}:{password}@{parsed.hostname}" if username or password else parsed.hostname
        if parsed.port:
            netloc += f":{parsed.port}"
        return urlunparse(("mysql+pymysql", netloc, parsed.path, "", "", ""))

    return raw_url

# Load env vars
raw_db_url = (
    os.getenv("DATABASE_URL") 
    or os.getenv("MYSQL_URL") 
    or os.getenv("DATABASE_PUBLIC_URL")
)

if not raw_db_url:
    # Fallback for local .env if needed
    raw_db_url = os.getenv("MYSQL_URL") 

if not raw_db_url:
    raise EnvironmentError("No database URL found in environment variables.")

DATABASE_URL = normalize_db_url(raw_db_url)
# For backwards compatibility with existing scripts
MYSQL_URL = DATABASE_URL

print("Raw DB URL:", raw_db_url)
print("Normalized DB URL:", DATABASE_URL)

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
CHUNK_SIZE = 100000
DEV_MODE_LIMIT = 10

# --- TABLE NAMES ---
TABLE_PATENTS = "patents"
TABLE_INVENTORS = "inventors"
TABLE_COMPANIES = "companies"
TABLE_PATENT_INVENTORS = "patent_inventors"
TABLE_PATENT_COMPANIES = "patent_companies"