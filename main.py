# we could make every request a function, which will hold default values set to equivalent of "Any"
# Any could be represented as an empty string since it symbolizes no constraints at all; it could also be
# AND TRUE within our WHERE statement.
# use limit 5 for the no matches but show 5
################
# DEPENCENCIES #
################
import os
import time
from time import process_time_ns

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

# function displays information held within cursor after running a query using pandas
def display_panda(cursor):
    result = cursor.fetchall()
    if len(result) > 0:
        columns = [desc[0] for desc in cursor.description] # get col descriptions
        df = pd.DataFrame(result, columns=columns)
        print(df.to_string(index=False) + '\n')
    else:
        print("No data found\n")



def fr1(cursor):
    try:
        cursor.execute(f"with popularity as (with slength as (select * , least(datediff(Checkout,Checkin), datediff(now(), checkin)) StayLength from {reservations} where (datediff(now(), Checkout) < 180) and datediff(now(), CheckIn) > 0) select Room, sum(StayLength) / 180 Popularity from slength group by Room), available as (with rs as (select Room, Checkin,Checkout from {reservations} where datediff(Checkout, now()) > 0), gaps as (select r1.Room, r1.Checkout, r2.CheckIn from rs r1 join rs r2 on r1.Checkout < r2.CheckIn and r1.Room = r2.Room where datediff(r1.CheckIn, r2.Checkout) <> 0) select Room, min(Checkout) nextAvailable  from gaps group by Room), recent as (select completed.Room Room, completed.checkout CheckoutDay, datediff({reservations}.Checkout, {reservations}.CheckIn) LengtOfMostRecentStay from (select Room, max(Checkout) checkout from {reservations} where datediff(now(), Checkout) > 0 group by Room) completed join {reservations} on {reservations}.Room = completed.Room and completed.checkout = {reservations}.Checkout) select available.Room, NextAvailable, Popularity, CheckoutDay MostRecentCheckout, LengtOfMostRecentStay from available join popularity on available.Room = popularity.Room join recent on recent.Room = available.Room;")
    except Exception as e:
        print(f"Error with SQL Query: {e}")

def fr2(cursor):
    try:
        clear_screen()
        print(">>> Make New Reservation <<<\n")
        
        # 1. Collect user input
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        desired_room = input("Room code (or press Enter for 'Any'): ").strip()
        desired_bedtype = input("Bed type (or press Enter for 'Any'): ").strip()
        begin_date = input("Begin date (YYYY-MM-DD): ").strip()
        end_date = input("End date (YYYY-MM-DD): ").strip()
        try:
            adults = int(input("Number of adults: ").strip())
            kids = int(input("Number of kids: ").strip())
        except ValueError:
            print("Invalid number entered for adults or kids. Reservation cancelled.")
            return
        
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
            ),
            Occupied as (
                Select Room 
                From {reservations} 
                Where not (Checkout <= (select beginDate from requested) or CheckIn >= (select endDate from requested))
            )
            Select r.RoomCode, r.RoomName, r.Beds, r.bedType, r.maxOcc, r.basePrice, r.decor
            From {rooms} r, requested
            Where ((requested.desiredRoom = 'Any') or (r.RoomCode = requested.desiredRoom))
            and ((requested.desiredBedType = 'Any') or (r.bedType = requested.desiredBedType))
            and r.maxOcc >= (select totalGuests from requested)
            and r.RoomCode not in (select Room from occupied);
        """
        params_exact = (desired_room, desired_bedtype, begin_date, end_date, total_ppl)
        cursor.execute(exact_sql, params_exact)
        exact_results = cursor.fetchall()
        
        if len(exact_results) > 0:
            results_list = exact_results
            print("Matches found:\n")
        else:
            print("No exact matches found. Showing up to 5 similar suggestions...\n")
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
                ),
                Occupied as (
                    Select Room 
                    From {reservations} 
                    Where not (Checkout <= date_sub((select beginDate from requested), interval 3 day) or CheckIn >= date_add((select endDate from requested), interval 3 day))
                )
                Select r.RoomCode, r.RoomName, r.Beds, r.bedType, r.maxOcc, r.basePrice, r.decor
                From {rooms} r, requested
                Where r.maxOcc >= (select totalGuests from requested) and r.RoomCode not in (select Room from occupied)
                Order by r.basePrice asc
                Limit 5;
            """
            params_similar = (desired_room, desired_bedtype, begin_date, end_date, total_ppl)
            cursor.execute(similar_sql, params_similar)
            similar_results = cursor.fetchall()
            if len(similar_results) == 0:
                print("Cannot make reservation.\n")
                return
            results_list = similar_results
        
        # 4. Display available rooms via pandas so the user can select one
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results_list, columns=columns)
        print(df.to_string(index=True))
        print()
        choice = input("Enter the row number to book (or 'C' to cancel): ").strip()
        if choice.lower() == 'c':
            clear_screen()
            print("Reservation cancelled.\n")
            return
        try:
            choice_idx = int(choice)
            if choice_idx < 0 or choice_idx >= len(results_list):
                print("Invalid row number. Reservation cancelled.")
                return
        except ValueError:
            print("Invalid input. Reservation cancelled.")
            return
        
        chosen_room = results_list[choice_idx]
        # Expecting: (RoomCode, RoomName, Beds, bedType, maxOcc, basePrice, decor)
        room_code = chosen_room[0]
        room_name = chosen_room[1]
        base_rate = float(chosen_room[5])
        
        # 5. Compute the total cost (weekdays at base rate; weekends at 110% of base rate)
        import datetime
        def compute_total_cost(rate, start_str, end_str):
            start = datetime.date.fromisoformat(start_str)
            end = datetime.date.fromisoformat(end_str)
            total = 0.0
            day = start
            while day < end:
                if day.weekday() >= 5:  # Saturday (5) and Sunday (6)
                    total += rate * 1.10
                else:
                    total += rate
                day += datetime.timedelta(days=1)
            return round(total, 2)
        total_cost = compute_total_cost(base_rate, begin_date, end_date)
        
        # 6. Insert the new reservation using a WITH query to generate a new reservation code
        insert_sql = f"""
            With new_code as (
                Select ifnull(max(CODE), 0) + 1 as newCode
                From {reservations}
            )
            Insert into {reservations}
                (CODE, Room, CheckIn, Checkout, Rate, LastName, FirstName, Adults, Kids)
            Select new_code.newCode,
                %s,
                %s,
                %s,
                r.basePrice,
                %s,
                %s,
                %s,
                %s
            From {rooms} r, new_code
            Where r.RoomCode = %s;
        """
        params_insert = (room_code, begin_date, end_date,
                         last_name, first_name, adults, kids,
                         room_code)
        cursor.execute(insert_sql, params_insert)
        
    except Exception as e:
        print(f"Error with SQL Query: {e}")
        return False

    clear_screen()
    print(">>> Reservation Confirmed <<<\n")
    print(f"Name: {first_name} {last_name}")
    print(f"Room: {room_code} - {room_name} (Bed Type: {chosen_room[3]})")
    print(f"Dates: {begin_date} to {end_date}")
    print(f"Adults: {adults}, Kids: {kids}")
    print(f"Total Cost: ${total_cost}\n")
    print("Reservation successfully inserted into the database.\n")


def cancel_h(cursor, code) -> bool:
    try:
        cursor.execute(f"DELETE from {reservations} where code = %s", [code])
        return True
    except Exception as e:
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



def details_h(cursor, args : list) -> bool:
    try:
        dateRange = args[2].split(" ")
        if len(dateRange) == 1:
            param = [args[0], args[1], args[3], args[4]]
            cursor.execute(f"select * from {reservations} r where FirstName like %s and LastName like %s and Room like %s and CODE like %s",
                       param)
            return True
        else:
            param = [args[0], args[1], dateRange[0], dateRange[1], dateRange[0], dateRange[1], args[3], args[4]]
            cursor.execute(f"select * from {reservations} r where FirstName like %s and LastName like %s and (CheckIn between %s and %s or Checkout between %s and %s) and Room like %s and CODE like %s",
                           param)
            return True
    except Exception as e:
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
        cursor.execute(
            f"with Rev as (select Room, Sum(if(checkin < '2025-01-01', greatest(datediff(LEAST(checkout, '2025-02-01'), '2025-01-01'), 0), if(checkout >= '2025-02-01', greatest(DateDiff('2025-02-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) January, Sum(if(checkin < '2025-02-01', greatest(datediff(LEAST(checkout, '2025-03-01'), '2025-02-01'), 0), if(checkout >= '2025-03-01', greatest(DateDiff('2025-03-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) February, Sum(if(checkin < '2025-03-01', greatest(datediff(LEAST(checkout, '2025-04-01'), '2025-03-01'), 0), if(checkout >= '2025-04-01', greatest(DateDiff('2025-04-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) March, Sum(if(checkin < '2025-04-01', greatest(datediff(LEAST(checkout, '2025-05-01'), '2025-04-01'), 0), if(checkout >= '2025-05-01', greatest(DateDiff('2025-05-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) April, Sum(if(checkin < '2025-05-01', greatest(datediff(LEAST(checkout, '2025-06-01'), '2025-05-01'), 0), if(checkout >= '2025-06-01', greatest(DateDiff('2025-06-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) May, Sum(if(checkin < '2025-06-01', greatest(datediff(LEAST(checkout, '2025-07-01'), '2025-06-01'), 0), if(checkout >= '2025-07-01', greatest(DateDiff('2025-07-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) June, Sum(if(checkin < '2025-07-01', greatest(datediff(LEAST(checkout, '2025-08-01'), '2025-07-01'), 0), if(checkout >= '2025-08-01', greatest(DateDiff('2025-08-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) July, Sum(if(checkin < '2025-08-01', greatest(datediff(LEAST(checkout, '2025-09-01'), '2025-08-01'), 0), if(checkout >= '2025-09-01', greatest(DateDiff('2025-09-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) August, Sum(if(checkin < '2025-09-01', greatest(datediff(LEAST(checkout, '2025-10-01'), '2025-09-01'), 0), if(checkout >= '2025-10-01', greatest(DateDiff('2025-10-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) September, Sum(if(checkin < '2025-10-01', greatest(datediff(LEAST(checkout, '2025-11-01'), '2025-10-01'), 0), if(checkout >= '2025-11-01', greatest(DateDiff('2025-11-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) October, Sum(if(checkin < '2025-11-01', greatest(datediff(LEAST(checkout, '2025-12-01'), '2025-11-01'), 0), if(checkout >= '2025-12-01', greatest(DateDiff('2025-12-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) November, Sum(if(checkin < '2025-12-01', greatest(datediff(LEAST(checkout, '2026-01-01'), '2025-12-01'), 0), if(checkout >= '2026-01-01', greatest(DateDiff('2026-01-01', Checkin), 0), datediff(Checkout, Checkin))) * Rate) December from {reservations} group by Room) (select * from Rev order by Room) union select 'Total', Sum(January), Sum(February), Sum(March), Sum(April), SUM(May), SUm(June), Sum(July), Sum(August), Sum(September), SUM(October), Sum(November), SUM(December) from Rev")
    except Exception as e:
        print(f"Error with SQL Query: {e}")



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
            fr1(cursor)
            display_panda(cursor)
        elif choice == "2": # Reservations
            fr2(cursor)
            display_panda(cursor)
            # print("yes")
        elif choice == "3": # Reservation Cancellation
            if fr3(cursor):
                print("Successfully cancelled the reservation.\n")
            else:
                print("Did not cancel any reservations\n")
        elif choice == "4": # Detailed Reservation Information
            if fr4(cursor):
                print("Retrieved the following reservations:\n")
            display_panda(cursor)
        elif choice == "5": # Revenue
            fr5(cursor)
            display_panda(cursor)
        elif choice == "6": # Exit
            replay = False
        else:
            print("Invalid input!\n")
            time.sleep(0.5)

    # TODO: commit changes made during runtime
    exit_seq(conn, cursor)

    return


if __name__ == "__main__":
    main()