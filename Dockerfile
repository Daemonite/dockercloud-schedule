FROM gliderlabs/alpine:3.1

RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base \
    supervisor \
  && rm -rf /var/cache/apk/*

COPY code/requirements.txt /code/requirements.txt
COPY config/supervisord.conf /etc/supervisord.conf
WORKDIR /code
RUN pip install -r requirements.txt

COPY code/dc-schedule.py /code/dc-schedule.py

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
