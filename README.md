# acme-cert-check
TLS certificate expiration checker for hosts with modern TLS setups.

Intended usage is for ACME compatible CAs 
(e.g. [Let's Encrypt](https://letsencrypt.org)),
where certificates are short lived (90 days), and they should automatically
renew when they are about to expire (usually 30 days before expiry).

The script requires that you have Python 3.5 or later installed, and uses Python
[defaults](https://docs.python.org/3/library/ssl.html#ssl.create_default_context)
for TLS connections (i.e. no SSLv2 or SSLv3, only TLS is supported, etc)

The script is only usable on Linux or Unix like operating systems, and does not
write to standard output, unless an error is encountered. You could use cron to
run it and to send email in case of errors.

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

# domain expires in less than 30 days (default validity)
acme-cert-check.py -d example.net
example.net: Certificate is valid for 29 days

# domain name does not exist in DNS
acme-cert-check.py -d example.net
example.net: Error: [Errno -2] Name or service not known


```

## Parameters
\-d | --domain HOSTNAME\[:PORT]\[:ADDRESS]

  Domain name to check. If necessary, you can provide non standard port number
  or IP address to check cert (e.g. this is useful in situation when you have
  a proxy in front of your server, but still want to use/validate TLS cert)

\- t | --taks N

  How many parallel tasks to run when checking (helps with large number of
  domains).

\-x | --validity DAYS

  Minimum certificate validity  (30 days by default).

\- h | --help

  Show help message

\- v | --verbose

  Print domain name and validity during checks.

## Design

We've tried hard to make script as simple as possible, here are some design
decisions:

- The script doesn't write anything on standard output during normal operation
  and returns 0 on success.

- There is no provision to send email, use standard unix tools or cron for
  alerting.

- There are no provisions to directly configure TLS parameters (crypto is very
  complicated topic). Instead, we rely on Python3 defaults. The script uses
  CA bundle provided by your operating system (e.g. Mozilla/NSS CA certs),
  which means it should behave like a regular web browser when trusting
  certificates.

- Checking large number of domains can take a long time, mostly taken by
  networking stuff (DNS queries, TLS protocol handshake) and CPU intensive
  crypto. To speed up the process, you can use `-t|--tasks` parameter.

  For example, on my computer it takes 11 seconds to check 32 domains with
  cold DNS cache (6 seconds on second try), and 0.9 seconds with `-t 32`
  (0.5 seconds with warm DNS cache). Depending on your situation (number
  of domains and available CPU resources), you may need to experiment with
  this parameter to achieve best results.

  This feature requires Python 3.5 or later.

- It allows checking TLS certificates for a domain on a different IP from the
  DNS data. For example, you could have your domain protected by CloudFlare or
  similar service, but still want to configure proper TLS certs for your origin
  server.
