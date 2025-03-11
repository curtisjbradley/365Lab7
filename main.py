# we could make every request a function, which will hold default values set to equivalent of "Any"
# Any could be represented as an empty string since it symbolizes no constraints at all; it could also be
# AND TRUE within our WHERE statement.
# use limit 5 for the no matches but show 5
################
# DEPENCENCIES #
################
import os
import time
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

optnsPrompt = str("Command options: \n1. Print all reservations\n2. Print all rooms\n3. Cancel reservation\n"
                  + "4. FR1\n5. FR5\n6. Exit\nPlease select option (1,2,3,4,5,6): ")


#########################
# FUNCTION DECLARATIONS #
#########################
# this function clears the console for visual graphics
def clear_screen():
    os.system('cls' if os.name == 'nt'
              else 'clear')



# This function prompts the user for credentials to log into the working database.
# User must have been previously granted access by owner of the working database.
def create_connection():
    clear_screen()
    print(">>> User Login <<<")
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

def fr1(cursor):
    try:
        cursor.execute(f"with popularity as (with slength as (select * , least(datediff(Checkout,Checkin), datediff(now(), checkin)) StayLength from {reservations} where (datediff(now(), Checkout) < 180) and datediff(now(), CheckIn) > 0) select Room, sum(StayLength) / 180 Popularity from slength group by Room), available as (with rs as (select Room, Checkin,Checkout from {reservations} where datediff(Checkout, now()) > 0), gaps as (select r1.Room, r1.Checkout, r2.CheckIn from rs r1 join rs r2 on r1.Checkout < r2.CheckIn and r1.Room = r2.Room where datediff(r1.CheckIn, r2.Checkout) <> 0) select Room, min(Checkout) nextAvailable  from gaps group by Room), recent as (select completed.Room Room, completed.checkout CheckoutDay, datediff({reservations}.Checkout, {reservations}.CheckIn) LengtOfMostRecentStay from (select Room, max(Checkout) checkout from {reservations} where datediff(now(), Checkout) > 0 group by Room) completed join {reservations} on {reservations}.Room = completed.Room and completed.checkout = {reservations}.Checkout) select available.Room, NextAvailable, Popularity, CheckoutDay MostRecentCheckout, LengtOfMostRecentStay from available join popularity on available.Room = popularity.Room join recent on recent.Room = available.Room;")
    except Exception as e:
        print(f"Error with SQL Query: {e}")

def fr5(cursor):
        try:
            cursor.execute(f"with Rev as (select Room, Sum(if(checkin < '2025-01-01', greatest(datediff(LEAST(checkout, '2025-02-01'), '2025-01-01'), 0), if(checkout >= '2025-02-01', greatest(DateDiff('2025-02-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) January, Sum(if(checkin < '2025-02-01', greatest(datediff(LEAST(checkout, '2025-03-01'), '2025-02-01'), 0), if(checkout >= '2025-03-01', greatest(DateDiff('2025-03-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) February, Sum(if(checkin < '2025-03-01', greatest(datediff(LEAST(checkout, '2025-04-01'), '2025-03-01'), 0), if(checkout >= '2025-04-01', greatest(DateDiff('2025-04-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) March, Sum(if(checkin < '2025-04-01', greatest(datediff(LEAST(checkout, '2025-05-01'), '2025-04-01'), 0), if(checkout >= '2025-05-01', greatest(DateDiff('2025-05-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) April, Sum(if(checkin < '2025-05-01', greatest(datediff(LEAST(checkout, '2025-06-01'), '2025-05-01'), 0), if(checkout >= '2025-06-01', greatest(DateDiff('2025-06-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) May, Sum(if(checkin < '2025-06-01', greatest(datediff(LEAST(checkout, '2025-07-01'), '2025-06-01'), 0), if(checkout >= '2025-07-01', greatest(DateDiff('2025-07-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) June, Sum(if(checkin < '2025-07-01', greatest(datediff(LEAST(checkout, '2025-08-01'), '2025-07-01'), 0), if(checkout >= '2025-08-01', greatest(DateDiff('2025-08-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) July, Sum(if(checkin < '2025-08-01', greatest(datediff(LEAST(checkout, '2025-09-01'), '2025-08-01'), 0), if(checkout >= '2025-09-01', greatest(DateDiff('2025-09-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) August, Sum(if(checkin < '2025-09-01', greatest(datediff(LEAST(checkout, '2025-10-01'), '2025-09-01'), 0), if(checkout >= '2025-10-01', greatest(DateDiff('2025-10-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) September, Sum(if(checkin < '2025-10-01', greatest(datediff(LEAST(checkout, '2025-11-01'), '2025-10-01'), 0), if(checkout >= '2025-11-01', greatest(DateDiff('2025-11-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) October, Sum(if(checkin < '2025-11-01', greatest(datediff(LEAST(checkout, '2025-12-01'), '2025-11-01'), 0), if(checkout >= '2025-12-01', greatest(DateDiff('2025-12-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) November, Sum(if(checkin < '2025-12-01', greatest(datediff(LEAST(checkout, '2026-01-01'), '2025-12-01'), 0), if(checkout >= '2026-01-01', greatest(DateDiff('2026-01-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) December from {reservations} group by Room) (select * from Rev order by Room) union select 'Total', Sum(January), Sum(February), Sum(March), Sum(April), SUM(May), SUm(June), Sum(July), Sum(August), Sum(September), SUM(October), Sum(November), SUM(December) from Rev")
        except Exception as e:
            print(f"Error with SQL Query: {e}")

# initial pandas setup to display tables
def pandas_setup():
    pd.set_option('display.max_rows', None)             # Display all rows
    pd.set_option('display.max_columns', None)          # Display all columns
    pd.set_option('display.width', None)                # No line wrapping

# function displays information held within cursor after running a query using pandas
def display_panda(cursor):
    result = cursor.fetchall()
    if len(result) > 0:
        columns = [desc[0] for desc in cursor.description] # get col descriptions
        df = pd.DataFrame(result, columns=columns)
        print(df.to_string(index=False) + '\n')
    else:
        print("No data found\n")

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


def cancel_h(cursor, code) -> bool:
    try:
        cursor.execute(f"DELETE from {reservations} where code = %s", [code])
        return True
    except Exception as e:
        return False


# function returns true if query was executed successfully, False otherwise.
def cancelres_query(cursor) -> bool:
    try:
        clear_screen()
        print(">>> User Cancel Reservations <<<")
        resCode = input("Enter reservation code: ")

        # TODO: index reservations
        cursor.execute(f"SELECT * from {reservations} as r where r.CODE = %s", [resCode]) # indexed op
        result = cursor.fetchall()
        if len(result) ==  0:
            clear_screen()
            print(f"No reservations found under reservation code {resCode}")
            time.sleep(1.2)
            clear_screen()
            return False
        else:
            cursor.execute(f"SELECT * from {reservations} as r where r.CODE = %s", [resCode])
            clear_screen()
            print("Attempting to cancel reservation:\n")
            # print entry to be deleted
            display_panda(cursor)

            # confirm with user to cancel
            while True:
                answer = input("Press 1 to delete reservation or 2 to cancel the process: ")
                if answer == "1":
                    isSuccessful = cancel_h(cursor, resCode)
                    clear_screen()
                    return isSuccessful
                if answer == "2":
                    time.sleep(0.3)
                    clear_screen()
                    return False
                else:
                    print("Invalid input")
                    time.sleep(0.5)

    except Exception as e:
        print(f"Error with SQL Query: {e}")
        return False


# prints the exit animation and closes both the connection and the cursor
def exit_seq(conn, cursor):
    print("Closing session...")
    cursor.close()
    conn.close()

    time.sleep(0.5)
    print("Exiting...")
    time.sleep(0.5)
    clear_screen()



#################
# MAIN FUNCTION #
#################
def main():
    # initial set up
    conn = create_connection()  # log in
    if conn is None or not conn.is_connected():    # failed to connect
        exit(1)

    try:
        cursor = conn.cursor()
    except Exception as err:
        print(f"Error: {err}")
        conn.close()
        exit(1)
    pandas_setup()
    clear_screen()


    print(f"Welcome {conn.user}!\n")
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
        elif choice == "3": # cancel reservation
            if cancelres_query(cursor):
                print("Successfully cancelled the reservation.\n")
            else:
                print("Did not cancel any reservations\n")
        elif choice == "4":
                    fr1(cursor)
                    display_panda(cursor)
        elif choice == "5":
                            fr5(cursor)
                            display_panda(cursor)
        elif choice == "6": # exit
            replay = False
        else:
            print("Invalid input!\n")
            time.sleep(0.5)

    exit_seq(conn, cursor)

    return


if __name__ == "__main__":
    main()