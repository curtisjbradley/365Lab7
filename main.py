# we could make every request a function, which will hold default values set to equivalent of "Any"
# Any could be represented as an empty string since it symbolizes no constraints at all; it could also be
# AND TRUE within our WHERE statement.

import mysql.connector
import getpass
from mysql.connector import Error as connError
import pandas as pd

dataBase = "jmalpart"                           # working database
reservations = f"{dataBase}.lab7_reservations"
rooms = f"{dataBase}.lab7_rooms"


# This function prompts the user for credentials to log into the working database.
# User must have been previously granted access by owner of the working database.
def create_connection():
    db_user = input("Enter database username: ")
    db_password = getpass.getpass("Enter database password: ")

    try:
        conn = mysql.connector.connect(user=db_user, password=db_password,
                                   host='mysql.labthreesixfive.com',
                                   database=dataBase)
        if conn.is_connected():
            print(f"________________________\nConnected to {dataBase}.\n\n") # TODO: Remove
    except connError as e:
        print(f"Error: {e}")
        return None

    return conn

def sample_query(cursor):
    try:
        cursor.execute(f"SELECT * from {reservations} as r")
        #cursor.execute("SELECT * from {reservations} as r") # this leads to an exception
    except Exception as e:
        print(f"Error with SQL Query: {e}")

def pandas_setup():
    pd.set_option('display.max_rows', None)     # Display all rows
    pd.set_option('display.max_columns', None)  # Display all columns
    pd.set_option('display.width', None)        # No line wrapping

def display_panda(cursor):
    result = cursor.fetchall()
    if len(result) > 0:
        columns = [desc[0] for desc in cursor.description] # get col descriptions
        df = pd.DataFrame(result, columns=columns)
        print(df)
    else:
        print("No data found")

def main():
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

    # attempt to run query
    sample_query(cursor)
    display_panda(cursor)

    cursor.close()
    conn.close()

    return


if __name__ == "__main__":
    main()