with Rev as (select Room,
                    Sum(if(checkin < '2025-01-01', greatest(datediff(LEAST(checkout, '2025-02-01'), '2025-01-01'), 0),
                           if(checkout >= '2025-02-01', greatest(DateDiff('2025-02-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) January,
                    Sum(if(checkin < '2025-02-01', greatest(datediff(LEAST(checkout, '2025-03-01'), '2025-02-01'), 0),
                           if(checkout >= '2025-03-01', greatest(DateDiff('2025-03-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) February,
                    Sum(if(checkin < '2025-03-01', greatest(datediff(LEAST(checkout, '2025-04-01'), '2025-03-01'), 0),
                           if(checkout >= '2025-04-01', greatest(DateDiff('2025-04-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) March,
                    Sum(if(checkin < '2025-04-01', greatest(datediff(LEAST(checkout, '2025-05-01'), '2025-04-01'), 0),
                           if(checkout >= '2025-05-01', greatest(DateDiff('2025-05-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) April,
                    Sum(if(checkin < '2025-05-01', greatest(datediff(LEAST(checkout, '2025-06-01'), '2025-05-01'), 0),
                           if(checkout >= '2025-06-01', greatest(DateDiff('2025-06-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) May,
                    Sum(if(checkin < '2025-06-01', greatest(datediff(LEAST(checkout, '2025-07-01'), '2025-06-01'), 0),
                           if(checkout >= '2025-07-01', greatest(DateDiff('2025-07-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) June,
                    Sum(if(checkin < '2025-07-01', greatest(datediff(LEAST(checkout, '2025-08-01'), '2025-07-01'), 0),
                           if(checkout >= '2025-08-01', greatest(DateDiff('2025-08-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) July,
                    Sum(if(checkin < '2025-08-01', greatest(datediff(LEAST(checkout, '2025-09-01'), '2025-08-01'), 0),
                           if(checkout >= '2025-09-01', greatest(DateDiff('2025-09-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) August,
                    Sum(if(checkin < '2025-09-01', greatest(datediff(LEAST(checkout, '2025-10-01'), '2025-09-01'), 0),
                           if(checkout >= '2025-10-01', greatest(DateDiff('2025-10-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) September,
                    Sum(if(checkin < '2025-10-01', greatest(datediff(LEAST(checkout, '2025-11-01'), '2025-10-01'), 0),
                           if(checkout >= '2025-11-01', greatest(DateDiff('2025-11-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) October,
                    Sum(if(checkin < '2025-11-01', greatest(datediff(LEAST(checkout, '2025-12-01'), '2025-11-01'), 0),
                           if(checkout >= '2025-12-01', greatest(DateDiff('2025-12-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) November,
                    Sum(if(checkin < '2025-12-01', greatest(datediff(LEAST(checkout, '2026-01-01'), '2025-12-01'), 0),
                           if(checkout >= '2026-01-01', greatest(DateDiff('2026-01-01', Checkin), 0),
                              datediff(Checkout, Checkin))) *
                        Rate) December
             from lab7_reservations
             group by Room)
    (select *
     from Rev
     order by Room)
union
select 'Total',
       Sum(January),
       Sum(February),
       Sum(March),
       Sum(April),
       SUM(May),
       SUm(June),
       Sum(July),
       Sum(August),
       Sum(September),
       SUM(October),
       Sum(November),
       SUM(December)
from Rev

