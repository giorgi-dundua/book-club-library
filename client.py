import requests
import streamlit as st

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


try:
    response = requests.get("http://127.0.0.1:8000/health", timeout=5)
    response.raise_for_status()
    with tab_health:
        if response.json() == {"status": "ok"}:
            st.success("API connected")
        else:
            st.error("Unexpected API response")
except requests.exceptions.Timeout:
    with tab_health:
        st.error("The request took too long")
except requests.exceptions.ConnectionError:
    with tab_health:
        st.error("Could not connect to the server")
except requests.exceptions.HTTPError as error:
    if error.response is not None:
        with tab_health:
            st.error(f"The server said no: {error.response.status_code}")
    else:
        with tab_health:
            st.error("An HTTP error occurred.")
except requests.exceptions.JSONDecodeError:
    with tab_health:
        st.error("The answer was not JSON")
except requests.exceptions.RequestException as error:
    with tab_health:
        st.error(f"Something else went wrong: {type(error).__name__}")
