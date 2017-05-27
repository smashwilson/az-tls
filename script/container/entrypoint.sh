#!/bin/sh

set -euo pipefail

if [ "${FORCE:-}" != "yes" ]; then
  printf "Checking current certificate's expiration date\n"
  EXPIRATION_DATE=$(
    echo |
    openssl s_client -connect pushbot.party:443 2>/dev/null |
    openssl x509 -noout -dates |
    grep notAfter
  )
  EXPIRATION_DATE="${EXPIRATION_DATE#notAfter=}"
  EXPIRATION_EPOCH=$(date +%s --date "${EXPIRATION_DATE}" -D '%b %e %H:%M:%S %Y')
  NOW_EPOCH=$(date +%s)

  let EXPIRATION_MS=EXPIRATION_EPOCH-NOW_EPOCH

  if [ "${EXPIRATION_MS}" -gt 604800 ]; then
    printf "Certificate expiration date %s is more than 7 days from now.\n" "${EXPIRATION_DATE}"
    printf "Doing nothing.\n"
    exit 0
  fi

  printf "Certificate expiration date %s is less than 7 days from now.\n" "${EXPIRATION_DATE}"
  exit 1
fi

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
