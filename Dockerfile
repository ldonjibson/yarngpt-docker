FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN git clone https://github.com/saheedniyi02/yarngpt.git /app/yarngpt

COPY models/ /app/models/
COPY app.py download_models.py /app/
RUN python download_models.py
RUN mkdir -p /app/output

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]