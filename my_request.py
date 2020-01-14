import requests


def short_request(sci_url, login, password):
    try:
        request = requests.get(sci_url, verify=True, auth=(login, password))
        return request.content
    except requests.exceptions.RequestException as e:
        print(e)
