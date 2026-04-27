import sys
import os
import logging
from data_pipeline import PatentDataPipeline
from sql_queries import PatentQueries
from reports import ReportGenerator
import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():

    print(" GLOBAL PATENT INTELLIGENCE DATA PIPELINE")

    
    try:
        # Step 1: ETL Pipeline
        print("\n STEP 1: Running ETL Pipeline...")
        etl = PatentDataPipeline()
        etl.run_pipeline()
        
        # Step 2: Run Analytical Queries
        print("\n STEP 2: Running Analytical Queries...")
        queries = PatentQueries()
        results = queries.run_all_queries()
        
        # Step 3: Generate Reports
        print("\n STEP 3: Generating Reports...")
        reporter = ReportGenerator(results)
        reporter.generate_all_reports()
        
        print("\n PIPELINE COMPLETED SUCCESSFULLY!")
        print(f" All outputs saved to '{config.OUTPUT_DIR}/' directory")
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"\n Pipeline failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())