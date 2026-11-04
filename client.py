import streamlit as st

from api_client import LibraryApiClient, LibraryApiError

PUBLISHED_YEAR_MIN = 1
PUBLISHED_YEAR_MAX = 9999

st.set_page_config(page_title="Book Club Library", layout="wide")

st.title("Book Club Library")
st.caption("UI prototype — Books tab uses sample data")

books = [
    {"ID": 1, "Title": "Dune", "Author": "Frank Herbert"},
    {"ID": 2, "Title": "Foundation", "Author": "Isaac Asimov"},
]

tab_health, tab_books, tab_manage, tab_loans, tab_stats = st.tabs(
    ["Health", "Books", "Manage books", "Loans", "Statistics"]
)

api = LibraryApiClient("http://127.0.0.1:8000")

with tab_books:
    search = st.text_input("Search by title")
    matches = [book for book in books if search.lower() in book["Title"].lower()]
    st.dataframe(matches, hide_index=True)

with tab_manage, st.form("add_book"):
    title = st.text_input("Title").strip()
    author = st.text_input("Author").strip()
    year_str = st.text_input("Published year (optional)").strip()

    if st.form_submit_button("Add book"):
        if not title:
            st.error("Enter a title")
        elif not author:
            st.error("Enter an author")
        else:
            year_int = None
            year_error = None
            if year_str:
                try:
                    year_int = int(year_str)
                    if not year_int in range(
                        PUBLISHED_YEAR_MIN, PUBLISHED_YEAR_MAX + 1
                    ):
                        year_error = f"Published year must be between {PUBLISHED_YEAR_MIN} and {PUBLISHED_YEAR_MAX}"

                except ValueError:
                    year_error = "Enter a whole-number year, or leave it blank"
            if year_error:
                st.error(year_error)
            else:
                try:
                    result = api.create_book(
                        title=title, authors=[author], published_year=year_int
                    )
                    st.info(
                        f"Book added successfully with ID {result['books'][0]['book_id']}"
                    )
                except LibraryApiError as error:
                    st.error(str(error))

with tab_loans:
    st.info("Borrow and return forms will be added here.")

with tab_stats:
    if st.button("Most borrowed"):
        try:
            result = api.get_most_borrowed_books()
            if result:
                st.dataframe(result, hide_index=True)
            else:
                st.info("No books in the catalogue")

        except LibraryApiError as error:
            st.error(str(error))

    if st.button("Never borrowed"):
        try:
            result = api.get_never_borrowed_books()
            if result:
                st.dataframe(result, hide_index=True)
            else:
                st.info("No never-borrowed books found")

        except LibraryApiError as error:
            st.error(str(error))


with tab_health:
    try:
        result = api.check_health()

        if result == {"status": "ok"}:
            st.success("API connected")
        else:
            st.error("Unexpected API response")

    except LibraryApiError as error:
        st.error(str(error))
