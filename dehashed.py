#!/usr/bin/env python3

"""
curl --silent -v  https://api.dehashed.com/search?query=\"$1\"
-u  lol@protonmail.com:a566b322da771a58233403bd53123
-H 'Accept: application/json'

./dehashed.py -q "email:'bob@acme.com.com'" -L
"""

import argparse
import requests
import json
from colorama import Fore, Style, init
init(autoreset=True)
from requests.auth import HTTPBasicAuth

email = '<YOURE DEHASHED ACCOUNT EMAIL'
key = '<DESHASHED APY KEY>'


def write_output(data):
    with open(outfile, 'a') as of:
        of.write(str(data) + "\n")

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


def query_api(query):
    """
    Query the dehashed API
    :param query: query string
    :return: html content
    """
    headers_dict = {'Accept': 'application/json'}
    if loose:
        url = f'https://api.dehashed.com/search?query={query}'
    else:
        url = f'https://api.dehashed.com/search?query="{query}"'

    if torify:
        session = get_tor_session()
        res = session.get(url=url, headers=headers_dict, auth=HTTPBasicAuth(email, key))
    else:
        res = requests.get(url=url, headers=headers_dict, auth=HTTPBasicAuth(email, key))
    if res.status_code == 200:
        return res.content
    else:
        print(Fore.RED + f'Error {res.status_code} in querying api.')
        if verbose:
            print(f'{res.content}')
        return None


def pp_json(json_data, sort=True, indents=4):
    """
    Pretty Json

    :param json_data: json data
    :param sort: sort fields
    :param indents: number of idents
    :return: --
    """
    if type(json_data) is str:
        data = json.dumps(json.loads(json_data), sort_keys=sort, indent=indents)
        print(data)
        if outfile:
            write_output(data=data)
    else:
        data = json.dumps(json_data, sort_keys=sort, indent=indents)
        print(data)
        if outfile:
            write_output(data=data)
    return None


def parse_out(json_data):
    final = ""
    json_data = json.loads(json_data)
    for i in json_data['entries'].__iter__():
        for x in i.keys():
            print(x + ' : ' + str(i[x]))
            final += str(x) + ' : ' + str(i[x]) + str('\n')
        print('\n')
    if outfile:
        write_output(final)

def main():
    """
    Program main logic
    :return:
    """
    parser = argparse.ArgumentParser(usage='Tool to query the dehashed api.')
    parser.add_argument('-q', '--query', dest='query', type=str, help='Single query')
    parser.add_argument('-l', '--list', dest='query_list', type=str, default=None, help='List of queries to run.')
    parser.add_argument('-p', '--pretty', dest='pretty_out', action='store_true', default=False,
                        help='Prettify the output so it is super skid friendly and cute.')
    parser.add_argument('-o', '--out_file', dest='out_file', default=None, type=str, help='Save output to this file.')
    parser.add_argument('-L', '--loose', dest='loose', action='store_true', default=False, help='Use loose search.')
    parser.add_argument('-t', '--torify', dest='torify', default=False, action='store_true', help='Use local tor proxy')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Increase verbosity.')
    args = parser.parse_args()
    global verbose
    global torify
    global pretty_out
    global loose
    global outfile
    verbose = args.verbose
    query = args.query
    query_list = args.query_list
    torify = args.torify
    pretty_out = args.pretty_out
    loose = args.loose
    outfile = args.out_file

    if query:
        ret = query_api(query)
        if ret:
            ret = ret.decode()
            if pretty_out:
                parse_out(ret)
            else:
                pp_json(ret)
    if query_list:
        with open(query_list, 'r') as ql:
            ql = ql.readlines()
            for line in ql:
                line = line.strip("\n\r")
                ret = query_api(line)
                if pretty_out:
                    parse_out(ret)
                else:
                    pp_json(ret)

    if not query or query_list:
        print(Fore.RED + 'Please supply either a query or query list. --help for usage.')
        exit(1)


if __name__ == '__main__':
    main()
