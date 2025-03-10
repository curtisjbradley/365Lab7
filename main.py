# we could make every request a function, which will hold default values set to equivalent of "Any"
# Any could be represented as an empty string since it symbolizes no constraints at all; it could also be
# AND TRUE within our WHERE statement.
################
# DEPENCENCIES #
################
import os
import mysql.connector
import getpass
from mysql.connector import Error as connError
import pandas as pd

####################
# GLOBAL VARIABLES #
####################
dataBase = "jmalpart"   # working database
# tables in fully-qualified form
reservations = f"{dataBase}.lab7_reservations"
rooms = f"{dataBase}.lab7_rooms"

optnsPrompt = "Command options: \n1. Print all reservations\n2. Print all rooms\n3. Exit\nPlease select option (1,2,3): "

#########################
# FUNCTION DECLARATIONS #
#########################
# This function prompts the user for credentials to log into the working database.
# User must have been previously granted access by owner of the working database.
def create_connection():
    db_user = input("Enter database username: ")
    db_password = getpass.getpass("Enter database password: ")

    try:
        conn = mysql.connector.connect(user=db_user, password=db_password,
                                   host='mysql.labthreesixfive.com',
                                   database=dataBase)
    except connError as e:
        print(f"Error: {e}")
        return None

    return conn



# this function clears the console for visual graphics
def clear_screen():
    os.system('cls' if os.name == 'nt'
              else 'clear')



def selre_query(cursor):
    try:
        cursor.execute(f"SELECT * from {reservations} as r")
        #cursor.execute("SELECT * from {reservations} as r") # this leads to an exception
    except Exception as e:
        print(f"Error with SQL Query: {e}")



def selro_query(cursor):
    try:
        cursor.execute(f"SELECT * from {rooms} as r")
    except Exception as e:
        print(f"Error with SQL Query: {e}")



# initial pandas setup to display tables
def pandas_setup():
    pd.set_option('display.max_rows', None)     # Display all rows
    pd.set_option('display.max_columns', None)  # Display all columns
    pd.set_option('display.width', None)        # No line wrapping

# function displays information held within cursor after running a query using pandas
def display_panda(cursor):
    result = cursor.fetchall()
    if len(result) > 0:
        columns = [desc[0] for desc in cursor.description] # get col descriptions
        df = pd.DataFrame(result, columns=columns)
        print(df)
    else:
        print("No data found")

#################
# MAIN FUNCTION #
#################
def main():
    # initial set up
    conn = create_connection()
    # failed to connect
    if conn is None:
        exit(1)
    # make cursor
    try:
        cursor = conn.cursor()
    except Exception as err:
        print(f"Error: {err}")
        conn.close()
        exit(1)
    pandas_setup()
    clear_screen()

    replay = True
    while replay:
        choice = input(optnsPrompt)

        clear_screen()
        if choice == "1": # select * from reservations
            selre_query(cursor)
            display_panda(cursor)
        elif choice == "2": # select * from rooms
            selro_query(cursor)
            display_panda(cursor)
        elif choice == "3": # exit
            replay = False
        else:
            print("Invalid input!\n")

    print("Closing session...")
    cursor.close()
    conn.close()

    print("Exiting...")
    return


if __name__ == "__main__":
    main()