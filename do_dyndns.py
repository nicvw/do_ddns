#!/usr/bin/env python3
"""."""
from argparse import ArgumentParser
import logging

from ipify import get_ip
from ipify.exceptions import IpifyException
from requests import get, post, put
from requests.utils import is_ipv4_address

DOMAIN_API_PATH = 'https://api.digitalocean.com/v2/domains/{}/records'


def _record_type(address):
    """Determing the record-type based on the type of IP address provided."""
    if is_ipv4_address(address):
        return 'A'
    return 'AAAA'


def _get_ids(domain, name, auth):
    """Fetch the ids for domain records matching name."""
    try:
        result = get(DOMAIN_API_PATH.format(domain), headers=auth)
        result = result.json()
    except ValueError:
        logging.error('unexpected response from %s', result.content)
        exit(1)
    logging.debug('domain records: %s', [x for x in result['domain_records'] if x['name'] == name])
    result = result['domain_records']
    return [x['id'] for x in result if x['name'] == name]


def _payload(name):
    """Generate the JSON payload for the update."""
    try:
        address = get_ip()
    except IpifyException:
        logging.error('unable to determing current address')
        exit(1)

    data = {
        'type': _record_type(address),
        'name': name,
        'data': address
    }
    return data


def _add_record(domain, name, auth):
    """Create a new record."""
    data = _payload(name)
    result = post(DOMAIN_API_PATH.format(domain), headers=auth, data=data).json()
    logging.info('added new record %s', result['domain_record'])


def _update_record(domain, name, pkid, auth):
    """Update an existing record."""
    data = _payload(name)
    url = DOMAIN_API_PATH.format(domain) + '/' + str(pkid)
    logging.debug('update url %s with %s', url, data)
    result = put(url, headers=auth, data=data).json()
    logging.info('updated record %s with %s', pkid,
                 {x: y for x, y in result['domain_record'].items() if y is not None})


def _oauth_header(token):
    return {'Authorization': 'Bearer ' + str(token)}


def _setup_logging(enable_informational_logging, enable_debug):
    if enable_debug is True:
        level = logging.DEBUG
    elif enable_informational_logging is True:
        level = logging.INFO
    else:
        level = logging.WARN
    logging.basicConfig(format='%(levelname)s: %(message)s', level=level)


def _arg_parser():
    parser = ArgumentParser()
    parser.add_argument('domain', help="the domain to be updated")
    parser.add_argument('name', help='the name of the record to be updated')
    parser.add_argument('headers', help='your api token from Digital Ocean', type=_oauth_header,
                        metavar='token')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true')
    group.add_argument('-d', '--debug', action='store_true')
    return parser.parse_args()


def _wrapper(domain, name, headers, verbose=False, debug=False):
    _setup_logging(verbose, debug)
    ids = _get_ids(domain, name, headers)
    if ids:
        logging.info('found %s records for %s.%s', len(ids), name, domain)
        for pkid in ids:
            _update_record(domain, name, pkid, headers)
    else:
        logging.info('no existing record found for %s.%s', name, domain)
        _add_record(domain, name, headers)


def main():
    """Entry point into __main__ execution."""
    args = _arg_parser()
    _wrapper(**(vars(args)))


if __name__ == '__main__':
    main()
