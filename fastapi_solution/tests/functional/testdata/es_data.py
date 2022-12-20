import uuid
from datetime import datetime

movies_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': ['Action', 'Sci-Fi'],
        "genres": [
            {"id": str(uuid.uuid4()), "name": 'Action'},
            {"id": str(uuid.uuid4()), "name": 'Sci-Fi'}
        ],
        'title': 'The Star',
        'description': 'New World',
        'director': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        "directors": [
            {'id': '111', 'name': 'Stan'},
        ],
        'actors': [
            {'id': '111', 'name': 'Ann'},
            {'id': '222', 'name': 'Bob'}
        ],
        'writers': [
            {'id': '333', 'name': 'Ben'},
            {'id': '444', 'name': 'Howard'}
        ],
    } for _ in range(20)] + [
    {
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': ['Action', 'Western'],
        "genres": [
            {"id": str(uuid.uuid4()), "name": 'Action'},
            {"id": str(uuid.uuid4()), "name": 'Western'}
        ],
        'title': 'Django',
        'description': 'blackguy',
        'director': ['Me'],
        'actors_names': ['Dan', 'Dick'],
        'writers_names': ['Lesly', 'Olga'],
        "directors": [
            {'id': '111', 'name': 'Me'},
        ],
        'actors': [
            {'id': '111', 'name': 'Dan'},
            {'id': '222', 'name': 'Dick'}
        ],
        'writers': [
            {'id': '333', 'name': 'Lesly'},
            {'id': '444', 'name': 'Olga'}
        ],
    } for _ in range(20)]
