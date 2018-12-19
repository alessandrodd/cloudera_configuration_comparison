# WARNING: UGLY CODE

import os
import difflib
from configparser import ConfigParser
import requests
from requests.auth import HTTPBasicAuth
# from urlparse import urlparse  # Python 2
from urllib.parse import urlparse  # Python 3

config = ConfigParser()
config.read('config.ini')

address_a = config.get("cluster_a", "address")
username_a = config.get("cluster_a", "username")
password_a = config.get("cluster_a", "password")

address_b = config.get("cluster_b", "address")
username_b = config.get("cluster_b", "username")
password_b = config.get("cluster_b", "password")

services = config.get("main", "services").split(",")


def show_diff(text, n_text):
    """
    http://stackoverflow.com/a/788780
    Unify operations between two compared strings seqm is a difflib.
    SequenceMatcher instance whose a & b are strings
    """
    seqm = difflib.SequenceMatcher(None, text, n_text)
    output = []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append("<font color=red>^" + seqm.b[b0:b1] + "</font>")
        elif opcode == 'delete':
            output.append("<font color=blue>^" + seqm.a[a0:a1] + "</font>")
        elif opcode == 'replace':
            # seqm.a[a0:a1] -> seqm.b[b0:b1]
            output.append("<font color=green>^" + seqm.b[b0:b1] + "</font>")
        else:
            raise RuntimeError("unexpected opcode")
    return ''.join(output)


def _unidiff_output(expected, actual, fromfile, tofile):
    """
    Helper function. Returns a string containing the unified diff of two multiline strings.
    """

    import difflib
    expected = expected.splitlines(1)
    actual = actual.splitlines(1)

    diff = difflib.unified_diff(expected, actual, fromfile, tofile)

    return ''.join(diff)


url_a = address_a + "/api/v10/clusters/cluster/services/"
url_b = address_b + "/api/v10/clusters/cluster/services/"

for service in services:
    full_url_a = url_a+service+"/config?view=full"
    r = requests.get(full_url_a, auth=(username_a, password_a))
    if r.status_code != 200 and r.status_code != 404:
        print("ERROR: return code " + str(r.status_code) + " for " + full_url_a)
        continue
    a = r.text
    full_url_b = url_b+service+"/config?view=full"
    r = requests.get(full_url_b, auth=(username_b, password_b))
    if r.status_code != 200 and r.status_code != 404:
        print("ERROR: return code " + str(r.status_code) + " for " + full_url_b)
        continue
    b = r.text
    diff = _unidiff_output(a, b, full_url_a, full_url_b)
    print("************************************")
    print(service)
    print("************************************")
    print(diff)
    print("")
    parsed_uri = urlparse(url_a)
    netloc_a = parsed_uri.hostname
    parsed_uri = urlparse(url_b)
    netloc_b = parsed_uri.hostname
    comparisondir = netloc_a+"_"+netloc_b
    if not os.path.exists(comparisondir):
        os.makedirs(comparisondir)
    diff_file_path = os.path.join(comparisondir, service+".diff")
    with open(diff_file_path, "w") as df:
        df.write(diff)

    cfg_groups = set()
    full_url_a = url_a+service+"/roleConfigGroups"
    r = requests.get(full_url_a, auth=(username_a, password_a))
    if r.status_code != 200 and r.status_code != 404:
        print("ERROR: return code " + str(r.status_code) + " for " + full_url_a)
        continue
    data = r.json()
    for item in data["items"]:
        cfg_groups.add(item["name"])
    full_url_b = url_b+service+"/roleConfigGroups"
    r = requests.get(full_url_b, auth=(username_b, password_b))
    if r.status_code != 200 and r.status_code != 404:
        print("ERROR: return code " + str(r.status_code) + " for " + full_url_b)
        continue
    data = r.json()
    for item in data["items"]:
        cfg_groups.add(item["name"])

    for cfg_group in cfg_groups:
        full_url_a = url_a+service+"/roleConfigGroups/"+cfg_group
        r = requests.get(full_url_a, auth=(username_a, password_a))
        if r.status_code != 200 and r.status_code != 404:
            print("ERROR: return code " +
                  str(r.status_code) + " for " + full_url_a)
            continue
        a = r.text
        full_url_b = url_b+service+"/roleConfigGroups/"+cfg_group
        r = requests.get(full_url_b, auth=(username_b, password_b))
        if r.status_code != 200 and r.status_code != 404:
            print("ERROR: return code " +
                  str(r.status_code) + " for " + full_url_b)
            continue
        b = r.text
        diff = _unidiff_output(a, b, full_url_a, full_url_b)
        print("************************************")
        print(cfg_group)
        print("************************************")
        print(diff)
        print("")
        parsed_uri = urlparse(url_a)
        netloc_a = parsed_uri.hostname
        parsed_uri = urlparse(url_b)
        netloc_b = parsed_uri.hostname
        comparisondir = netloc_a+"_"+netloc_b
        if not os.path.exists(comparisondir):
            os.makedirs(comparisondir)
        diff_file_path = os.path.join(comparisondir, cfg_group+".diff")
        with open(diff_file_path, "w") as df:
            df.write(diff)
