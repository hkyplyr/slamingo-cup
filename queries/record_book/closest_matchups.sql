-- name: Closest Matchups
-- ordinal: 4

SELECT
    ROW_NUMBER() OVER (
        ORDER BY
            difference ASC
    ) AS rank,
    manager,
    'Week ' || week || ', ' || season || ' (vs. ' || opponent || ')' AS footer,
    PRINTF ('%.2f', difference) AS value
FROM
    (
        SELECT
            own.manager,
            own.week,
            own.season,
            opp.manager AS opponent,
            own.points_for - opp.points_for AS difference
        FROM
            weekly_results AS own
            JOIN weekly_results AS opp ON opp.season = own.season
            AND opp.week = own.week
            AND opp.manager = own.opponent
        WHERE
            own.playoffs = 0
    ) AS results
WHERE
    difference > 0
ORDER BY
    difference ASC
LIMIT
    10;