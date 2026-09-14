SELECT
    name AS player,
    sleeper_id AS player_id,
    season,
    PRINTF('%.2f', fantasy_points) AS points,
    PRINTF('%.2f', fantasy_points / games_played) AS points_per_game,
    managers
FROM (
    SELECT
        p.sleeper_id,
        p.positions,
        ps.season,
        p.name,
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
        ) AS fantasy_points,
        COUNT(*) AS games_played,
        GROUP_CONCAT(DISTINCT sp.manager) AS managers
    FROM players p
    JOIN player_stats ps on ps.sleeper_id = p.sleeper_id
    JOIN selected_positions sp ON sp.season = ps.season
      AND sp.week = ps.week
      AND sp.sleeper_id = ps.sleeper_id
    WHERE (ps.season, ps.week) IN (
        SELECT DISTINCT wr.season, wr.week
        FROM weekly_results wr
    ) AND p.positions = :position
    GROUP BY
    p.sleeper_id,
    p.name,
    ps.season
)
ORDER BY fantasy_points DESC
LIMIT 10;