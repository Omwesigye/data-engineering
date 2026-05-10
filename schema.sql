DROP TABLE IF EXISTS patent_companies CASCADE;
DROP TABLE IF EXISTS patent_inventors CASCADE;
DROP TABLE IF EXISTS patents CASCADE;
DROP TABLE IF EXISTS inventors CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

-- Patents table
CREATE TABLE patents (
    patent_id VARCHAR(100) PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    filing_date DATE,
    year INTEGER
);

-- Inventors table
CREATE TABLE inventors (
    inventor_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255),
    country VARCHAR(100)
);

-- Companies (assignees) table
CREATE TABLE companies (
    company_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255)
);

-- Relationship table: Patent to Inventors (many-to-many)
CREATE TABLE patent_inventors (
    patent_id VARCHAR(100),
    inventor_id VARCHAR(100),
    PRIMARY KEY (patent_id, inventor_id),
    FOREIGN KEY (patent_id) REFERENCES patents(patent_id) ON DELETE CASCADE,
    FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id) ON DELETE CASCADE
);

-- Relationship table: Patent to Companies (many-to-many)
CREATE TABLE patent_companies (
    patent_id VARCHAR(100),
    company_id VARCHAR(100),
    PRIMARY KEY (patent_id, company_id),
    FOREIGN KEY (patent_id) REFERENCES patents(patent_id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_patents_year ON patents(year);
CREATE INDEX idx_patents_filing_date ON patents(filing_date);
CREATE INDEX idx_inventors_country ON inventors(country);
CREATE INDEX idx_patent_inventors_patent ON patent_inventors(patent_id);
CREATE INDEX idx_patent_inventors_inventor ON patent_inventors(inventor_id);
CREATE INDEX idx_patent_companies_patent ON patent_companies(patent_id);
CREATE INDEX idx_patent_companies_company ON patent_companies(company_id);

-- Create view for easy patent summary
CREATE OR REPLACE VIEW patent_summary AS
SELECT 
    p.patent_id,
    p.title,
    p.year,
    COUNT(DISTINCT i.inventor_id) as inventor_count,
    COUNT(DISTINCT c.company_id) as company_count
FROM patents p
LEFT JOIN patent_inventors pi ON p.patent_id = pi.patent_id
LEFT JOIN inventors i ON pi.inventor_id = i.inventor_id
LEFT JOIN patent_companies pc ON p.patent_id = pc.patent_id
LEFT JOIN companies c ON pc.company_id = c.company_id
GROUP BY p.patent_id, p.title, p.year;

-- Comments omitted as MySQL uses table-level options instead.