-- Проверка наличия telegramid в user_info
SELECT EXISTS(SELECT telegramid FROM user_info WHERE telegramid = '111111111111');
-- Проверка группы на существование
SELECT EXISTS(SELECT name FROM team WHERE name = 'Челябинск');
-- Вывести список всех групп, в которых состоит пользователь X
SELECT name FROM view_member WHERE telegramid = '222222222222';
-- Вывести все записи с freetime, связанные с пользователем X
SELECT * FROM view_freetime WHERE telegramid = '111111111111';
-- Вывести все записи из freetime, связанные с пользователями группы X
SELECT * FROM view_freetime WHERE name = 'Сатка';
-- Добавлять запись о новом пользователе в user_info
INSERT INTO user_info(telegramid) VALUES
('1'),
('2'),
('3');
-- Добавлять в группу
INSERT INTO team(name) VALUES
('A'),
('B'),
('C');
-- Добавлять запись о свободном времени пользователя в freetime. [YYYY-MM-DD HH:MM:SS, YYYY-MM-DD HH:MM:SS]
INSERT INTO freetime(userid, freetime) VALUES
(1, ARRAY['[2024-03-24 10:00:00, 2024-03-24 12:00:00]'::tsrange,
                      '[2024-03-25 14:00:00, 2024-03-25 16:00:00]'::tsrange]);
					  
					  








