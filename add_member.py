"""
Add a member with info details, such as name, email and phone number

"""

import datetime
import re
from database import db_insert


def get_member_name(name_type) -> str:    
    while True:
        name = input(f"Enter your {name_type}: ").strip().capitalize()
        if not name:
            print("Error: Field cannot be empty. Please try again.")
            continue
        if not name.isalpha():
            print(f"Error: {name_type} must contain letters only (no numbers or spaces). Please try again.")
            continue
        return name

def get_member_email() -> str:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    while True:
        email = input("Enter your email address: ").strip().lower()
        if not email:
            print("Error: Field cannot be empty. Please try again.")
            continue
        if not re.match(pattern, email):
            print("Error: Invalid email format. Please make sure it contains '@' and a valid domain.")
            continue
        return email

def get_member_phone() -> str:
    pattern = r'^(\+46|0)[0-9\s-]{7,12}$'
    while True:
        phone = input("Enter your phone number: ").strip()
        if not phone:
            print("Error: Field cannot be empty. Please try again.")
            continue
        if not re.match(pattern, phone):
            print("Error: Invalid phone number format. Use numbers, spaces, or hyphens only.")
            continue
        return phone


def collect_member_info()-> tuple:
    print("--- Please enter your details ---")
    
    first_name = get_member_name("First name")
    last_name = get_member_name("Last name")
    email = get_member_email()
    phone = get_member_phone()
    joined = datetime.date.today().strftime("%Y-%m-%d")

    full_name = " ".join([first_name, last_name])

    # Returning data as a list
    return (full_name, email, phone, joined)



def add_member() -> None:
    member_info = collect_member_info()

    for detail in member_info:
        if detail is None:
            break
        # else:
        #     collect_member_info
            

    db_insert("?", member_info)



add_member()


# collect_member_info()

    
# member_data = collect_member_info()
# print("\n--- Saved Information ---")
# for detail in member_data:
#     print(detail)
