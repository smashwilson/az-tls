FROM certbot/certbot:v0.24.0
LABEL maintainer "Ash Wilson"

RUN apk add --no-cache python3 openssl curl
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
ADD certbot /app/certbot/
ADD script/container /app/script/
RUN mkdir -p /out
WORKDIR /app

ENTRYPOINT ["/app/script/entrypoint.sh"]
