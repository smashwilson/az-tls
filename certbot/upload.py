#!/usr/bin/env python3

import os
import json
import urllib.request
import base64
import ssl
from pathlib import Path

ssl_context = ssl.create_default_context()
if os.environ.get('TRUST_LE_STAGING') == 'yes':
    ssl_context.load_verify_locations(
        cafile=Path(__file__).parent.resolve().joinpath('fakelerootx1.pem'),
    )

if os.environ.get('DANGER_DISABLE_CERT_CHECK') == 'yes':
    print('!!! Disabling TLS certification verification.')
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.VerifyMode.CERT_NONE

# debuglevel=10
log_handler = urllib.request.HTTPSHandler(context=ssl_context)
opener = urllib.request.build_opener(log_handler)

tls_locations = {
    'TLS_DH_PARAMS': '/etc/letsencrypt/live/dhparams.pem',
    'TLS_CERTIFICATE': '/etc/letsencrypt/live/backend.azurefire.net/fullchain.pem',
    'TLS_KEY': '/etc/letsencrypt/live/backend.azurefire.net/privkey.pem'
}

tls_secrets_payload = {}
for varname, filepath in tls_locations.items():
    with open(filepath, encoding='utf8') as f:
        tls_secrets_payload[varname] = f.read()

if os.environ.get('AZ_COORDINATOR_TOKEN') and os.environ['AZ_COORDINATOR_ADDR']:
    def generate_auth_header():
        pair = '{}:{}'.format('az-tls', os.environ['AZ_COORDINATOR_TOKEN']).encode('utf-8')
        return 'Basic {}'.format(base64.b64encode(pair).decode('utf-8'))

    auth_header = generate_auth_header()

    print('Uploading TLS certificate secrets to the coordinator')
    secrets_req = urllib.request.Request(
        method='POST',
        url='{}/secrets'.format(os.environ['AZ_COORDINATOR_ADDR']),
        headers={'Authorization': auth_header, 'Content-Type': 'application/json'},
        data=json.dumps(tls_secrets_payload).encode('utf-8')
    )
    opener.open(secrets_req)

    print('Triggering a coordinator sync')
    sync_req = urllib.request.Request(
        method='POST',
        headers={'Authorization': auth_header},
        url='{}/sync'.format(os.environ['AZ_COORDINATOR_ADDR'])
    )
    opener.open(sync_req)

    print('Upload complete.')
else:
    outfile = '/etc/letsencrypt/secrets.json'
    with open(outfile, mode='w', encoding='utf8') as outf:
        outf.write(json.dumps(tls_secrets_payload))
    print('Secrets written to file {}.'.format(outfile))
