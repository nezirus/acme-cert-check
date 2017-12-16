# acme-cert-check
TLS certificate expiration checker for hosts with modern TLS certs

Intended usage is for ACME compatible CAs (e.g. [Let's Encrypt][1]), where
certificates are short lived (90 days), and they should automatically renew
when they are about to expire (usually 30 days before expiry).

----------

## Parameters
\-d | --domain HOSTNAME\[:PORT]\[:ADDRESS]
: Domain name to check. If necessary, you can provide non standard port number
  or IP address to check cert (e.g. this is useful in situation when you have a proxy in front of your server, but still want to use/validate TLS cert)

\- t | --taks N
: How much parallel tasks to run when checking (helps with large number of
  domains).

\-x | --validity DAYS
: Minimum certificate validity  (30 days by default).

\- h | --help
: Show help message

\- v | --verbose
: Print domain name and validity during checks.

## Usage

```
# single domain
acme-cert-check.py -d example.net

# multiple domains
acme-cert-check.py -d first.example.net -d  second.example.net

# single domain from stdin
echo 'example.net' | acme-cert-check.py

# single or multiple domains from a file
cat domains.txt | acme-cert-check.py --tasks 8

# domain behind a proxy
acme-cert-check.py -d example.net::127.0.0.1

# domain behind a proxy, on custom port
acme-cert-check.py -d example.net:8443:127.0.0.1
```

[1] https://letsencrypt.org
