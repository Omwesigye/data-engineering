FROM python:3.11-slim

# Install system dependencies for MySQL and common Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose port (Render ignores this but it's good practice)
EXPOSE 10000

# Start the application using the dynamic PORT variable provided by Render
CMD ["sh", "-c", "streamlit run dashboard.py --server.port ${PORT:-10000} --server.address 0.0.0.0"]
