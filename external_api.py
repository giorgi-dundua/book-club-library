'''
Fetches book information from Open Library
Docs: https://openlibrary.org/docs#/
'''
import requests

OPEN_LIBRARY_BASE='https://openlibrary.org'

def search_info(keyword, filter='') -> dict:
    match filter:
        case 'isbn':
            return fetch_isbn(keyword).get('docs').pop(0)
        case 'title':
            return fetch_title(keyword).get('docs').pop(0)
        case 'author':
            return fetch_author(keyword).get('docs').pop(0)
        case _:
            return fetch_general(keyword).get('docs').pop(0)


def fetch_isbn(isbn: str) -> dict:
    endpoint = OPEN_LIBRARY_BASE+'/search.json?isbn={0}'.format(isbn)
    data = get_req_json(endpoint)
    return data


def fetch_title(title: str) -> dict:
    endpoint = OPEN_LIBRARY_BASE+'/search.json?title={0}'.format(title.lower().title())
    data = get_req_json(endpoint)
    return data


def fetch_author(author: str) -> dict:
    endpoint = OPEN_LIBRARY_BASE+'/search.json?author={0}'.format(author.lower().title())
    data = get_req_json(endpoint)
    return data


def fetch_general(search: str) -> dict:
    endpoint = OPEN_LIBRARY_BASE+'/search.json?q={0}'.format(search)
    data = get_req_json(endpoint)
    return data


def get_req_json(endpoint,params=None,headers=None,timeout=10):
    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print('The request timed out.')
    except requests.exceptions.ConnectionError:
        print('Could not connect to the server.')
    except requests.exceptions.HTTPError as error:
        print(f'The server gave an error: {error.response.status_code}')
    except requests.exceptions.JSONDecodeError:
        print('The returned data was not JSON format.')
    except requests.exceptions.RequestException as error:
        print(f'Something else went wrong: {type(error).__name__}')
    return None