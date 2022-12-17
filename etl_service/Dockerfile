FROM python:3.10.8-slim

WORKDIR /opt/app

RUN groupadd -r dev && useradd -d /opt/app -r -g dev dev \
    && chown dev:dev -R /opt/app


COPY requirements.txt .

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chown -R dev:dev /opt/app

USER dev

CMD ["python", "/opt/app/main.py"]
