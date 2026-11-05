import streamlit as st

from api_client import LibraryApiClient, LibraryApiError

PUBLISHED_YEAR_MIN = 1
PUBLISHED_YEAR_MAX = 9999

st.set_page_config(page_title="Book Club Library", layout="wide")

st.title("Book Club Library")

tab_health, tab_books, tab_manage, tab_members, tab_loans, tab_stats = st.tabs(
    ["Health", "Books", "Manage books", "Members", "Loans", "Statistics"]
)

api = LibraryApiClient("http://127.0.0.1:8000")

with tab_health:
    try:
        result = api.check_health()

        if result == {"status": "ok"}:
            st.success("API connected")
        else:
            st.error("Unexpected API response")

    except LibraryApiError as error:
        st.error(str(error))

with tab_books:
    with st.form("browse_books"):
        search = st.text_input("Search by title (optional)").strip()
        if st.form_submit_button("Show books"):
            try:
                result = api.get_books(search)
                if result:
                    st.dataframe(result, hide_index=True)
                else:
                    st.info("No books found")
            except LibraryApiError as error:
                st.error(str(error))

    with st.form("find_book"):
        book_id = st.number_input("Book ID", min_value=1, step=1)
        if st.form_submit_button("Find book"):
            try:
                result = api.get_book(book_id)
                if result:
                    st.dataframe([result], hide_index=True)
            except LibraryApiError as error:
                st.error(str(error))


with tab_manage, st.form("add_book"):
    st.subheader("Add book")
    title = st.text_input("Title").strip()
    authors = [
        line.strip()
        for line in st.text_area("Authors (one per line)").splitlines()
        if line.strip()
    ]
    year_str = st.text_input("Published year (optional)").strip()

    if st.form_submit_button("Add book"):
        if not title:
            st.error("Enter a title")
        elif not authors:
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
                        title=title, authors=authors, published_year=year_int
                    )
                    st.info(
                        f"Book added successfully with ID {result['books'][0]['book_id']}"
                    )
                except LibraryApiError as error:
                    st.error(str(error))

with tab_manage, st.form("edit_book"):
    st.subheader("Edit book")
    st.caption("Leave fields blank to keep their current values")
    book_id = st.number_input("Book ID", min_value=1, step=1)
    title = st.text_input("Title").strip()
    authors = [
        line.strip()
        for line in st.text_area("Authors (complete list, one per line)").splitlines()
        if line.strip()
    ]
    year_str = st.text_input("Published year").strip()
    clear_year = st.checkbox("Clear publication year")

    if st.form_submit_button("Update book"):
        changes = {}
        if title:
            changes["title"] = title
        if authors:
            changes["authors"] = authors

        year_error = None
        if clear_year and year_str:
            year_error = "Leave the year blank when clearing it"
        elif clear_year:
            changes["published_year"] = None
        elif year_str:
            try:
                year_int = int(year_str)
                if not PUBLISHED_YEAR_MIN <= year_int <= PUBLISHED_YEAR_MAX:
                    year_error = f"Published year must be between {PUBLISHED_YEAR_MIN} and {PUBLISHED_YEAR_MAX}"
                else:
                    changes["published_year"] = year_int
            except ValueError:
                year_error = "Enter a whole-number year, or leave it blank"

        if year_error:
            st.error(year_error)
        elif not changes:
            st.info("Enter at least one change")
        else:
            try:
                result = api.patch_book(book_id, changes)
                st.success(f"Book {result['book_id']} updated successfully")
            except LibraryApiError as error:
                st.error(str(error))

with tab_manage, st.form("delete_book"):
    if "delete_candidate" not in st.session_state:
        st.session_state["delete_candidate"] = None
    st.subheader("Delete book")
    message = st.session_state.pop("delete_success", None)
    if message is not None:
        st.success(message)
    st.caption("Enter a book ID and find the book first")
    book_id = st.number_input("Book ID", min_value=1, value=None, step=1)
    if st.form_submit_button("Find book"):
        st.session_state["delete_confirmed"] = False
        if not book_id:
            st.warning("Enter a book ID")
        else:
            try:
                result = api.get_book(book_id)
                st.session_state["delete_candidate"] = result
            except LibraryApiError as error:
                st.error(str(error))
                st.session_state["delete_candidate"] = None
    candidate = st.session_state["delete_candidate"]
    if candidate is not None:
        st.dataframe([candidate], hide_index=True)
        confirmed_delete = st.checkbox(
            "I confirm that I want to delete the book", key="delete_confirmed"
        )

    if st.form_submit_button("Delete book"):
        if not candidate:
            st.warning("Find the book first")
        else:
            if candidate["book_id"] != book_id:
                st.warning("The ID changed. Find the book again")
            else:
                if confirmed_delete:
                    try:
                        api.delete_book(candidate["book_id"])
                        st.session_state["delete_success"] = (
                            f"Book with ID {book_id} deleted"
                        )

                        st.session_state["delete_candidate"] = None
                        st.rerun()
                    except LibraryApiError as error:
                        st.error(str(error))
                else:
                    st.warning("Please check the confirmation box to enable deletion")

with tab_members:
    st.info("Library Member Information")
    if st.button("Show members"):
        try:
            result = api.get_members_personal_data()
            if result["members"]:
                st.dataframe(result["members"], hide_index=True)
            else:
                st.info("No members found")

        except LibraryApiError as error:
            st.error(str(error))

    with st.form("find_member"):
        st.info("Find Member by ID")
        member_id = st.number_input("Member ID", min_value=1, value=None, step=1)
        if st.form_submit_button("Find member"):
            if member_id is None:
                st.warning("Enter a member ID")
            else:
                try:
                    result = api.get_member_personal_data(member_id)
                    st.dataframe([result], hide_index=True)
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
