Patent DataPipeline

A big data project that extracts, transforms, and loads (ETL) patent data into a PostgreSQL database. It features robust analytics, automated reporting, and an interactive Streamlit dashboard to explore patent trends, top inventors, and leading innovative companies.

Project Architecture

1. ETL Pipeline: Processes large local `.tsv.zip` patent datasets up to one million rows in chunks to ensure low memory usage, applying necessary transformations and loading the data into PostgreSQL.
2. Database: PostgreSQL database holding normalized data (Patents, Inventors, Companies, and many-to-many relationships).
3. Analytics: Pre-configured SQL queries yielding actionable intelligence on yearly trends and top performers.
4. Dashboard: An interactive Streamlit frontend for data visualization.

 Getting Started

Follow these steps to set up the project on your local machine.

Prerequisites

Python 3.8+
MySQL Server

1. Clone the Repository
git clone <your-repository-url>
cd DataPipeline

 2. Set Up a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

python -m venv .venv
.venv\Scripts\activate
3. Install Dependencies

Install the required Python packages from `requirements.txt`:
pip install -r requirements.txt
 4. Database Configuration

1. Create a new PostgreSQL database for this project (e.g., `patent_db`).
2. Run the provided `schema.sql` script against your new database to create the necessary tables and indexes. You can do this via your preferred PostgreSQL client (e.g., PostgreSQL Workbench, DBeaver) or via the command line:
mysql -u your_username -p your_database_name < schema.sql

5. Environment Variables

Create a file named `.env` in the root of the project and add your PostgreSQL connection string.
6. Add Raw Data

The pipeline expects zipped TSV files from PatentsView. Create a folder named `raw` in the project root and place the following files inside:
- `g_patent.tsv.zip`
- `g_inventor_disambiguated.tsv.zip`
- `g_assignee_not_disambiguated.tsv.zip`
Run the ETL Pipeline

To extract the data from the `raw` directory, process it in chunks, and load it into your MySQL database:
python run_pipeline.py

Generate Analytics Reports

To run the predefined SQL queries, analyze the data, and export the results to CSV and JSON formats in the `output/` directory:

python reports.py

Navigate to the  URL provided in your terminal  to view the dashboard in your bowser.

GitHub Repository: https://github.com/Omwesigye/data-engineering.git

Dashboard url:  https://data-engineering-by23.onrender.com
