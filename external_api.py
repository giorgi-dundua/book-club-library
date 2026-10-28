'''
Fetches book information from Open Library
Docs: https://openlibrary.org/docs#/
'''
import requests
from datetime import datetime

from database import db_insert

''' Open Library API is slow so have to use a substantial timeout '''
OPEN_LIBRARY_BASE='https://openlibrary.org'
timeout_in_seconds = 5

def get_req_json(endpoint,params=None,headers=None,timeout=timeout_in_seconds) -> dict:
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

def fetch_isbn(isbn: str) -> dict:
    endpoint = OPEN_LIBRARY_BASE+'/search.json?isbn={0}'.format(isbn.strip())
    data = get_req_json(endpoint)
    return data

def fetch_title(title: str) -> dict:
    endpoint = OPEN_LIBRARY_BASE+'/search.json?title={0}'.format(title.strip().lower().title())
    data = get_req_json(endpoint)
    return data

def fetch_author(author: str) -> dict:
    endpoint = OPEN_LIBRARY_BASE+'/search.json?author={0}'.format(author.strip().lower().title())
    data = get_req_json(endpoint)
    return data

def fetch_general(search: str) -> dict:
    endpoint = OPEN_LIBRARY_BASE+'/search.json?q={0}'.format(search.strip())
    data = get_req_json(endpoint)
    return data

def search_info(keyword, filter) -> dict:
    ''' search by different filter, Open Library weighs relavancy so first element is usually correct '''
    match filter:
        case 'isbn':    return fetch_isbn(keyword).get('docs').pop(0)
        case 'title':   return fetch_title(keyword).get('docs').pop(0)
        case 'author':  return fetch_author(keyword).get('docs').pop(0)
        case _:         return fetch_general(keyword).get('docs').pop(0)

def parse_book_data(data) -> tuple:
    try:
        title = data.get('title')
        author_name = data.get('author_name')[0]
        published = datetime(data.get('first_publish_year'),1,1)
    except TypeError:
        print('Some data fields are missing or null')
    return (title, author_name, published)

''' imports and running db_add_book dependant on sqlite database implementation '''
def db_add_book(data) -> None:
    title, author_name, published = parse_book_data(data)
    db_insert('INSERT INTO books (title, published) VALUES (?, ?)', title, published)
    db_insert('INSERT INTO authors (author_name) VALUES (?)', author)
    ''' Not sure on a more elegant way to link in composite table ''' 
    db_insert(  'INSERT INTO book_author (book_id, author_id) VALUES ('
                '(SELECT book_id FROM books WHERE title == ?),'
                '(SELECT author_id FROM authors WHERE author_name == ?))',
                title, author_name)