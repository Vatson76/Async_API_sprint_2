from sqlite_to_postgres.d_models import (
    Filmwork, PersonFilmwork, Person,
    Genre, GenreFilmwork
)
from sqlite_to_postgres.query_templates import (
    genre_insert_query, person_insert_query, filmwork_insert_query,
    genre_filmwork_insert_query, person_filmwork_insert_query
)


table_to_dataclass = {
    'film_work': Filmwork,
    'genre': Genre,
    'genre_film_work': GenreFilmwork,
    'person': Person,
    'person_film_work': PersonFilmwork
}

table_to_insert_query = {
    'film_work': filmwork_insert_query,
    'genre': genre_insert_query,
    'genre_film_work': genre_filmwork_insert_query,
    'person': person_insert_query,
    'person_film_work': person_filmwork_insert_query
}
