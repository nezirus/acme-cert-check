#!/usr/bin/env python3

# Copyright (c) 2017, Adis Nezirović <nezirus at gmail.com>
# Licensed under the terms of GNU GPL version 3 or later

import sys
import ssl
from argparse import ArgumentParser, Namespace
from datetime import datetime, timedelta
from select import select
from asyncio import gather, get_event_loop, open_connection
import functools


default_conf = Namespace(tasks=1, validity=30, domains=None)
epilog = 'Note: You can provide a list of domains (one per line) on STDIN'


def cli_parser(conf):
    parser = ArgumentParser(description='TLS certificate checker',
                            epilog=epilog)
    parser.add_argument('-d', '--domain', dest='domains',
                        metavar='HOSTNAME:PORT:ADDRESS',
                        help='Domain name (port and address are optional)',
                        action='append',
                        default=[])
    parser.add_argument('-t', '--tasks',
                        help='how many tasks to run in parallel',
                        default=conf.tasks, type=int)
    parser.add_argument('-x', '--validity',
                        help='minimum validity in days ({} by default)'.
                        format(conf.validity),
                        default=conf.validity, type=int)
    parser.add_argument('-v', '--verbose', help='show check results',
                        action='store_true', default=False)

    return parser, parser.parse_args()


def parse_timestamp(timestamp):
    return datetime.strptime(timestamp, '%b %d %H:%M:%S %Y %Z')


def slice_list(items, tasks):
    assert(tasks > 0)
    size = len(items)
    mod = size % tasks
    ratio = size // tasks

    for i in range(0, ratio):
        yield items[i*tasks:(i+1)*tasks]

    if mod > 0:
        yield items[(size-mod):]


async def check_domain(conf, loop, d):
    ctx = ssl.create_default_context()
    now = datetime.utcnow()

    if d.count(':') < 2:
        d = d + (2-d.count(':'))*':'

    hostname, port, address = d.split(':', 2)

    if port == '':
        port = 443

    try:
        port = int(port)
    except ValueError:
        print('{}: Invalid port number in \'{}\''.format(hostname, d),
              file=sys.stderr)
        return

    if address == '':
        address = hostname

    try:
        reader, writer = await open_connection(address, port,
                                               server_hostname=hostname,
                                               ssl=ctx, loop=loop)
    except ssl.SSLError as e:
        print('{}: SSL error: {}'.format(hostname, e), file=sys.stderr)
        return
    except OSError as e:
        print('{}: Error: {}'.format(hostname, e), file=sys.stderr)
        return

    cert = writer.get_extra_info('peercert')
    writer.close()

    try:
        before = parse_timestamp(cert['notBefore'])
        after = parse_timestamp(cert['notAfter'])
    except ValueError as e:
        print('{}: Could not parse cert date'.format(hostname),
              file=sys.stderr)
        return

    if now < before or now + timedelta(days=conf.validity) > after:
        if now < before or now > after:
            print('{}: Certificate expired', file=sys.stderr)
        else:
            t = after - now
            print('{}: Certificate is valid for {} days'.format(hostname,
                  t.days), file=sys.stderr)
        return

    if conf.verbose:
        t = after - now
        print('{}: Valid for {} days'.format(hostname, t.days))


if __name__ == '__main__':
    parser, conf = cli_parser(default_conf)

    if select([sys.stdin], [], [], 0.0)[0]:
        for line in sys.stdin:
            conf.domains.append(line.strip())

    if conf.domains:
        loop = get_event_loop()
        f = functools.partial(check_domain, conf, loop)
        for d in slice_list(conf.domains, conf.tasks):
            coros = [f(x) for x in d]
            loop.run_until_complete(gather(*coros))

        loop.close()
    else:
        parser.print_help()
