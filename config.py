import os
from dotenv import load_dotenv

# Load local .env only for local development
load_dotenv()

# Build a robust MySQL URL for SQLAlchemy
def normalize_mysql_url(raw_url: str) -> str:
    """Convert a raw MySQL URL into a SQLAlchemy‑compatible URL.
    Handles Railway's `mysql://` format, ensures the `pymysql` driver is used,
    and URL‑encodes username/password to avoid parsing errors.
    """
    from urllib.parse import urlparse, quote_plus, urlunparse

    # Ensure we have a string
    raw_url = raw_url.strip()

    # Replace driver prefix if needed
    if raw_url.startswith("mysql://"):
        raw_url = raw_url.replace("mysql://", "mysql+pymysql://", 1)
    elif not raw_url.startswith("mysql+pymysql://"):
        # If missing driver entirely, prepend it (still safe to parse later)
        raw_url = f"mysql+pymysql://{raw_url.split('://')[-1]}"

    # Parse the URL
    parsed = urlparse(raw_url)
    username = quote_plus(parsed.username) if parsed.username else ""
    password = quote_plus(parsed.password) if parsed.password else ""
    netloc = f"{username}:{password}@{parsed.hostname}" if username or password else parsed.hostname
    if parsed.port:
        netloc += f":{parsed.port}"
    # Reconstruct URL with the possibly encoded credentials
    return urlunparse(("mysql+pymysql", netloc, parsed.path, "", "", ""))

# Load env vars (Railway may expose MYSQL_URL or DATABASE_URL)
raw_mysql = os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL") or os.getenv("MYSQL_PRIVATE_URL")
if not raw_mysql:
    raise EnvironmentError(
        "Database URL not found. Please set MYSQL_URL (or DATABASE_URL) in your environment or .env file."
    )

MYSQL_URL = normalize_mysql_url(raw_mysql)

print("Raw MYSQL_URL:", raw_mysql)
print("Normalized MYSQL_URL:", MYSQL_URL)

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