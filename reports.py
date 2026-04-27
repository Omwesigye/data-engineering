"""
Report generation module.
Creates console, CSV, and JSON reports from query results.
"""

import os
import json
from datetime import datetime
import pandas as pd
from typing import Dict
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate various report formats from patent analysis."""
    
    def __init__(self, query_results: Dict[str, pd.DataFrame]):
        """Initialize with query results."""
        self.results = query_results
        # Ensure output directory exists
        if hasattr(config, 'OUTPUT_DIR'):
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    def generate_console_report(self):
        """Print formatted report to console."""
        print("GLOBAL PATENT INTELLIGENCE REPORT")
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        
        # Total patents
        total_patents = self.results['yearly_trends']['patent_count'].sum() if not self.results['yearly_trends'].empty else 0
        print(f"\n TOTAL PATENTS: {total_patents:,}")
        
        # Top Inventors
     
        print(" TOP 10 INVENTORS")
        if not self.results['top_inventors'].empty:
            for idx, row in self.results['top_inventors'].head(10).iterrows():
                print(f"{idx+1:2d}. {row['name'][:40]:40s} - {row['patent_count']:5d} patents ({row['country']})")
        
        # Top Companies
        print(" TOP 10 COMPANIES")
        if not self.results['top_companies'].empty:
            for idx, row in self.results['top_companies'].head(10).iterrows():
                print(f"{idx+1:2d}. {row['name'][:40]:40s} - {row['patent_count']:5d} patents")
        
        # Top Countries
        print(" PATENTS BY COUNTRY")
        if not self.results['top_countries'].empty:
            for idx, row in self.results['top_countries'].head(10).iterrows():
                bar_length = int(row['percentage'] / 2)
                bar = " " * bar_length
                print(f"{row['country'][:20]:20s} {bar} {row['percentage']:5.1f}% ({row['patent_count']:,} patents)")
        
        # Yearly Trends
    
        print(" YEARLY PATENT TRENDS")
        if not self.results['yearly_trends'].empty:
            for _, row in self.results['yearly_trends'].head(10).iterrows():
                growth = row['yoy_growth'] if pd.notna(row['yoy_growth']) else 0
                growth_symbol = "+" if growth > 0 else "-" if growth < 0 else "="
                print(f"{int(row['year'])}: {row['patent_count']:6,} patents  {growth_symbol} {abs(growth):5.1f}%")
        
        # Performance Summary from CTE
        print(" INVENTOR PERFORMANCE INSIGHTS")
       
        if not self.results['cte_analysis'].empty:
            avg_patents = self.results['cte_analysis']['total_patents'].mean()
            above_avg = len(self.results['cte_analysis'][self.results['cte_analysis']['performance_category'] == 'Above Average'])
            print(f"Average patents per inventor: {avg_patents:.1f}")
            print(f"Above-average performers: {above_avg}")
            print(f"Top performer: {self.results['cte_analysis'].iloc[0]['name']} - {self.results['cte_analysis'].iloc[0]['total_patents']} patents")
    
        print("Report Complete")
    def generate_csv_reports(self):
        """Export specific reports to CSV files."""
        # Top inventors report
        if not self.results['top_inventors'].empty:
            self.results['top_inventors'].to_csv(f"{config.OUTPUT_DIR}/top_inventors.csv", index=False)
            logger.info("Saved top_inventors.csv")
        
        # Top companies report
        if not self.results['top_companies'].empty:
            self.results['top_companies'].to_csv(f"{config.OUTPUT_DIR}/top_companies.csv", index=False)
            logger.info("Saved top_companies.csv")
        
        # Country trends report
        if not self.results['top_countries'].empty:
            self.results['top_countries'].to_csv(f"{config.OUTPUT_DIR}/country_trends.csv", index=False)
            logger.info("Saved country_trends.csv")
    
    def generate_json_report(self):
        """Generate JSON format report."""
        # Prepare JSON structure
        total_patents = self.results['yearly_trends']['patent_count'].sum() if not self.results['yearly_trends'].empty else 0
        
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_patents": int(total_patents)
            },
            "top_inventors": [],
            "top_companies": [],
            "top_countries": [],
            "yearly_trends": [],
            "insights": {}
        }
        
        # Add top inventors
        if not self.results['top_inventors'].empty:
            for _, row in self.results['top_inventors'].head(10).iterrows():
                report["top_inventors"].append({
                    "name": row['name'],
                    "patents": int(row['patent_count']),
                    "country": row['country']
                })
        
        # Add top companies
        if not self.results['top_companies'].empty:
            for _, row in self.results['top_companies'].head(10).iterrows():
                report["top_companies"].append({
                    "name": row['name'],
                    "patents": int(row['patent_count'])
                })
        
        # Add country trends
        if not self.results['top_countries'].empty:
            for _, row in self.results['top_countries'].iterrows():
                report["top_countries"].append({
                    "country": row['country'],
                    "patents": int(row['patent_count']),
                    "share": float(row['percentage']) / 100
                })
        
        # Add yearly trends
        if not self.results['yearly_trends'].empty:
            for _, row in self.results['yearly_trends'].iterrows():
                report["yearly_trends"].append({
                    "year": int(row['year']),
                    "patents": int(row['patent_count']),
                    "growth": float(row['yoy_growth']) if pd.notna(row['yoy_growth']) else None
                })
        
        # Add insights from CTE
        if not self.results['cte_analysis'].empty:
            report["insights"] = {
                "average_patents_per_inventor": float(self.results['cte_analysis']['total_patents'].mean()),
                "most_prolific_inventor": {
                    "name": self.results['cte_analysis'].iloc[0]['name'],
                    "patents": int(self.results['cte_analysis'].iloc[0]['total_patents']),
                    "patents_per_year": float(self.results['cte_analysis'].iloc[0]['patents_per_year'])
                }
            }
        
        # Save JSON report
        with open(f"{config.OUTPUT_DIR}/report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("Saved report.json")
        return report
    
    def generate_all_reports(self):
        """Generate all report formats."""
        self.generate_console_report()
        self.generate_csv_reports()
        json_report = self.generate_json_report()
        return json_report

if __name__ == "__main__":
    # Example usage
    from sql_queries import PatentQueries
    queries = PatentQueries()
    results = queries.run_all_queries()
    reporter = ReportGenerator(results)
    reporter.generate_all_reports()