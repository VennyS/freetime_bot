INSERT INTO user_info(telegramid, first_name) VALUES 
(11, 'Андрей'), 
(22, 'Леонтий'),
(33, 'Данил');

INSERT INTO team(name, hash, adminid) VALUES
('Сатка', '1be82cb4898e5894', 1),
('Магнитогорск', '03256626d2ee411c', 2),
('Петровка', 'ae4867e49e961119', 3);

INSERT INTO member(userid, teamid) VALUES
(1, 1),
(2, 2),
(3, 3),
(1, 2),
(1, 3);

INSERT INTO freetime(userid, freetime) VALUES
(1, ARRAY['[2024-03-24 12:00:00, 2024-03-24 16:00:00]'::tsrange,
                      '[2024-03-25 18:00:00, 2024-03-25 22:00:00]'::tsrange]),
(2, ARRAY['[2024-03-24 10:00:00, 2024-03-24 14:00:00]'::tsrange,
                      '[2024-03-25 15:00:00, 2024-03-25 21:00:00]'::tsrange]),
(3, ARRAY['[2024-03-24 8:00:00, 2024-03-24 24:00:00]'::tsrange])
