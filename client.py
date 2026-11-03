import requests
import streamlit as st

from api_client import LibraryApiClient

st.set_page_config(page_title="Book Club Library", layout="wide")

st.title("Book Club Library")
st.caption("UI prototype — sample book data; API health check connected")

books = [
    {"ID": 1, "Title": "Dune", "Author": "Frank Herbert"},
    {"ID": 2, "Title": "Foundation", "Author": "Isaac Asimov"},
]

tab_health, tab_books, tab_manage, tab_loans, tab_stats = st.tabs(
    ["Health", "Books", "Manage books", "Loans", "Statistics"]
)

with tab_books:
    search = st.text_input("Search by title")
    matches = [book for book in books if search.lower() in book["Title"].lower()]
    st.dataframe(matches, hide_index=True)

with tab_manage, st.form("add_book"):
    title = st.text_input("Title")
    author = st.text_input("Author")
    if st.form_submit_button("Add book"):
        st.info("Prototype only — saving will use the API.")

with tab_loans:
    st.info("Borrow and return forms will be added here.")

with tab_stats:
    st.metric("Books in sample catalogue", len(books))

api = LibraryApiClient("http://127.0.0.1:8000")

with tab_health:
    try:
        result = api.check_health()

        if result == {"status": "ok"}:
            st.success("API connected")
        else:
            st.error("Unexpected API response")

    except requests.exceptions.Timeout:
        st.error("The request took too long")

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the server")

    except requests.exceptions.HTTPError as error:
        status = error.response.status_code
        st.error(f"API returned HTTP {status}")

    except requests.exceptions.JSONDecodeError:
        st.error("The response was not valid JSON")

    except requests.exceptions.RequestException as error:
        st.error(f"Request failed: {error}")
