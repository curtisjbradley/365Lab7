# we could make every request a function, which will hold default values set to equivalent of "Any"
# Any could be represented as an empty string since it symbolizes no constraints at all; it could also be
# AND TRUE within our WHERE statement.
import mysql.connector
import getpass
from mysql.connector import Error as connError

# working database
dataBase = "jmalpart"
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
            print(f"Connected to {dataBase}.")
    except connError as e:
        print(f"Error: {e}")
        return None

    return conn

def sample_query(cursor):
    #cursor.execute("SELECT * from {reservations} as r") # this leads to an exception
    cursor.execute(f"SELECT * from {reservations} as r")



def main():
    conn = create_connection()

    # failed to connect
    if conn is None:
        exit(1)

    try:
        # make cursor
        cursor = conn.cursor()

        sample_query(cursor)
        result = cursor.fetchall()
        print(result)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

    return


if __name__ == "__main__":
    main()