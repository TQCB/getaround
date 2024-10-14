from python:3.13-slim
workdir /app

# Install required python libraries
copy requirements.txt .
run pip install --no-cache-dir --timeout 100 -r /app/requirements.txt

# Copy the rest of our app files
copy . .

# Launch our app onto a gunicorn webserver
cmd gunicorn model_api:app --bind 0.0.0.0:$PORT --timeout 100 --worker-class uvicorn.workers.UvicornWorker