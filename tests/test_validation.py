from datetime import datetime, timedelta
from database import db_select, db_insert, db_delete, db_update, validate_loan, validate_return

one_per_book = 'SELECT COUNT(*) FROM loans WHERE return_date IS NULL GROUP BY book_id'
delete_loan = 'DELETE FROM loans WHERE member_id == ? AND book_id == ?'
insert = 'INSERT INTO loans (member_id, book_id, loan_date, due_date) VALUES (?, ?, ?, ?)'
select = 'SELECT * FROM loans WHERE member_id == ? AND book_id == ?'
select_not_returned = 'SELECT * FROM loans WHERE member_id == ? AND book_id == ? AND return_date IS NULL'
update = 'UPDATE loans SET return_date = ? WHERE member_id == ? AND book_id == ?'
member_id, book_id = 900, 900

# not adding author because not needed for current test. using fixed id to be able to delete after test.
add_member = 'INSERT INTO members (member_id, member_name, email, phone, joined) VALUES (?, ?, ?, ?, ?)'
add_book = 'INSERT INTO books (book_id, title, published) VALUES (?, ?, ?)'
delete_member = 'DELETE FROM members WHERE member_id == ?'
delete_book = 'DELETE FROM books WHERE book_id == ?'

def build_test_subjects():
    db_insert(add_member, member_id, 'Test Member', 'test@test.com', '555-123456', datetime(2000, 1, 1))
    db_insert(add_book, book_id, 'Test Book', datetime(2000, 1, 1))

def remove_test_subjects():
    db_delete(delete_loan, member_id, book_id)
    db_delete(delete_member, member_id)
    db_delete(delete_book, book_id)

def test_one_loan_per_book():
    assert all(count[0] == 1 for count in db_select(one_per_book))

def test_second_loan_on_active_rejected():
    build_test_subjects()
    db_delete(delete_loan, member_id, book_id)
    assert not db_select(select, member_id, book_id)
    assert validate_loan(book_id)
    db_insert(insert, member_id, book_id, datetime.now(), datetime.now()+timedelta(days=14))
    assert db_select(select, member_id, book_id)
    assert not validate_loan(book_id)
    ''' IntegrityError, second loan rejected '''
    db_insert(insert, member_id, book_id, datetime.now(), datetime.now()+timedelta(days=14))
    assert len(db_select(select, member_id, book_id)) == 1
    remove_test_subjects()

def test_returned_book_can_loan_after():
    build_test_subjects()
    db_delete(delete_loan, member_id, book_id)
    assert not db_select(select, member_id, book_id)
    db_insert(insert, member_id, book_id, datetime.now(), datetime.now()+timedelta(days=14))
    assert db_select(select, member_id, book_id)
    assert validate_return(member_id, book_id)
    db_update(update, datetime.now(), member_id, book_id)
    assert not db_select(select_not_returned, member_id, book_id)
    assert validate_loan(book_id)
    db_insert(insert, member_id, book_id, datetime.now(), datetime.now()+timedelta(days=14))
    assert db_select(select, member_id, book_id)
    remove_test_subjects()