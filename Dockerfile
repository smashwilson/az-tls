FROM certbot/certbot:v0.36.0
LABEL maintainer "Ash Wilson"

RUN apk add --no-cache python3 openssl curl gcc g++ make libffi-dev openssl-dev python3-dev bash
ADD requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
ADD certbot /app/certbot/
ADD script/container /app/script/
RUN mkdir -p /out
WORKDIR /app

ENTRYPOINT ["/app/script/entrypoint.sh"]
