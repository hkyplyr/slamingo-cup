-- name: Highest Scores
-- ordinal: 1

SELECT
    ROW_NUMBER() OVER (
        ORDER BY
            points_for DESC
    ) AS rank,
    manager,
    'Week ' || week || ', ' || season || ' (vs. ' || opponent || ')' AS footer,
    PRINTF ('%.2f', points_for) AS value
FROM
    (
        SELECT
            own.manager,
            own.week,
            own.season,
            opp.manager AS opponent,
            own.points_for
        FROM
            weekly_results AS own
            JOIN weekly_results AS opp ON opp.season = own.season
            AND opp.week = own.week
            AND opp.manager = own.opponent
        WHERE
            own.playoffs = 0
    ) AS results
WHERE
    points_for > 0
ORDER BY
    points_for DESC
LIMIT
    10;