

from sqlalchemy import create_engine, text
import pandas as pd
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatentQueries:
    def __init__(self):
        """Initialize database connection."""
        db_url = config.MYSQL_URL
        self.engine = create_engine(db_url)
    
    def q1_top_inventors(self, limit: int = 10) -> pd.DataFrame:
        """Q1: Top inventors with most patents."""
        query = """
        SELECT 
            i.inventor_id,
            i.name,
            i.country,
            COUNT(DISTINCT pi.patent_id) as patent_count
        FROM inventors i
        JOIN patent_inventors pi ON i.inventor_id = pi.inventor_id
        GROUP BY i.inventor_id, i.name, i.country
        ORDER BY patent_count DESC
        LIMIT :limit
        """
        return pd.read_sql(text(query), self.engine, params={"limit": limit})
    
    def q2_top_companies(self, limit: int = 10) -> pd.DataFrame:
        query = """
        SELECT 
            c.company_id,
            c.name,
            COUNT(DISTINCT pc.patent_id) as patent_count
        FROM companies c
        JOIN patent_companies pc ON c.company_id = pc.company_id
        GROUP BY c.company_id, c.name
        ORDER BY patent_count DESC
        LIMIT :limit
        """
        return pd.read_sql(text(query), self.engine, params={"limit": limit})
    
    def q3_top_countries(self) -> pd.DataFrame:
        query = """
        SELECT 
            COALESCE(i.country, 'Unknown') as country,
            COUNT(DISTINCT pi.patent_id) as patent_count,
            ROUND(100.0 * COUNT(DISTINCT pi.patent_id) / SUM(COUNT(DISTINCT pi.patent_id)) OVER(), 2) as percentage
        FROM inventors i
        JOIN patent_inventors pi ON i.inventor_id = pi.inventor_id
        GROUP BY i.country
        ORDER BY patent_count DESC
        """
        return pd.read_sql(text(query), self.engine)
    
    def q4_trends_over_time(self) -> pd.DataFrame:
        """Q4: Patent trends by year."""
        query = """
        SELECT 
            p.year,
            COUNT(DISTINCT p.patent_id) as patent_count,
            LAG(COUNT(DISTINCT p.patent_id)) OVER (ORDER BY p.year) as previous_year_count,
            ROUND(100.0 * (COUNT(DISTINCT p.patent_id) - LAG(COUNT(DISTINCT p.patent_id)) OVER (ORDER BY p.year)) / 
                  NULLIF(LAG(COUNT(DISTINCT p.patent_id)) OVER (ORDER BY p.year), 0), 2) as yoy_growth
        FROM patents p
        WHERE p.year > 0
        GROUP BY p.year
        ORDER BY p.year DESC
        """
        return pd.read_sql(text(query), self.engine)
    
    def q5_join_query(self, limit: int = 20) -> pd.DataFrame:
        """Q5: JOIN query combining patents, inventors, and companies."""
        query = """
        SELECT 
            p.patent_id,
            p.title,
            p.year,
            GROUP_CONCAT(DISTINCT i.name SEPARATOR ', ') as inventors,
            GROUP_CONCAT(DISTINCT c.name SEPARATOR ', ') as assignees
        FROM patents p
        LEFT JOIN patent_inventors pi ON p.patent_id = pi.patent_id
        LEFT JOIN inventors i ON pi.inventor_id = i.inventor_id
        LEFT JOIN patent_companies pc ON p.patent_id = pc.patent_id
        LEFT JOIN companies c ON pc.company_id = c.company_id
        GROUP BY p.patent_id, p.title, p.year
        ORDER BY p.year DESC
        LIMIT :limit
        """
        return pd.read_sql(text(query), self.engine, params={"limit": limit})
    
    def q6_cte_query(self) -> pd.DataFrame:
        """Q6: CTE query for complex analysis of inventor productivity."""
        query = """
        WITH inventor_stats AS (
            SELECT 
                i.inventor_id,
                i.name,
                i.country,
                COUNT(DISTINCT pi.patent_id) as total_patents,
                COUNT(DISTINCT p.year) as active_years,
                MIN(p.year) as first_patent_year,
                MAX(p.year) as last_patent_year
            FROM inventors i
            JOIN patent_inventors pi ON i.inventor_id = pi.inventor_id
            JOIN patents p ON pi.patent_id = p.patent_id
            WHERE p.year > 0
            GROUP BY i.inventor_id, i.name, i.country
        ),
        ranked_inventors AS (
            SELECT 
                *,
                ROW_NUMBER() OVER (ORDER BY total_patents DESC) as rank_val,
                AVG(total_patents) OVER() as avg_patents
            FROM inventor_stats
        )
        SELECT 
            rank_val as `rank`,
            name,
            country,
            total_patents,
            active_years,
            ROUND(CAST(total_patents AS DECIMAL) / active_years, 2) as patents_per_year,
            CASE 
                WHEN total_patents > avg_patents THEN 'Above Average'
                ELSE 'Below Average'
            END as performance_category
        FROM ranked_inventors
        WHERE rank_val <= 20
        ORDER BY rank_val
        """
        return pd.read_sql(text(query), self.engine)
    
    def q7_ranking_query(self) -> pd.DataFrame:
        """Q7: Ranking inventors using window functions."""
        query = """
        SELECT 
            i.inventor_id,
            i.name,
            i.country,
            COUNT(DISTINCT pi.patent_id) as patent_count,
            RANK() OVER (ORDER BY COUNT(DISTINCT pi.patent_id) DESC) as `rank`,
            DENSE_RANK() OVER (ORDER BY COUNT(DISTINCT pi.patent_id) DESC) as `dense_rank`,
            PERCENT_RANK() OVER (ORDER BY COUNT(DISTINCT pi.patent_id) DESC) as `percent_rank`,
            NTILE(4) OVER (ORDER BY COUNT(DISTINCT pi.patent_id) DESC) as `quartile`
        FROM inventors i
        JOIN patent_inventors pi ON i.inventor_id = pi.inventor_id
        GROUP BY i.inventor_id, i.name, i.country
        ORDER BY patent_count DESC
        LIMIT 50
        """
        return pd.read_sql(text(query), self.engine)
    
    def run_all_queries(self) -> dict:
        """Execute all queries and return results."""
        logger.info("Executing all analytical queries...")
        
        results = {
            'top_inventors': self.q1_top_inventors(10),
            'top_companies': self.q2_top_companies(10),
            'top_countries': self.q3_top_countries(),
            'yearly_trends': self.q4_trends_over_time(),
            'joined_data': self.q5_join_query(20),
            'cte_analysis': self.q6_cte_query(),
            'ranked_inventors': self.q7_ranking_query()
        }
        
        # Save results to CSV
        for name, df in results.items():
            if not df.empty:
                df.to_csv(f"{config.OUTPUT_DIR}/{name}.csv", index=False)
                logger.info(f"Saved {name}.csv with {len(df)} rows")
        
        return results

if __name__ == "__main__":
    queries = PatentQueries()
    results = queries.run_all_queries()