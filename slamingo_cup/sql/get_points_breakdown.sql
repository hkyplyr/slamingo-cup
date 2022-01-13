SELECT
    t.name,
    (SELECT SUM(points) FROM players p
    WHERE p.started = 1 AND p.positions LIKE '%QB%' AND p.team_id = :team_id
    ) as qb_points,
    (SELECT SUM(points) FROM players p
    WHERE p.started = 1 AND p.positions LIKE '%RB%' AND p.team_id = :team_id
    ) as rb_points,
    (SELECT SUM(points) FROM players p
    WHERE p.started = 1 AND p.positions LIKE '%WR%' AND p.team_id = :team_id
    ) as wr_points,
    (SELECT SUM(points) FROM players p
    WHERE p.started = 1 AND p.positions LIKE '%TE%' AND p.team_id = :team_id
    ) as te_points,
    (SELECT SUM(points) FROM players p
    WHERE p.started = 1 AND p.positions LIKE '%K%' AND p.team_id = :team_id
    ) as k_points,
    (SELECT SUM(points) FROM players p
    WHERE p.started = 1 AND p.positions LIKE '%DEF%' AND p.team_id = :team_id
    ) as def_points,
    SUM(p.points) as total_points
FROM players p
JOIN teams t ON t.id = p.team_id
WHERE p.team_id = :team_id AND p.started = 1
GROUP BY t.name;
