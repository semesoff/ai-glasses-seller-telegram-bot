FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/piper:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates espeak-ng ffmpeg unzip wget \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/models \
    && wget -q https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip -O /tmp/vosk-model-small-ru-0.22.zip \
    && unzip -q /tmp/vosk-model-small-ru-0.22.zip -d /app/models \
    && rm /tmp/vosk-model-small-ru-0.22.zip

RUN wget -q https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz -O /tmp/piper_linux_x86_64.tar.gz \
    && tar -xzf /tmp/piper_linux_x86_64.tar.gz -C /opt \
    && ln -s /opt/piper/piper /usr/local/bin/piper \
    && mkdir -p /app/models/piper \
    && wget -q https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx -O /app/models/piper/ru_RU-dmitri-medium.onnx \
    && wget -q https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx.json -O /app/models/piper/ru_RU-dmitri-medium.onnx.json \
    && rm /tmp/piper_linux_x86_64.tar.gz

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .

CMD ["python", "-m", "app.main"]
