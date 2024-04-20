-- Создаем правило для представления view_team
CREATE OR REPLACE OR REPLACE RULE insert_view_team_rule AS
    ON INSERT TO view_team
    DO INSTEAD (
        -- Вставляем новую запись в таблицу member
        INSERT INTO team (name, hash, adminid)
        VALUES (
            NEW.name,
            NEW.hash, (SELECT id FROM user_info WHERE telegramid = NEW.telegramid)
        );
    );
    
-- Создаем правило для представления view_member
CREATE OR REPLACE RULE insert_view_member_rule AS
    ON INSERT TO view_member
    DO INSTEAD (
        -- Вставляем новую запись в таблицу member
        INSERT INTO member (userid, teamid)
        VALUES (
            (SELECT id FROM user_info WHERE telegramid = NEW.telegramid),
            (SELECT id FROM team WHERE name = NEW.name)
        );
    );

-- Создаем правило для обновления записей в представлении view_member
CREATE OR REPLACE RULE update_view_member_rule AS
    ON UPDATE TO view_member
    DO INSTEAD (
        -- Обновляем запись в таблице member с использованием новых значений
        UPDATE member
        SET userid = (SELECT id FROM user_info WHERE telegramid = NEW.telegramid),
            teamid = (SELECT id FROM team WHERE name = NEW.name)
        WHERE userid = (SELECT id FROM user_info WHERE telegramid = OLD.telegramid)
          AND teamid = (SELECT id FROM team WHERE name = OLD.name);
    );

-- Создаем правило для удаления записей из представления view_member
CREATE OR REPLACE RULE delete_view_member_rule AS
    ON DELETE TO view_member
    DO INSTEAD (
        -- Удаляем запись из таблицы member
        DELETE FROM member
        WHERE userid = (SELECT id FROM user_info WHERE telegramid = OLD.telegramid)
          AND teamid = (SELECT id FROM team WHERE name = OLD.name);
    );

-- Создаем правило для вставки/обновления записей в представлении view_member
CREATE OR REPLACE RULE insert_view_freetime_rule AS
    ON INSERT TO view_freetime
    DO INSTEAD (
        INSERT INTO freetime (userid, freetime)
        VALUES (
            (SELECT id FROM user_info WHERE telegramid = NEW.telegramid),
            NEW.freetime
        )
        ON CONFLICT (userid) DO UPDATE
        SET freetime = EXCLUDED.freetime;
    );

-- Создаем правило для обновления записей в представлении view_member
CREATE OR REPLACE RULE update_view_freetime_rule AS
    ON UPDATE TO view_freetime
    DO INSTEAD (
        -- Обновляем запись в таблице member с использованием новых значений
        UPDATE freetime
        SET freetime = NEW.freetime
        WHERE userid = (SELECT id FROM user_info WHERE telegramid = OLD.telegramid);
    );

-- Создаем правило для удаления записей из представления view_member
CREATE OR REPLACE RULE delete_view_freetime_rule AS
    ON DELETE TO view_freetime
    DO INSTEAD (
        -- Удаляем запись из таблицы member
        DELETE FROM freetime
        WHERE userid = (SELECT id FROM user_info WHERE telegramid = OLD.telegramid)
    );
