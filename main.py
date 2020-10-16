import sqlite3
import os.path

# Setup functions
def set_up_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS accounts
    (first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    subscription_price REAL NOT NULL,
    email TEXT NOT NULL,
    phone_number INT NOT NULL,
    website TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL)""")

    conn.commit()

    cursor.close()

def store_master_password():
    master_password = ""
    while True:
        master_password = input("Please choose your new master password: ")
        print("Your new master password is: ", master_password)
        confirmation = input("Is that alright with you? Type 'y' to confirm: ")
        if confirmation[0].lower() == 'y':
            print("Satisfaction confirmed! Setting new master password...")
            break
        else:
            print("Satisfaction not confirmed. Choosing a new password...")

    master_password_file = open("master_password_file.txt", "w")
    master_password_file.write(master_password)
    master_password_file.close()

def get_master_password():
    master_password_file = open("master_password_file.txt", "r")
    master_password = master_password_file.readline()
    master_password_file.close()
    return master_password

def view_options(conn):
    while True:
        print("Enter the conditions under which to search the database.")
        print("Enter 'a' to view all the accounts, enter 'n' to search by a full name,"
              , " enter 'p' to search by subscribed price, or enter 'w' to search by website.")
        choice = input("Please enter your choice: ")
        if choice[0].lower() == 'a':
            try:
                cursor = conn.cursor()
                view_command = "SELECT * FROM accounts"
                cursor.execute(view_command)
                return cursor
            except sqlite3.Error as error:
                print("Failed to view account(s) in table", error)
        elif choice[0].lower() == 'n':
            first_name = input("Please enter the exact first name: ")
            last_name = input("Please enter the exact last name: ")
            try:
                cursor = conn.cursor()
                view_command = "SELECT * FROM accounts WHERE first_name = ? AND last_name = ?"
                cursor.execute(view_command, (first_name, last_name))
                return cursor
            except sqlite3.Error as error:
                print("Failed to view account(s) in table", error)
        elif choice[0].lower() == 'p':
            while True:
                try:
                    price = float(input("Please enter the exact price of the plan of which you wish to view all those who subscribed: "))
                    break
                except ValueError:
                    print("Please enter an actual decimal number!")
            try:
                cursor = conn.cursor()
                view_command = "SELECT * FROM accounts WHERE subscription_price = ?"
                cursor.execute(view_command, (price,))
                return cursor
            except sqlite3.Error as error:
                print("Failed to view account(s) in table", error)
        elif choice[0].lower() == 'w':
            website_name = input("Please enter the exact name of the website: ")
            try:
                cursor = conn.cursor()
                view_command = "SELECT * FROM accounts WHERE website = ?"
                cursor.execute(view_command, (website_name,))
                return cursor
            except sqlite3.Error as error:
                print("Failed to view account(s) in table", error)
        else:
            print("Sorry, no valid input was entered.\n")

def view(conn, use_direct_query=False, direct_query="", direct_query_first_name="", direct_query_last_name=""):
    try:
        if use_direct_query:
            cursor = conn.cursor()
            cursor.execute(direct_query, (direct_query_first_name, direct_query_last_name))
        else:
            cursor = view_options(conn)
        number_of_accounts = 0
        while True:
            account = cursor.fetchone()
            if account == None:
                break

            print("First name: ", account[0])
            print("Last name: ", account[1])
            print("Subscription price: ", account[2])
            print("Email: ", account[3])
            print("Phone number: ", account[4])
            print("Website: ", account[5])
            print("Username: ", account[6])
            print("Password: ", account[7])
            print("\n")
            number_of_accounts += 1
        print("{0} accounts were found.".format(number_of_accounts))
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read data from table", error)

# Insert function
def insert(conn, file_input=False, file_input_account=""):
    new_account_list = []
    if not file_input:
        while True:
            print("Enter the details of the new account in this format:")
            print("First name|Last name|Subscription price|Email|Phone number|Website|Username|Password")
            new_account_list = input("Enter it here: ").split("|")
            if (len(new_account_list) != 8):
                print("You need to have typed in eight items, each separated by a vertical pipe!")
                continue
            try:
                new_account_list[2] = float(new_account_list[2])
                new_account_list[4] = int(new_account_list[4])
            except ValueError:
                print("The subscription price needs to be an actual decimal number, and",
                      " the phone number needs to be written as an integer with no spaces or dashes!")
                continue
            break
    else:
        new_account_list = file_input_account.split("|")
        if (len(new_account_list) != 8):
            print("The file string needs to have eight items, each separated by a vertical pipe!")
            return
        try:
            new_account_list[2] = float(new_account_list[2])
            new_account_list[4] = int(new_account_list[4])
        except ValueError:
            print("The subscription price needs to be an actual decimal number, and",
                  " the phone number needs to be written as an integer with no spaces or dashes!")
            return

    # Check to see if the account already exists.
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts")
        while True:
            account = cursor.fetchone()
            if account == None:
                break
            if new_account_list[0] == account[0] and new_account_list[1] == account[1] and new_account_list[5] == account[5]:
                print("An account with first name '{0}', last name '{1}', and website '{2}' already exists!".format(new_account_list[0], new_account_list[1], new_account_list[5]))
                cursor.close()
                return
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to read data from table", error)

    try:
        cursor = conn.cursor()
        insert_command = "INSERT INTO accounts VALUES(?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(insert_command, (new_account_list[0], new_account_list[1], new_account_list[2], new_account_list[3], new_account_list[4], new_account_list[5], new_account_list[6], new_account_list[7]))
        conn.commit()
        cursor.close()
        print("Account successfully added to database!")
    except sqlite3.Error as error:
        print("Failed to add account to table", error)

# Update functions

def update_account_personal(conn, column, new_info, first_name, last_name):
    # Update the person's personal details all across the table.
    try:
        cursor = conn.cursor()
        update_command = "UPDATE accounts SET {0} = ? WHERE first_name = ? AND last_name = ?"
        update_command_with_column = update_command.format(column)
        cursor.execute(update_command_with_column, (new_info, first_name, last_name))
        conn.commit()
        cursor.close()
        print("Successfully updated account(s)!")
    except sqlite3.Error as error:
        print("Failed to update account(s) in table", error)

def update_account_website(conn, column, new_info, first_name, last_name, website):
    # Update one account (of a specific website) of the given person.
    try:
        cursor = conn.cursor()
        update_command = "UPDATE accounts SET {0} = ? WHERE first_name = ? AND last_name = ? AND website = ?"
        update_command_with_column = update_command.format(column)
        cursor.execute(update_command_with_column, (new_info, first_name, last_name, website))
        conn.commit()
        cursor.close()
        print("Successfully updated account(s)!")
    except sqlite3.Error as error:
        print("Failed to update account(s) in table", error)

def get_full_name(conn):
    # Get the person's full name and check to see if any accounts with that name exist.

    print("Which account(s) do you wish to choose?")
    first_name = input("Enter the first name: ")
    last_name = input("Enter the last name: ")
    try:
        cursor = conn.cursor()
        select_command = "SELECT * FROM accounts WHERE first_name = ? AND last_name = ?"
        cursor.execute(select_command, (first_name, last_name))
    except sqlite3.Error as error:
        print("Failed to read data from table", error)
        return None, None

    if not len(cursor.fetchall()) == 0:
        cursor.close()
        return first_name, last_name
    else:
        print("\nNo accounts were found with that name!\n")
        cursor.close()
        return None, None

def get_website(conn, first_name, last_name):
    # Get the specific website with the details that the person wants to modify
    # Make an existence check as well

    website_choice = input("Please choose a website from the person's list: ")
    try:
        cursor = conn.cursor()
        select_command = "SELECT * FROM accounts WHERE first_name = ? AND last_name = ? AND website = ?"
        cursor.execute(select_command, (first_name, last_name, website_choice))
    except sqlite3.Error as error:
        print("Failed to read data from table", error)
        return None

    if not len(cursor.fetchall()) == 0:
        cursor.close()
        return website_choice
    else:
        print("\nNo account was found with that website!\n")
        cursor.close()
        return None


def update(conn):

    first_name, last_name = get_full_name(conn)

    if (first_name == None or last_name == None):
        return

    # Print out the accounts of this person as a reminder.
    print("Here are all the accounts of this person:")
    select_command = "SELECT * FROM accounts WHERE first_name = ? AND last_name = ?"
    view(conn, True, select_command, first_name, last_name)

    # Does the user want to update the person's own details, or do they want to change a specific website account?
    while True:
        print("Do you wish to update this person's personal details, or do you wish to update a website account of theirs?")
        update_choice = input("Press 'p' to choose personal details, or 'w' to choose a website: ")
        if update_choice[0].lower() == 'p':
            while True:
                print("What do you wish to update?")
                print("""Enter 0 to update a first name, enter 1 to update a last name, 
                enter 2 to update a subscription price, enter 3 to update an email, 
                or enter 4 to update a phone number.""")

                choice = input("Enter it here: ")

                if choice == "0":
                    new_first_name = input("Please enter the new first name: ")
                    update_account_personal(conn, "first_name", new_first_name, first_name, last_name)
                    break
                elif choice == "1":
                    new_last_name = input("Please enter the new last name: ")
                    update_account_personal(conn, "last_name", new_last_name, first_name, last_name)
                    break
                elif choice == "2":
                    # Check for float
                    while True:
                        new_sub_price = input("Please enter the new subscription price: ")
                        try:
                            new_sub_price = float(new_sub_price)
                        except ValueError:
                            print("The subscription price needs to be an actual decimal number.")
                            continue
                        break
                    update_account_personal(conn, "subscription_price", new_sub_price, first_name, last_name)
                    break
                elif choice == "3":
                    new_email = input("Please enter the new email: ")
                    update_account_personal(conn, "email", new_email, first_name, last_name)
                    break
                elif choice == "4":
                    # Check for int
                    while True:
                        new_phone_number = input("Please enter the new phone number (as an integer with no spaces or dashes): ")
                        try:
                            new_phone_number = int(new_phone_number)
                        except ValueError:
                            print("The new phone number needs to be an integer with no spaces or dashes!")
                            continue
                        break
                    update_account_personal(conn, "phone_number", new_phone_number, first_name, last_name)
                    break
                else:
                    print("\nNo proper choice was specified! Please try again.\n")
            break
        elif update_choice[0].lower() == 'w':

            # Get the specific website with the details that the person wants to modify
            # Make an existence check as well
            website_choice = get_website(conn, first_name, last_name)
            if website_choice == None:
                return

            while True:
                print("What do you wish to update?")
                print("Enter 5 to update a website name, enter 6 to update a username, or enter 7 to update a password.")

                choice = input("Enter it here: ")

                if choice == "5":
                    new_website = input("Please enter the new website name: ")
                    update_account_website(conn, "website", new_website, first_name, last_name, website_choice)
                    break
                elif choice == "6":
                    new_username = input("Please enter the new username: ")
                    update_account_website(conn, "username", new_username, first_name, last_name, website_choice)
                    break
                elif choice == "7":
                    new_password = input("Please enter the new password: ")
                    update_account_website(conn, "password", new_password, first_name, last_name, website_choice)
                    break
                else:
                    print("\nNo proper choice was specified! Please try again.\n")
            break
        else:
            print("Please choose either 'p' or 'w'!")

def delete(conn, prepare_for_file_overwrite=False):

    # Check to see if the user wants to delete all the accounts in the table
    all_choice = ""
    if not prepare_for_file_overwrite:
        print("Do you wish to delete all the accounts in the database, or do you wish to choose one person?")
        all_choice = input("Press 'a' to delete all of the accounts, or any other key to choose a person: ")
    if all_choice == 'a' or prepare_for_file_overwrite:
        try:
            cursor = conn.cursor()
            delete_command = "DELETE FROM accounts"
            cursor.execute(delete_command)
            conn.commit()
            cursor.close()
            print("Successfully deleted all accounts!")
        except sqlite3.Error as error:
            print("Failed to delete all accounts from table", error)
        finally:
            return

    # Get the full name of the person you want to perform deleting actions on
    first_name, last_name = get_full_name(conn)
    if (first_name == None or last_name == None):
        return

    # Print out the accounts of this person as a reminder.
    print("Here are all the accounts of this person:")
    select_command = "SELECT * FROM accounts WHERE first_name = ? AND last_name = ?"
    view(conn, True, select_command, first_name, last_name)

    while True:
        print("Do you wish to delete this person from the database, or do you wish to simply delete one of their website accounts?")
        delete_choice = input("Press 'p' to choose person, or 'w' to choose a website: ")
        if delete_choice[0].lower() == 'p':
            try:
                cursor = conn.cursor()
                delete_command = "DELETE FROM accounts WHERE first_name = ? AND last_name = ?"
                cursor.execute(delete_command, (first_name, last_name))
                conn.commit()
                cursor.close()
                print("Successfully deleted person!")
            except sqlite3.Error as error:
                print("Failed to delete person from table", error)
            finally:
                break
        elif delete_choice[0].lower() == 'w':
            website_choice = get_website(conn, first_name, last_name)
            if website_choice == None:
                return
            try:
                cursor = conn.cursor()
                delete_command = "DELETE FROM accounts WHERE first_name = ? AND last_name = ? AND website = ?"
                cursor.execute(delete_command, (first_name, last_name, website_choice))
                conn.commit()
                cursor.close()
                print("Successfully deleted website account!")
            except sqlite3.Error as error:
                print("Failed to delete account from table", error)
            finally:
                break
        else:
            print("Please choose either 'p' or 'w'!")
# Import functions
def import_from_file(conn):
    file_name = input("Please enter the name of the text file containing the account strings: ")
    if os.path.isfile(file_name):
        while True:
            print("Do you wish to append to the table or do you wish to overwrite the table?")
            import_choice = input("Press 'a' for append or 'o' for overwrite: ")
            if import_choice == 'a':
                import_file = open(file_name, "r")
                for account_string in import_file:
                    account_string_without_newline = account_string.strip("\n")
                    insert(conn, True, account_string_without_newline)
                import_file.close()
                break
            elif import_choice == 'o':
                delete(conn, True)
                import_file = open(file_name, "r")
                for account_string in import_file:
                    account_string_without_newline = account_string.strip("\n")
                    insert(conn, True, account_string_without_newline)
                import_file.close()
                break
            else:
                print("No valid input was passed in!")
    else:
        print("Not a valid file name!")

# Export functions
def export_to_file(conn):
    file_name = input("Please enter the name of the text file to contain the account strings: ")
    while True:
        print("Do you wish to append to the file or do you wish to overwrite the contents in the file?")
        export_choice = input("Press 'a' for append or 'o' for overwrite: ")
        if export_choice == 'a':
            export_file = open(file_name, "a+")
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM accounts")
                while True:
                    account = cursor.fetchone()
                    if account == None:
                        break
                    raw_account_string = "{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}"
                    account_string = raw_account_string.format(account[0], account[1],
                                                               account[2], account[3],
                                                               account[4], account[5],
                                                               account[6], account[7])
                    export_file.write(account_string + "\n")
            except sqlite3.Error as error:
                print("Failed to write accounts from table to file", error)
            export_file.close()
            break
        elif export_choice == 'o':
            export_file = open(file_name, "w+")
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM accounts")
                while True:
                    account = cursor.fetchone()
                    if account == None:
                        break
                    raw_account_string = "{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}"
                    account_string = raw_account_string.format(account[0], account[1],
                                                               account[2], account[3],
                                                               account[4], account[5],
                                                               account[6], account[7])
                    export_file.write(account_string + "\n")
            except sqlite3.Error as error:
                print("Failed to write accounts from table to file", error)
            export_file.close()
            break
        else:
            print("No valid input was passed in!")

# Main loop
print("Welcome to the Password Manager!")
conn = sqlite3.connect("passwordmanager.db")

if not os.path.isfile("master_password_file.txt"):
    master_password_file = open("master_password_file.txt", "w+")

master_password = get_master_password()
if master_password == "":
    print("First-time user detected! Preparing setup protocols...")
    set_up_tables(conn)
    store_master_password()
else:
    while True:
        password_guess = input("Please enter the master password: ")
        if password_guess == master_password:
            print("Password accepted!")
            break
        else:
            print("Password denied...")

while True:
    print("""Press 0 to view the database, press 1 to insert a new account, press 2 to update the database,
    press 3 to delete something from the database, press 4 to import accounts from a file,
    press 5 to export accounts to a file, press 6 to change the master password, and press 7 to exit.""")
    choice = input("Please enter your choice here: ")
    if choice == "0":
        view(conn)
    elif choice == "1":
        insert(conn)
    elif choice == "2":
        update(conn)
    elif choice == "3":
        delete(conn)
    elif choice == "4":
        import_from_file(conn)
    elif choice == "5":
        export_to_file(conn)
    elif choice == "6":
        store_master_password()
    elif choice == "7":
        print("Thank you for visiting the Password Manager!")
        conn.close()
        break
    else:
        print("No valid input was entered!")