CREATE VIEW view_member AS 
SELECT user_info.telegramid, team.name
FROM member 
LEFT JOIN team ON team.id = member.teamid
LEFT JOIN user_info ON user_info.id = member.userid;

CREATE VIEW view_freetime AS 
SELECT user_info.telegramid, freetime.freetime, view_member.name
FROM freetime
LEFT JOIN user_info ON user_info.id = freetime.userid
LEFT JOIN view_member ON view_member.telegramid = user_info.telegramid
-- ARRAY['[2024-03-24 10:00:00, 2024-03-24 12:00:00]'::tsrange,
--                       '[2024-03-25 14:00:00, 2024-03-25 16:00:00]'::tsrange]





