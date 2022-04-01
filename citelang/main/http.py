__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


from citelang.logger import logger
import os
import json
import requests
import time

default_headers = {"Accept": "application/json", "User-Agent": "citelang-python"}
params = {"per_page": 100}

api_key = os.environ.get("CITELANG_LIBRARIES_KEY")
if api_key:
    params.update({"api_key": api_key})


def check_response(typ, r, return_json=True, stream=False, retry=True):
    """
    Ensure the response status code is 20x
    """
    session = requests.session()

    # Rate is 60/minute
    if r.status_code == 429:
        logger.info("Exceeded API limit, sleeping 1 minute.")
        time.sleep(60)
        r = session.send(r.request)
        return check_response(typ, r, return_json, stream, retry=retry)

    if r.status_code == 401:
        logger.exit("You must set CITELAG_LIBRARIES_KEY in the environment.")

    if r.status_code not in [200, 201]:
        logger.exit(
            "Unsuccessful response: %s, %s %s" % (r.status_code, r.reason, r.text)
        )

    # All data is typically json
    if return_json and not stream:
        return r.json()
    return r


def print_response(r):
    """
    Print the result of a response
    """
    response = r.json()
    logger.info("%s: %s" % (r.url, json.dumps(response, indent=4)))


def do_request(
    typ,
    url,
    data=None,
    json=None,
    headers=None,
    return_json=True,
    stream=False,
):
    """
    Do a request (get, post, etc)
    """
    # If we have a cached token, use it!
    headers = headers or {}
    headers.update(default_headers)
    logger.info("%s %s" % (typ.upper(), url))

    # The first post when you upload the model defines the flavor (regression)
    if json:
        r = requests.request(
            typ, url, json=json, headers=headers, stream=stream, params=params
        )
    else:
        r = requests.request(
            typ, url, data=data, headers=headers, stream=stream, params=params
        )
    if not stream and not return_json:
        print_response(r)
    return check_response(typ, r, return_json=return_json, stream=stream)


def post(url, data=None, json=None, headers=None, return_json=True):
    """
    Perform a POST request
    """
    return do_request(
        "post", url, data=data, json=json, headers=headers, return_json=return_json
    )


def delete(url, data=None, json=None, headers=None, return_json=True):
    """
    Perform a DELETE request
    """
    return do_request(
        "delete",
        url,
        data=data,
        json=json,
        headers=headers,
        return_json=return_json,
    )


def get(url, data=None, json=None, headers=None, return_json=True, stream=False):
    """
    Perform a GET request
    """
    return do_request(
        "get",
        url,
        data=data,
        json=json,
        headers=headers,
        return_json=return_json,
        stream=stream,
    )
