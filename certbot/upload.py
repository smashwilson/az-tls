#!/usr/bin/env python

import json
import urllib.request

password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
password_manager.add_password(None, os.environ['AZ_COORDINATOR_ADDR'], 'az-tls', os.environ['AZ_COORDINATOR_TOKEN'])
auth_handler = urllib.request.HTTPBasicAuthHandler(password_manager)
opener = urllib.request.build_opener(auth_handler)

tls_locations = {
    'TLS_DH_PARAMS': '/etc/letsencrypt/live/dhparams',
    'TLS_CERTIFICATE': '/etc/letsencrypt/live/backend.azurefire.net/fullchain.pem',
    'TLS_KEY': '/etc/letsencrypt/live/backend.azurefire.net/privkey.pem'
}

tls_secrets_payload = {}
for varname, filepath in tls_locations.items():
    with open(filepath, encoding='utf8') as f:
        tls_secrets_payload[varname] = f.read()

print('Uploading TLS certificate secrets to the coordinator')
secrets_req = urllib.request.Request(
    method='POST',
    url='{}/secrets'.format(os.environ['AZ_COORDINATOR_ADDR']),
    headers={'Content-Type': 'application/json'},
    data=json.dumps(tls_secrets_payload).encode('utf-8')
)
opener.open(secrets_req)

print('Triggering a coordinator sync')
sync_req = urllib.request.Request(
    method='POST',
    url='{}/sync'.format(os.environ(['AZ_COORDINATOR_ADDR']))
)
opener.open(sync_req)

print('Upload complete.')
