# az-tls

A container that renews TLS certifications from Let's Encrypt via DNS verification when certificate expiration is near.

Environment variables accepted for configuration:

| Variable name | Description | Default |
| --- | --- | --- |
| `EMAIL` | Valid email address used to identify a Let's Encrypt account. | :star: **required** |
| `AZ_COORDINATOR_ADDR` | Protocol, hostname, and port used to communicate with an `az-coordinator` daemon. Format: `https://hostname.net:8443`. | :star: **required** |
| `AZ_COORDINATOR_TOKEN` | Authentication token to supply with `az-coordinator` requests. | :star: **required** |
| `FORCE` | If `"yes"`, a new certificate will be issued even if the current one has not expired. | _empty_ |
| `LE_PRODUCTION` | If `"yes"`, a production certificate will be issued instead of a staging one. | _empty_ |
