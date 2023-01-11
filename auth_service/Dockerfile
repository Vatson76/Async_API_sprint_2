FROM python:3.9

WORKDIR /opt/app

RUN groupadd -r dev && useradd -d /opt/src -r -g dev dev \
    && chown dev:dev -R /opt/src


COPY ./requirements.txt .
COPY ./run_app.sh .

RUN chmod +x run_app.sh

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY ./src .

RUN chown -R dev:dev /opt/src

USER dev

ENTRYPOINT ["./run_app.sh"]
