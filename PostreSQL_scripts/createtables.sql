CREATE TABLE user_info (
	id SERIAL PRIMARY KEY,
	telegramid BIGINT NOT NULL,
	first_name varchar(32) NOT NULL,
	nickname varchar(64) NOT NULL
);

CREATE TABLE team(
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	hash VARCHAR(64) NOT NULL,
	adminid INTEGER REFERENCES user_info(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE member (
	id SERIAL PRIMARY KEY,
	userid INTEGER REFERENCES user_info(id) ON DELETE CASCADE ON UPDATE CASCADE,
	teamid INTEGER REFERENCES team(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE freetime (
	id SERIAL PRIMARY KEY,
	userid INTEGER REFERENCES user_info(id) ON DELETE CASCADE ON UPDATE CASCADE,
	freetime tsrange[]
)
