With requested as (
    Select 
         'desiredRoom' as desiredRoom,
         'desiredBedType' as desiredBedType,
         'beginDate' as beginDate,
         'endDate' as endDate,
         (adults + kids) as totalGuests
    From dual
),
Occupied as (
    Select Room 
    From lab7_reservations 
    Where not (Checkout <= (select beginDate from requested) or CheckIn >= (select endDate from requested))
)
Select r.RoomCode, r.RoomName, r.Beds, r.bedType, r.maxOcc, r.basePrice, r.decor
From lab7_rooms r, requested
Where ((requested.desiredRoom = 'Any') or (r.RoomCode = requested.desiredRoom))
  and ((requested.desiredBedType = 'Any') or (r.bedType = requested.desiredBedType))
  and r.maxOcc >= (select totalGuests from requested)
  and r.RoomCode not in (select Room from occupied);

With requested as (
    Select 
         'desiredRoom' as desiredRoom,
         'desiredBedType' as desiredBedType,
         'beginDate' as beginDate,
         'endDate' as endDate,
         (adults + kids) as totalGuests
    From dual
),
Occupied as (
    Select Room 
    From lab7_reservations 
    Where not (Checkout <= date_sub((select beginDate from requested), interval 3 day) or CheckIn >= date_add((select endDate from requested), interval 3 day))
)
Select r.RoomCode, r.RoomName, r.Beds, r.bedType, r.maxOcc, r.basePrice, r.decor
From lab7_rooms r, requested
Where r.maxOcc >= (select totalGuests from requested) and r.RoomCode not in (select Room from occupied)
Order by r.basePrice asc
Limit 5;

With new_code as (
    Select ifnull(max(CODE), 0) + 1 as newCode
    From lab7_reservations
)
Insert into lab7_reservations
    (CODE, Room, CheckIn, Checkout, Rate, LastName, FirstName, Adults, Kids)
Select new_code.newCode,
       'chosenRoom',
       'beginDate',
       'endDate',
       r.basePrice,
       'userLastName',
       'userFirstName',
       adults,
       kids
From lab7_rooms r, new_code
Where r.RoomCode = 'chosenRoom';
