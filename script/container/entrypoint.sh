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
fi

if [ "${LE_PRODUCTION:-}" = "yes" ]; then
  SERVER_ARG=
else
  SERVER_ARG="--test-cert"
fi

printf "Issuing new certificate\n"
certbot certonly --manual --preferred-challenges=dns \
  --manual-auth-hook /app/certbot/auth.py \
  --manual-cleanup-hook /app/certbot/cleanup.py \
  -n --agree-tos --email "${EMAIL}" --manual-public-ip-logging-ok ${SERVER_ARG} \
  --domain pushbot.party \
  --domain api.pushbot.party

printf "Generating new Diffie-Helman parameters\n"
openssl dhparam -out /etc/letsencrypt/live/dhparams.pem 2048

printf "Creating certificate tarball\n"
cd /etc/letsencrypt/live/
tar zcvhf /out/tls-certificates.tar.gz dhparams.pem pushbot.party/*.pem
cd /app

printf "Encrypting tarball and uploading to S3\n"
python /app/certbot/upload.py

printf "Triggering an infrastructure build on Travis\n"
BODY='{
  "request": {
    "branch": "master",
    "config": {
      "merge_mode": "deep_merge",
      "env": [
        "BUILD_CAUSE=\"automatic TLS certificate renewal\""
      ]
    }
  }
}'

curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Travis-API-Version: 3" \
  -H "Authorization: token ${TRAVIS_TOKEN}" \
  -d "${BODY}" \
  https://api.travis-ci.org/repo/smashwilson%2Fazurefire-infra/requests
