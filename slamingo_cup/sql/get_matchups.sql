SELECT
    t1.name,
    wr1.pf,
    t2.name,
    wr2.pf
FROM matchups m
JOIN teams t1 ON t1.id = m.winner_team
JOIN teams t2 ON t2.id = m.loser_team
JOIN weekly_results wr1 ON wr1.week = m.week AND t1.id = wr1.team_id
JOIN weekly_results wr2 ON wr2.week = m.week AND t2.id = wr2.team_id
WHERE m.week = :week
ORDER BY (wr1.pf + wr2.pf) DESC;