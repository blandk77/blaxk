# Stage 1: Build multi-downloader-nx
FROM node:18 AS node-builder
WORKDIR /app/multi-downloader-nx
RUN git clone https://github.com/anidl/multi-downloader-nx.git .
RUN npm install && npm run tsc

# Stage 2: Final image
FROM python:3.9-slim
WORKDIR /app

# Install FFmpeg and MKVToolNix
RUN apt-get update && apt-get install -y ffmpeg mkvtoolnix && apt-get clean

# Install Node.js
RUN apt-get install -y nodejs npm

# Copy multi-downloader-nx
COPY --from=node-builder /app/multi-downloader-nx /app/multi-downloader-nx

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .
COPY .env .

# Command to run bot
CMD gunicorn app:app & python3 bot.py
