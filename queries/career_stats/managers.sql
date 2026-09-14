WITH season_weeks AS (
    -- Dynamically identify Semifinal and Final weeks per season
    SELECT 
        season,
        MAX(week) - 1 AS semi_playoff_week,
        MAX(week) AS final_playoff_week
    FROM weekly_results
    WHERE playoffs = 1
    GROUP BY season
),
team_season_summary AS (
    -- Aggregate per-manager, per-season metrics needed to determine end-of-year rank
    SELECT 
        wr.season,
        wr.manager,
        MAX(wr.playoffs) AS playoffs,
        MAX(CASE WHEN wr.playoffs = 1 AND wr.consolation = 0 THEN 1 ELSE 0 END) AS in_championship_bracket,

        -- Semifinal & Final activity flags
        MAX(CASE WHEN wr.playoffs = 1 AND wr.consolation = 0 AND wr.week = sw.semi_playoff_week THEN 1 ELSE 0 END) AS played_semifinal,
        MAX(CASE WHEN wr.playoffs = 1 AND wr.consolation = 0 AND wr.week = sw.semi_playoff_week AND wr.result = 'W' THEN 1 ELSE 0 END) AS won_semifinal,
        MAX(CASE WHEN wr.playoffs = 1 AND wr.consolation = 0 AND wr.week = sw.final_playoff_week AND wr.result = 'W' THEN 1 ELSE 0 END) AS won_final_week,

        -- Regular season tiebreakers
        SUM(CASE WHEN wr.playoffs = 0 AND wr.result = 'W' THEN 1 ELSE 0 END) AS reg_wins,
        SUM(CASE WHEN wr.playoffs = 0 AND wr.result = 'T' THEN 0.5 ELSE 0 END) AS reg_ties,
        SUM(CASE WHEN wr.playoffs = 0 THEN wr.points_for ELSE 0 END) AS reg_points
    FROM weekly_results wr
    JOIN season_weeks sw ON wr.season = sw.season
    GROUP BY wr.season, wr.manager
),
season_standings AS (
    -- Assign exact season final rank (1 through N) for every team each year
    SELECT 
        season,
        manager,
        ROW_NUMBER() OVER (
            PARTITION BY season
            ORDER BY 
                -- TIER 1: Main Bracket vs Consolation Pool
                CASE WHEN playoffs = 1 AND in_championship_bracket = 1 THEN 1 ELSE 2 END ASC,

                -- TIER 2: Top 4 placements via Semis & Finals
                CASE 
                    WHEN playoffs = 1 AND in_championship_bracket = 1 AND won_semifinal = 1 AND won_final_week = 1 THEN 1
                    WHEN playoffs = 1 AND in_championship_bracket = 1 AND won_semifinal = 1 AND won_final_week = 0 THEN 2
                    WHEN playoffs = 1 AND in_championship_bracket = 1 AND played_semifinal = 1 AND won_semifinal = 0 AND won_final_week = 1 THEN 3
                    WHEN playoffs = 1 AND in_championship_bracket = 1 AND played_semifinal = 1 AND won_semifinal = 0 AND won_final_week = 0 THEN 4
                    ELSE 5
                END ASC,

                -- TIER 3: Remaining main bracket teams (5th, 6th, 7th...) by reg season
                CASE WHEN playoffs = 1 AND in_championship_bracket = 1 THEN reg_wins END DESC,
                CASE WHEN playoffs = 1 AND in_championship_bracket = 1 THEN reg_ties END DESC,
                CASE WHEN playoffs = 1 AND in_championship_bracket = 1 THEN reg_points END DESC,

                -- TIER 4: Consolation Pool by reg season
                reg_wins DESC,
                reg_ties DESC,
                reg_points DESC
        ) AS final_rank
    FROM team_season_summary
),
career_playoffs AS (
    -- Career rollup for championships, last place finishes, and avg finish
    SELECT 
        st.manager,
        SUM(CASE WHEN st.final_rank = 1 THEN 1 ELSE 0 END) AS championships,
        SUM(CASE WHEN st.final_rank = sb.last_place_rank THEN 1 ELSE 0 END) AS last_place_finishes,
        ROUND(AVG(CAST(st.final_rank AS REAL)), 1) AS avg_finish
    FROM season_standings st
    JOIN (
        SELECT season, MAX(final_rank) AS last_place_rank 
        FROM season_standings 
        GROUP BY season
    ) sb ON sb.season = st.season
    GROUP BY st.manager
),
all_play AS (
    SELECT
        a.manager,
        SUM(CASE WHEN a.points_for > b.points_for THEN 1 ELSE 0 END) AS all_play_wins,
        SUM(CASE WHEN a.points_for < b.points_for THEN 1 ELSE 0 END) AS all_play_losses,
        SUM(CASE WHEN a.points_for = b.points_for THEN 1 ELSE 0 END) AS all_play_ties
    FROM weekly_results a
    JOIN weekly_results b ON a.season = b.season
        AND a.week = b.week
        AND a.manager != b.manager
    WHERE a.playoffs = 0
    GROUP BY a.manager
),
playoff_appearances AS (
    SELECT 
        manager, 
        COUNT(DISTINCT season) AS playoff_appearances
    FROM weekly_results
    WHERE playoffs = 1 AND consolation = 0
    GROUP BY manager
),
seasons AS (
    SELECT
        manager,
        COUNT(DISTINCT season) AS seasons
    FROM weekly_results
    GROUP BY manager
)
SELECT
    own.manager AS name,
    m.active,
    COALESCE(cp.championships, 0) AS titles,
    COALESCE(cp.last_place_finishes, 0) AS last_place_finishes,
    SUM(CASE WHEN own.result = 'W' THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN own.result = 'L' THEN 1 ELSE 0 END) AS losses,
    SUM(CASE WHEN own.result = 'T' THEN 1 ELSE 0 END) AS ties,
    ap.all_play_wins,
    ap.all_play_losses,
    ap.all_play_ties,
    ROUND(SUM(own.points_for), 2) AS points_for,
    ROUND(SUM(opp.points_for), 2) AS points_against,
    COALESCE(pa.playoff_appearances, 0) AS playoff_appearances,
    COALESCE(cp.avg_finish, 'N/A') AS avg_finish,
    s.seasons
FROM weekly_results own
JOIN weekly_results opp ON opp.season = own.season
    AND opp.week = own.week
    AND opp.manager = own.opponent
LEFT JOIN all_play ap ON ap.manager = own.manager
LEFT JOIN playoff_appearances pa ON pa.manager = own.manager
LEFT JOIN seasons s ON s.manager = own.manager
LEFT JOIN career_playoffs cp ON cp.manager = own.manager
LEFT JOIN managers m ON m.name = own.manager
WHERE own.playoffs = 0
GROUP BY own.manager
ORDER BY wins DESC, avg_finish ASC;