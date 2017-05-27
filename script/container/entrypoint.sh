#!/bin/sh

set -euo pipefail

# TODO: use openssl to verify that the certificate needs renewal

printf "Issuing new certificate\n"
certbot certonly --manual --preferred-challenges=dns \
  --manual-auth-hook /app/certbot/auth.py \
  --manual-cleanup-hook /app/certbot/cleanup.py \
  -n --agree-tos --manual-public-ip-logging-ok --email "${EMAIL}" \
  --test-cert \
  --domain pushbot.party \
  --domain api.pushbot.party

printf "Creating certificate tarball\n"
cd /etc/letsencrypt/live/
tar zcvf /out/tls-certificates.tar.gz pushbot.party/*.pem
cd /app

printf "Encrypting tarball and uploading to S3\n"
python /app/certbot/upload.py
