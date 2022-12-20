import uuid
from datetime import datetime

movies_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': ['Action', 'Sci-Fi'],
        'title': 'The Star',
        'description': 'New World',
        'director': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': '111', 'name': 'Ann'},
            {'id': '222', 'name': 'Bob'}
        ],
        'writers': [
            {'id': '333', 'name': 'Ben'},
            {'id': '444', 'name': 'Howard'}
        ],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'film_work_type': 'movie'
    } for _ in range(20)] + [
    {
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': ['Action', 'Western'],
        'title': 'Django',
        'description': 'blackguy',
        'director': ['Me'],
        'actors_names': ['Dan', 'Dick'],
        'writers_names': ['Lesly', 'Olga'],
        'actors': [
            {'id': '111', 'name': 'Dan'},
            {'id': '222', 'name': 'Dick'}
        ],
        'writers': [
            {'id': '333', 'name': 'Lesly'},
            {'id': '444', 'name': 'Olga'}
        ],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'film_work_type': 'movie'
    } for _ in range(20)]
