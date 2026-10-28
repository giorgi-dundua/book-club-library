from datetime import datetime, timedelta
from database import db_select, db_insert, db_delete, db_update, validate_loan, validate_return

one_per_book = 'SELECT COUNT(*) FROM loans WHERE return_date IS NULL GROUP BY book_id'
delete = 'DELETE FROM loans WHERE member_id == ? AND book_id == ?'
insert = 'INSERT INTO loans (member_id, book_id, loan_date, due_date) VALUES (?, ?, ?, ?)'
select = 'SELECT * FROM loans WHERE member_id == ? AND book_id == ?'
select_not_returned = 'SELECT * FROM loans WHERE member_id == ? AND book_id == ? AND return_date IS NULL'
update = 'UPDATE loans SET return_date = ? WHERE member_id == ? AND book_id == ?'
member_id, book_id = 5, 5

def test_one_loan_per_book():
    assert all(count[0] == 1 for count in db_select(one_per_book))

def test_second_loan_on_active_rejected():
    db_delete(delete, member_id, book_id)
    assert not db_select(select, member_id, book_id)
    assert validate_loan(book_id)
    db_insert(insert, member_id, book_id, datetime.now(), datetime.now()+timedelta(days=14))
    assert db_select(select, member_id, book_id)
    assert not validate_loan(book_id)
    ''' IntegrityError, second loan rejected '''
    db_insert(insert, member_id, book_id, datetime.now(), datetime.now()+timedelta(days=14))
    assert len(db_select(select, member_id, book_id)) == 1

def test_returned_book_can_loan_after():
    db_delete(delete, member_id, book_id)
    assert not db_select(select, member_id, book_id)
    db_insert(insert, member_id, book_id, datetime.now(), datetime.now()+timedelta(days=14))
    assert db_select(select, member_id, book_id)
    assert validate_return(member_id, book_id)
    db_update(update, datetime.now(), member_id, book_id)
    assert not db_select(select_not_returned, member_id, book_id)
    assert validate_loan(book_id)
    db_insert(insert, member_id, book_id, datetime.now(), datetime.now()+timedelta(days=14))
    assert db_select(select, member_id, book_id)
    db_delete(delete, member_id, book_id)