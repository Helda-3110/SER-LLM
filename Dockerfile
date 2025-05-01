# Base image with Python 3.7
FROM python:3.7-slim

# Set working directory
WORKDIR /app

# System dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    libasound-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files into container
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Streamlit configuration
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
