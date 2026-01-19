FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for spatial libraries
RUN apt-get update && apt-get install -y \
    libspatialindex-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port (Render/Railway will provide PORT env var)
# Default to 5000 for local testing if not set
ENV PORT=5000
EXPOSE $PORT

# Run Gunicorn
# CMD uses shell form to allow variable expansion
CMD gunicorn --bind 0.0.0.0:$PORT app:app
