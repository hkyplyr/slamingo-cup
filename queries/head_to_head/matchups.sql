SELECT 
    own.manager AS a,
    opp.manager AS b,
    SUM(CASE WHEN own.result = "W" THEN 1 ELSE 0 END) AS a_wins,
    SUM(CASE WHEN own.result = "L" THEN 1 ELSE 0 END) AS b_wins,
    SUM(CASE WHEN own.result = "T" THEN 1 ELSE 0 END) AS ties
FROM weekly_results own
JOIN weekly_results opp ON opp.season = own.season
    AND opp.week = own.week
    AND opp.manager = own.opponent
WHERE own.manager < opp.manager AND own.playoffs = 0
GROUP BY own.manager, opp.manager;