#!/bin/bash
# Run the Streamlit dashboard

echo "🚀 Starting Patent Intelligence Dashboard..."
echo "📊 Dashboard will open in your browser shortly..."

# Run streamlit app
streamlit run dashboard.py --server.port 8501 --server.address localhost
