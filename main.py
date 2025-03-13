# we could make every request a function, which will hold default values set to equivalent of "Any"
# Any could be represented as an empty string since it symbolizes no constraints at all; it could also be
# AND TRUE within our WHERE statement.
# use limit 5 for the no matches but show 5
################
# DEPENCENCIES #
################
import os
import time
import datetime

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

optnsPrompt = str("Command options: \n1. Rooms and Rates\n2. Reservations\n3. Reservation Cancellation\n"
                  + "4. Detailed Reservation Information\n5. Revenue\n6. Exit\nPlease select option (1,2,3,4,5,6): ")


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



# initial pandas setup to display tables
def pandas_setup():
    pd.set_option('display.max_rows', None)             # Display all rows
    pd.set_option('display.max_columns', None)          # Display all columns
    pd.set_option('display.width', None)                # No line wrapping
    pd.options.display.colheader_justify = 'left'       # ensure cols left-align

# function displays information held within cursor after running a query using pandas
def display_panda(cursor):
    result = cursor.fetchall()
    if len(result) > 0:
        columns = [desc[0] for desc in cursor.description] # get col descriptions
        df = pd.DataFrame(result, columns=columns)
        print(df.to_string(index=False) + '\n')
        return df
    else:
        print("No reservations found with the given filters.\n")
        return None



def fr1(cursor):
    try:
        with open("FR1.sql", 'r') as f1:
            cursor.execute(f1.read())
            f1.close()
        return True
    except Exception:
        return False



# helper to fr2
def areDatesValid(begin_date, end_date):
    # Convert strings to datetime objects
    try:
        date1 = datetime.date.fromisoformat(begin_date)
        date2 = datetime.date.fromisoformat(end_date)
        if date1 > date2 or date1 < datetime.date.today(): # end date cannot be before begin date and begin from today
            raise ValueError
    except ValueError:
        return False
    return True


# helper function to fr2.
def compute_total_cost(rate, begin_date, end_date):
    start = datetime.date.fromisoformat(begin_date)
    end = datetime.date.fromisoformat(end_date)
    total = 0.0
    day = start
    while day < end:
        if day.weekday() >= 5:  # weekends
            total += rate * 1.10
        else:
            total += rate
        day += datetime.timedelta(days=1)
    return round(total, 2)


def fr2(cursor) -> bool:
    try:
        clear_screen()
        print(">>> Make New Reservation <<<\n")
        
        # 1. Collect user input
        first_name = input("First name: ")
        last_name = input("Last name: ")
        desired_room = input("Room code (or press Enter for 'Any'): ")
        desired_bedtype = input("Bed type (or press Enter for 'Any'): ")
        begin_date = input("Begin date (YYYY-MM-DD): ")
        end_date = input("End date (YYYY-MM-DD): ")
        if not areDatesValid(begin_date, end_date):
            clear_screen()
            print("Invalid dates!\n")
            time.sleep(1)
            clear_screen()
            return False
        try:
            adults = int(input("Number of adults: "))
            kids = int(input("Number of kids: "))
            clear_screen()
            # cannot have a reservation with 0 people
            if adults + kids == 0:
                raise ValueError
        except ValueError:
            clear_screen()
            print("Invalid number entered for adults or kids. Reservation cancelled.")
            time.sleep(1.2)
            clear_screen()
            return False
        
        if desired_room == "":
            desired_room = "Any"
        if desired_bedtype == "":
            desired_bedtype = "Any"
        total_ppl = adults + kids

        # 2. Execute the Exact Match Query using a WITH clause
        # (Using parameterized values instead of literal placeholders.)
        exact_sql = f"""
            With requested as (
                Select 
                    %s as desiredRoom,
                    %s as desiredBedType,
                    %s as beginDate,
                    %s as endDate,
                    %s as totalGuests
                From dual
            )
            Select r.RoomCode, r.RoomName, r.Beds, r.bedType, r.maxOcc, r.basePrice, r.decor
            From {rooms} r
            Join requested
            Where (requested.desiredRoom = 'Any' or r.RoomCode = requested.desiredRoom)
              and (requested.desiredBedType = 'Any' or r.bedType = requested.desiredBedType)
              and r.maxOcc >= requested.totalGuests
              and r.RoomCode not in (
                  Select Room from {reservations}
                  Join requested
                  Where not (Checkout <= requested.beginDate or CheckIn >= requested.endDate)
              );
        """
        params_exact = (desired_room, desired_bedtype, begin_date, end_date, total_ppl)
        cursor.execute(exact_sql, params_exact)
        exact_results = cursor.fetchall()
        
        if len(exact_results) > 0:
            results_list = exact_results
            print("Matches found:\n")
        else:
            # 3. Execute the Similar Suggestions Query (with relaxed date window by 3 days)
            similar_sql = f"""
                With requested as (
                    Select 
                        %s as desiredRoom,
                        %s as desiredBedType,
                        %s as beginDate,
                        %s as endDate,
                        %s as totalGuests
                    From dual
                )
                Select r.RoomCode, r.RoomName, r.Beds, r.bedType, r.maxOcc, r.basePrice, r.decor
                From {rooms} r
                Join requested
                Where (requested.desiredRoom = 'Any' or r.RoomCode = requested.desiredRoom)
                and (requested.desiredBedType = 'Any' or r.bedType = requested.desiredBedType)
                and r.maxOcc >= requested.totalGuests
                and r.RoomCode not in (
                    Select Room
                    From {reservations}
                    Join requested
                    Where not (Checkout <= DATE_SUB(requested.beginDate, INTERVAL 3 DAY) or CheckIn >= DATE_ADD(requested.endDate, INTERVAL 3 DAY))
                )
                Order by r.basePrice asc
                Limit 5;
            """
            params_similar = (desired_room, desired_bedtype, begin_date, end_date, total_ppl)
            cursor.execute(similar_sql, params_similar)
            similar_results = cursor.fetchall()

            if len(similar_results) == 0:
                clear_screen()
                print("Cannot make the reservation.\n")
                clear_screen()
                time.sleep(1)
                return False
            results_list = similar_results
            print("No exact matches found. Showing up to 5 similar suggestions:\n\n")

        # set up DataFrame for next prints
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results_list, columns=columns)
        # 4. Display available rooms via pandas so the user can select one
        while True:
            print(df.to_string(index=True) + "\n")
            choice = input("Enter the row number to book (or 'C' to cancel): ")
            if choice.lower() == 'c':
                clear_screen()
                print("Reservation cancelled.\n")
                time.sleep(1)
                clear_screen()
                return False
            try:
                choice_idx = int(choice)
                if choice_idx < 0 or choice_idx >= len(results_list):
                    raise ValueError
                break   # valid input
            except ValueError:
                clear_screen()
                print("Invalid input!")
                time.sleep(0.7)
                clear_screen()
        # end of while

        
        chosen_room = results_list[choice_idx]
        # Expecting: (RoomCode, RoomName, Beds, bedType, maxOcc, basePrice, decor)
        room_code = chosen_room[0]
        room_name = chosen_room[1]
        base_rate = float(chosen_room[5])
        
        # 5. Compute the total cost (weekdays at base rate; weekends at 110% of base rate)
        total_cost = compute_total_cost(base_rate, begin_date, end_date)
        
        # 6. Insert the new reservation using a WITH query to generate a new reservation code
        insert_sql = f"""
           Insert into lab7_reservations
            (CODE, Room, CheckIn, Checkout, Rate, LastName, FirstName, Adults, Kids)
            Select (Select ifnull(max(CODE), 0) + 1 as newCode
            From lab7_reservations),
            %s,
            %s,
            %s,
            r.basePrice,
            %s,
            %s,
            %s,
            %s
            From lab7_rooms r
            Where r.RoomCode = %s;
        """
        params_insert = (room_code, begin_date, end_date,
                         last_name, first_name, adults, kids,
                         room_code)
        cursor.execute(insert_sql, params_insert)
    except Exception:
        clear_screen()
        return False

    clear_screen()
    print(">>> Reservation Confirmed <<<\n")
    print(f"Name: {first_name} {last_name}")
    print(f"Room: {room_code} - {room_name} (Bed Type: {chosen_room[3]})")
    print(f"Dates: {begin_date} to {end_date}")
    print(f"Adults: {adults}, Kids: {kids}")
    print(f"Total Cost: ${total_cost}\n")
    return True

def cancel_h(cursor, code) -> bool:
    try:
        cursor.execute(f"DELETE from {reservations} where code = %s", [code])
        return True
    except Exception:
        return False

# function returns true if query was executed successfully, False otherwise.
def fr3(cursor) -> bool:
    try:
        clear_screen()
        print(">>> User Cancel Reservations <<<")
        resCode = input("Enter reservation code: ")

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
            df = display_panda(cursor)

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
                    clear_screen()
                    print("Invalid input")
                    time.sleep(0.5)
                    clear_screen()
                    print("Attempting to cancel reservation:\n\n" + df.to_string(index=False) + "\n")


    except Exception:
        return False



def details_h(cursor, args : list) -> bool:
    try:
        dateRange = args[2].split(" ")
        if len(dateRange) == 1:
            param = [args[0], args[1], args[3], args[4]]
            cursor.execute(f"""
                    select ro.RoomName, r.* 
                    from {reservations} r 
                    join {rooms} ro on r.Room = ro.RoomCode 
                    where FirstName like %s and LastName like %s and Room like %s and CODE like %s;""",
                    param)
            return True
        else:
            param = [args[0], args[1], dateRange[0], dateRange[1], dateRange[0], dateRange[1], args[3], args[4]]
            cursor.execute(f"""
                select ro.RoomName, r.* 
                from {reservations} r 
                join {rooms} ro on r.Room = ro.RoomCode 
                where FirstName like %s 
                    and LastName like %s 
                    and (CheckIn between %s and %s or Checkout between %s and %s) 
                    and Room like %s and CODE like %s;""",
                    param)
            return True
    except Exception:
        return False



def fr4(cursor) -> bool:
    args = []
    for i in range(5):
        args.append("")
    print(">>> Detailed Reservation Information <<<")
    print("Please enter the following details:\n")
    args[0] = input("First Name: ")
    args[1] = input("Last Name: ")
    args[2] = input("Range of Dates (separated by space): ")
    args[3] = input("Room code: ")
    args[4] = input("Reservation code: ")

    # cannot have %
    if '%' in args[2] or '%' in args[3]:
        clear_screen()
        print("Invalid input. Both date ranges and the room code have to be complete")
        time.sleep(1.5)
        clear_screen()
        return False

    dateRange = args[2].split(" ")
    if len(dateRange) != 2 and len(args[2]) != 0:
        clear_screen()
        print("Invalid input. You need to either provide no date or a range")
        time.sleep(1.5)
        clear_screen()
        return False

    # convert empty filters into wildcards
    for i in range(len(args)):
        if args[i] == '':
            args[i] = '%'

    isSuccessful = details_h(cursor, args)
    clear_screen()
    return isSuccessful



def fr5(cursor):
    try:
        with open("FR5.sql", 'r') as f5:
            cursor.execute(f5.read())
            f5.close()
        return True
    except Exception:
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
        if choice == "1": # Rooms and Rates
            if fr1(cursor):
                display_panda(cursor)
            else:
                print("Error fetching rooms and rates.\n")
        elif choice == "2": # Reservations
            if not fr2(cursor):
                print("Did not finalize the reservation.\n")
        elif choice == "3": # Reservation Cancellation
            if fr3(cursor):
                print("Successfully cancelled the reservation.\n")
            else:
                print("Did not cancel any reservations.\n")
        elif choice == "4": # Detailed Reservation Information
            if fr4(cursor):
                print("Retrieved the following reservations:\n")
            display_panda(cursor)
        elif choice == "5": # Revenue
            if fr5(cursor):
                display_panda(cursor)
            else:
                print("Error fetching revenue.\n")
        elif choice == "6": # Exit
            replay = False
        else:
            clear_screen()
            print("Invalid input!\n")
            time.sleep(0.7)
            clear_screen()
            print(f"Welcome {conn.user}!\n")

    # TODO: commit changes made during runtime
    exit_seq(conn, cursor)

    return


if __name__ == "__main__":
    main()