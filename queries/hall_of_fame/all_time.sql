WITH manager_player_points AS (
    SELECT
        p.sleeper_id,
        sp.manager AS manager_name,
        SUM(
            ps.pass_yards * 0.04 +
            ps.pass_touchdowns * 4 +
            ps.pass_interceptions * -1 +
            ps.rush_yards * 0.1 +
            ps.rush_touchdowns * 6 +
            ps.receptions * 0.5 +
            ps.rec_yards * 0.1 +
            ps.rec_touchdowns * 6 +
            ps.fumbles_lost * -2 +
            ps.two_point_conversions * 2
        ) AS manager_fantasy_points
    FROM players p
    JOIN player_stats ps ON ps.sleeper_id = p.sleeper_id
    JOIN selected_positions sp ON sp.season = ps.season
        AND sp.week = ps.week
        AND sp.sleeper_id = ps.sleeper_id
    WHERE (ps.season, ps.week) IN (
        SELECT DISTINCT wr.season, wr.week 
        FROM weekly_results wr
    ) AND p.positions = :position
    GROUP BY p.sleeper_id, sp.manager
    ORDER BY p.sleeper_id, manager_fantasy_points DESC 
),
ordered_managers_string AS (
    SELECT 
        sleeper_id,
        GROUP_CONCAT(DISTINCT manager_name) AS managers_list
    FROM manager_player_points
    WHERE manager_name IS NOT NULL
    GROUP BY sleeper_id
)
SELECT
    player,
    player_id,
    PRINTF('%.2f', total_fantasy_points) AS points,
    PRINTF('%.2f', total_fantasy_points / games_played) AS points_per_game,
    games_played,
    managers
FROM (
    SELECT
        p.sleeper_id AS player_id,
        p.name AS player,
        SUM(
            ps.pass_yards * 0.04 +
            ps.pass_touchdowns * 4 +
            ps.pass_interceptions * -1 +
            ps.rush_yards * 0.1 +
            ps.rush_touchdowns * 6 +
            ps.receptions * 0.5 +
            ps.rec_yards * 0.1 +
            ps.rec_touchdowns * 6 +
            ps.fumbles_lost * -2 +
            ps.two_point_conversions * 2
        ) AS total_fantasy_points,
        COUNT(p.name) AS games_played,
        oms.managers_list AS managers
    FROM players p
    JOIN player_stats ps ON ps.sleeper_id = p.sleeper_id
    LEFT JOIN ordered_managers_string oms ON p.sleeper_id = oms.sleeper_id
    WHERE (ps.season, ps.week) IN (
        SELECT DISTINCT wr.season, wr.week 
        FROM weekly_results wr
    ) AND p.positions = :position
    GROUP BY p.sleeper_id, p.name
)
ORDER BY CAST(points AS REAL) DESC
LIMIT 10;
