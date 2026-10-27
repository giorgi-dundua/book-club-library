'''
Fetches book information from Open Library
Docs: https://openlibrary.org/docs#/
'''
import requests

OPEN_LIBRARY_BASE='https://openlibrary.com'

def get_req_json(endpoint,params=None,headers=None,timeout=1):
    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print('The request timed out.',response.url)
    except requests.exceptions.ConnectionError:
        print('Could not connect to the server.')
    except requests.exceptions.HTTPError as error:
        print(f'The server gave an error: {error.response.status_code}')
    except requests.exceptions.JSONDecodeError:
        print('The returned data was not JSON format.')
    except requests.exceptions.RequestException as error:
        print(f'Something else went wrong: {type(error).__name__}')
    return None