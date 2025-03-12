select ro.RoomName, r.*
    from lab7_reservations r
    join lab7_rooms ro on r.Room = ro.RoomCode
    where FirstName like '%'
        and LastName like '%'
        and Room like '%'
        and CODE like '%'
;

-- or

select ro.RoomName, r.*
    from lab7_reservations r
    join lab7_rooms ro on r.Room = ro.RoomCode
    where FirstName like '%'
        and LastName like '%'
        -- and (CheckIn between %s and %s or Checkout between %s and %s)
        and Room like '%'
        and CODE like '%'
;