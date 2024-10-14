from python:3.12-slim
workdir /app

copy requirements.txt .
run pip install --no-cache-dir --timeout 1000 -r requirements.txt

copy . .

cmd streamlit run dashboard.py