genres_sql_query = """
    SELECT
        g.id as id,
        g.name as name,
        g.description as description,
        g.modified as modified
    FROM content.genre g
    WHERE g.modified > '{last_modified}'
    ORDER BY g.modified
"""

persons_sql_query = """
    SELECT
        p.id as id,
        p.full_name as name,
        p.modified as modified,
        COALESCE (
           json_agg(
               DISTINCT jsonb_build_object(
                   'id', fw.id,
                   'title', fw.title,
                   'imdb_rating', fw.rating
               )
           )
            FILTER (WHERE fw.id is not null),
           '[]'
       ) as films,
        COALESCE(
            array_agg(DISTINCT pfw.role)
            FILTER (WHERE pfw.id is not null),
            '{{}}'
        ) as roles,
        COALESCE(
            array_agg(DISTINCT fw.id)
            FILTER (WHERE fw.id is not null),
            '{{}}'
        )::text[] as film_ids
    FROM content.person p
    LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
    LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
    WHERE p.modified > '{last_modified}'
    GROUP BY p.id
    ORDER BY p.modified
"""

movies_sql_query = """
    SELECT
        fw.id as id,
        fw.rating as imdb_rating,
        fw.title as title,
        fw.description as description,
        fw.modified as modified,
        COALESCE(
            array_agg(DISTINCT g.name)
            FILTER (WHERE g.id is not null),
            '{{}}'
            ) as genre,
        COALESCE (
           json_agg(
               DISTINCT jsonb_build_object(
                   'id', g.id,
                   'name', g.name
               )
           )
            FILTER (WHERE g.id is not null),
           '[]'
       ) as genres,
        COALESCE(
            array_agg(DISTINCT p.full_name)
            FILTER (WHERE p.id is not null and pfw.role = 'director'),
            '{{}}'
            ) as director,
        COALESCE(
            array_agg(DISTINCT p.full_name)
            FILTER (WHERE p.id is not null and pfw.role = 'actor'),
            '{{}}'
            ) as actors_names,
        COALESCE(
            array_agg(DISTINCT p.full_name)
            FILTER (WHERE p.id is not null and pfw.role = 'writer'),
            '{{}}'
            ) as writers_names,
        COALESCE (
           json_agg(
               DISTINCT jsonb_build_object(
                   'id', p.id,
                   'name', p.full_name
               )
           )
            FILTER (WHERE p.id is not null and pfw.role = 'actor'),
           '[]'
       ) as actors,
        COALESCE (
           json_agg(
               DISTINCT jsonb_build_object(
                   'id', p.id,
                   'name', p.full_name
               )
           )
            FILTER (WHERE p.id is not null and pfw.role = 'writer'),
           '[]'
       ) as writers
    FROM content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
    WHERE fw.modified > '{last_modified}'
    OR p.modified > '{last_modified}'
    OR g.modified > '{last_modified}'
    GROUP BY fw.id
    ORDER BY fw.modified
"""