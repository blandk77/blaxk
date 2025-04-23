# Stage 1: Build multi-downloader-nx
FROM node:18 AS node-builder
WORKDIR /app/multi-downloader-nx
RUN npm install -g pnpm
RUN git clone https://github.com/anidl/multi-downloader-nx.git .
RUN pnpm install
RUN pnpm run tsc

# Stage 2: Final image
FROM python:3.9-slim
WORKDIR /app

# Install FFmpeg, MKVToolNix, and Node.js
RUN apt-get update && apt-get install -y \
    ffmpeg \
    mkvtoolnix \
    nodejs \
    npm \
    && apt-get clean


# Copy multi-downloader-nx
COPY --from=node-builder /app/multi-downloader-nx /app/multi-downloader-nx

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code and env
COPY main.py .
COPY .env .

# Command to run bot
CMD gunicorn app:app & python3 main.py
