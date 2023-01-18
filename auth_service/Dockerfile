FROM python:3.9

ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240

WORKDIR /opt/app

RUN groupadd -r dev && useradd -d /opt/app -r -g dev dev \
    && chown dev:dev -R /opt/app


COPY ./requirements.txt .
COPY ./src/run_uwsgi.sh .

RUN chmod +x run_uwsgi.sh

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY ./migrations ./migrations
COPY ./src .

USER dev

ENTRYPOINT ["./run_uwsgi.sh"]
