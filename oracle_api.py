import requests
from requests.auth import HTTPBasicAuth

from config import (
    ORACLE_BASE_URL,
    ORACLE_USERNAME,
    ORACLE_PASSWORD,
)


def get_oracle_data(endpoint, params=None):

    url = (
        f"{ORACLE_BASE_URL.rstrip('/')}/"
        f"{endpoint.lstrip('/')}"
    )

    headers = {
        "Accept": "application/json"
    }

    response = requests.get(
        url=url,
        auth=HTTPBasicAuth(
            ORACLE_USERNAME,
            ORACLE_PASSWORD
        ),
        headers=headers,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


def get_oracle_file_content(file_contents_url):

    # Convert relative Oracle URL to complete URL
    if file_contents_url.startswith("/"):
        url = (
            f"{ORACLE_BASE_URL.rstrip('/')}"
            f"{file_contents_url}"
        )
    else:
        url = file_contents_url

    response = requests.get(
        url=url,
        auth=HTTPBasicAuth(
            ORACLE_USERNAME,
            ORACLE_PASSWORD
        ),
        headers={
            "Accept": "*/*"
        },
        timeout=60
    )

    response.raise_for_status()

    return response