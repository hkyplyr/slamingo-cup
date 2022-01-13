SELECT t.name, SUM(p.points)
FROM players p
JOIN teams t ON t.id = p.team_id
WHERE p.started = 1 AND p.positions LIKE :positions
GROUP BY t.name
ORDER BY t.name;

