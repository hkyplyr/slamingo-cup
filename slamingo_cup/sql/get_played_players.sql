SELECT * FROM (
    SELECT 
        name,
        "QB",
        sum(points) as pf,
        count(*) as starts,
        sum(points) / count(*) as avg
    FROM players
    WHERE started = 1 AND team_id = :team_id AND positions LIKE '%QB%'
    GROUP BY name
    ORDER BY sum(points) DESC
) UNION ALL 
SELECT * FROM (
    SELECT 
        name,
        "RB",
        sum(points) as pf,
        count(*) as starts,
        sum(points) / count(*) as avg
    FROM players
    WHERE started = 1 AND team_id = :team_id AND positions LIKE '%RB%'
    GROUP BY name
    ORDER BY sum(points) DESC
) UNION ALL 
SELECT * FROM (
    SELECT 
        name,
        "WR",
        sum(points) as pf,
        count(*) as starts,
        sum(points) / count(*) as avg
    FROM players
    WHERE started = 1 AND team_id = :team_id AND positions LIKE '%WR%'
    GROUP BY name
    ORDER BY sum(points) DESC
) UNION ALL 
SELECT * FROM (
    SELECT 
        name,
        "TE",
        sum(points) as pf,
        count(*) as starts,
        sum(points) / count(*) as avg
    FROM players
    WHERE started = 1 AND team_id = :team_id AND positions LIKE '%TE%'
    GROUP BY name
    ORDER BY sum(points) DESC
) UNION ALL 
SELECT * FROM (
    SELECT 
        name,
        "K",
        sum(points) as pf,
        count(*) as starts,
        sum(points) / count(*) as avg
    FROM players
    WHERE started = 1 AND team_id = :team_id AND positions LIKE '%K%'
    GROUP BY name
    ORDER BY sum(points) DESC
) UNION ALL 
SELECT * FROM (
    SELECT 
        name,
        "DEF",
        sum(points) as pf,
        count(*) as starts,
        sum(points) / count(*) as avg
    FROM players
    WHERE started = 1 AND team_id = :team_id AND positions LIKE '%DEF%'
    GROUP BY name
    ORDER BY sum(points) DESC
);
