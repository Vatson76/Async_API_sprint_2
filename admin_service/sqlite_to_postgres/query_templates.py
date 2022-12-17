filmwork_insert_query = """
INSERT INTO content.film_work (
    id, title, description, creation_date, rating, 
    type, created, modified, certificate, file_path
)
VALUES (
    %(id)s, %(title)s, %(description)s, %(creation_date)s, %(rating)s, 
    %(type)s, %(created)s, %(modified)s, %(certificate)s, %(file_path)s
)
ON CONFLICT (id) DO NOTHING; 
"""

genre_insert_query = """
INSERT INTO content.genre (id, name, created, modified, description)
VALUES (%(id)s, %(name)s, %(created)s, %(modified)s, %(description)s)
ON CONFLICT (id) DO NOTHING; 
"""


genre_filmwork_insert_query = """
INSERT INTO content.genre_film_work (id, genre_id, film_work_id, created, modified)
VALUES (%(id)s, %(genre_id)s, %(film_work_id)s, %(created)s, %(modified)s)
ON CONFLICT (id) DO NOTHING; 
"""


person_insert_query = """
INSERT INTO content.person (id, full_name, created, modified, gender)
VALUES (%(id)s, %(full_name)s, %(created)s, %(modified)s, %(gender)s)
ON CONFLICT (id) DO NOTHING; 
"""


person_filmwork_insert_query = """
INSERT INTO content.person_film_work (id, person_id, film_work_id, role, created)
VALUES (%(id)s, %(person_id)s, %(film_work_id)s, %(role)s, %(created)s)
ON CONFLICT (id) DO NOTHING; 
"""
