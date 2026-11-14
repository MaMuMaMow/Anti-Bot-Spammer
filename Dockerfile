FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && apt-get install -y --no-install-recommends libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY /src /app/src
COPY /requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN groupadd -g 10001 appgroup && useradd -m -u 10001 -g appgroup appuser

ENTRYPOINT [ "python", "/app/src/main.py" ]