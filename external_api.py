'''
Fetches book information from Open Library
Docs: https://openlibrary.org/docs#/
'''
import requests
from datetime import datetime

from database import db_insert

OPEN_LIBRARY_BASE='https://openlibrary.org'

def search_info(keyword, filter) -> dict:
    match filter:
        case 'isbn':
            return fetch_isbn(keyword).get('docs').pop(0)
        case 'title':
            return fetch_title(keyword).get('docs').pop(0)
        case 'author':
            return fetch_author(keyword).get('docs').pop(0)
        case _:
            return fetch_general(keyword).get('docs').pop(0)

''' imports and running db_parse_and_add dependant on sqlite database implementation  '''
def db_parse_and_add(data) -> None:
    title = data.get('title')
    author_name = data.get('author_name')[0]
    published_year = data.get('first_publish_year')
    db_insert('INSERT INTO books (title, published) VALUES (?, ?)', title, datetime(published_year))
    db_insert('INSERT INTO authors (author_name) VALUES (?)', author)
    db_insert(  'INSERT INTO book_author (book_id, author_id) VALUES ('
                '(SELECT book_id FROM books WHERE title == ?),'
                '(SELECT author_id FROM authors WHERE author_name == ?))',
                title, author_name)

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