create function tsrange_interception (
    internal_state tsrange, next_data_values tsrange
) returns tsrange as $$
    select internal_state * next_data_values;
$$ language sql;

create aggregate tsrange_interception_agg (tsrange) (
    sfunc = tsrange_interception,
    stype = tsrange,
    initcond = $$[-infinity, infinity]$$
);

CREATE OR REPLACE FUNCTION find_group_intersections(group_name VARCHAR)
RETURNS TABLE (interseption tsrange) AS
$$
BEGIN
    RETURN QUERY
    WITH ranges AS (
        SELECT
            name,
            row_number() OVER (PARTITION BY name ORDER BY telegramid) AS rn,
            unnest(freetime) AS tr
        FROM view_freetime
    ), cr AS (
        SELECT r0.tr AS tr0, r1.tr AS tr1
        FROM ranges r0
        CROSS JOIN ranges r1
        WHERE
            r0.name = group_name
            AND r1.name = group_name
            AND r0.rn < r1.rn
            AND r0.tr && r1.tr
    ), interseptions AS (
        SELECT tr0 * tsrange_interception_agg(tr1) AS interseption
        FROM cr
        GROUP BY tr0
        HAVING count(*) = (SELECT count(distinct telegramid) FROM view_freetime WHERE name = group_name) - 1
    )
    SELECT * FROM interseptions;
END;
$$ LANGUAGE plpgsql;