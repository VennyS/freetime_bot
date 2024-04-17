CREATE VIEW view_member AS 
SELECT user_info.telegramid, user_info.first_name, team.name 
FROM member 
LEFT JOIN team ON team.id = member.teamid
LEFT JOIN user_info ON user_info.id = member.userid;

CREATE VIEW view_freetime AS 
SELECT user_info.telegramid, freetime.freetime, view_member.name
FROM freetime
LEFT JOIN user_info ON user_info.id = freetime.userid
LEFT JOIN view_member ON view_member.telegramid = user_info.telegramid;

CREATE VIEW view_team AS 
SELECT team.name, user_info.first_name, user_info.telegramid, team.hash
FROM team
LEFT JOIN user_info ON user_info.id = team.adminid;