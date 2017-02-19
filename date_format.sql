2015-03-20 04:05:00

2015-03-25 05:30:00


2015-05-20 17:22:00


SELECT MINUTE(tick_date) AS mn, high, low, close
FROM `tick_minute` 
WHERE `tick_date` BETWEEN '2017-01-20 08:38:00' - INTERVAL 1 MINUTE AND '2017-01-20 08:38:00' + INTERVAL 61 MINUTE

++++++++++++++++++++++++

SELECT DATE_FORMAT(tick_date,'%H:%i') as tm, high, low, close
FROM `tick_minute` 
WHERE `tick_date` BETWEEN '2016-12-20 10:01:00' - INTERVAL 1 MINUTE AND '2016-12-20 10:01:00' + INTERVAL 70 MINUTE
order by tm

119.47 high 119.52 low 119.44

++++++++++++++++++++++++

set @dt='2015-05-20 09:34:00';

SELECT DATE_FORMAT(tick_date,'%H:%i') as tm, high, low, close
FROM `tick_minute` 
WHERE `tick_date` BETWEEN @dt - INTERVAL 10 MINUTE AND @dt + INTERVAL 50 MINUTE
order by tm;


40% posive, 
60% negative

profit: ~-20% negative
