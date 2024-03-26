-- Создаем правило для представления view_member
CREATE RULE insert_view_member_rule AS
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
CREATE RULE update_view_member_rule AS
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
CREATE RULE delete_view_member_rule AS
    ON DELETE TO view_member
    DO INSTEAD (
        -- Удаляем запись из таблицы member
        DELETE FROM member
        WHERE userid = (SELECT id FROM user_info WHERE telegramid = OLD.telegramid)
          AND teamid = (SELECT id FROM team WHERE name = OLD.name);
    );

