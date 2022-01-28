FROM nvidia/cuda:11.1.1-base-ubuntu20.04

RUN apt-get update \
    && apt-get install \
    curl wget python3.8 \
    python3.8-distutils \
    python3-pip \
    curl wget -y \
    && rm -rf /var/lib/apt/lists/* 

# FastAPI section
# device env
ENV DEVICE="cuda"
# Copy and install requirements.txt
COPY ./requirements.txt ./requirements.txt
COPY ./src /app
COPY ./scripts/start.sh /start.sh
COPY ./scripts/gunicorn_conf.py /gunicorn_conf.py
# COPY ./scripts/start-reload.sh /start-reload.sh
# COPY ./scripts/prestart.sh /app
RUN mkdir -p /app/resources/model \
    && pip install --upgrade --no-cache-dir -r requirements.txt \
    && pip install --upgrade --no-cache-dir click==7.1.2 \
    && chmod +x /start.sh \
    && mkdir -p /app/results
ARG MODEL_PATH
# /home/huguetcabot/sentence_transformers/model_paraphrase_cross_WP2_MSWA
COPY ${MODEL_PATH}/* /app/resources/model/

WORKDIR /app

ENV PYTHONPATH=/app

EXPOSE 80

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]
