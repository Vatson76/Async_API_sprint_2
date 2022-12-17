FROM python:3.10.8-slim

RUN apt update
RUN apt -y install gcc

WORKDIR /opt/app

RUN apt-get update && apt-get install -y gettext

RUN groupadd -r dev && useradd -d /opt/app -r -g dev dev \
    && chown dev:dev -R /opt/app

ENV DJANGO_SETTINGS_MODULE 'config.settings'
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240

COPY requirements.txt .

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod -R +rw /opt/app/movies/locale
RUN chmod +x run_uwsgi.sh
RUN chown dev:dev /var/log
RUN chown -R dev:dev /opt/app

USER dev

EXPOSE 8000

CMD ["./run_uwsgi.sh"]
