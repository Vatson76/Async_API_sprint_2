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
} for _ in range(20)] + [{
    'id': str(uuid.uuid4()),
    'imdb_rating': 5.5,
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

persons_data = [{
    'id': str(uuid.uuid4()),
    'name': 'Dan',
    'film_ids': [str(uuid.uuid4())],
    'films': [
        {'id': 'asdasdasdascxz', 'title': 'Django', 'imdb_rating': 5.5}
    ],
    'roles': ['actor']
} for _ in range(20)] + [{
    'id': str(uuid.uuid4()),
    'name': 'Ann',
    'film_ids': [str(uuid.uuid4())],
    'films': [
        {'id': 'asdasdasdasdasdsfrewfvcxv', 'title': 'The Star', 'imdb_rating': 8.5}
    ],
    'roles': ['actor']
} for _ in range(20)]

genres_data = [{
    'id': str(uuid.uuid4()),
    'name': 'Action',
    'description': 'Action movies'
} for _ in range(20)] + [{
    'id': str(uuid.uuid4()),
    'name': 'Thriller',
    'description': 'Scary movies'
} for _ in range(20)]

persons_movies = {
        'id': '724c72b9-dcfd-435f-8547-bac44d55b7d2',
        'title': 'Django',
        'imdb_rating': 5.5,
        'genre': ['Comedy'],
        "genres": [
            {"id": str(uuid.uuid4()), "name": 'Comedy'}
        ],
        'description': 'Happy New Year comedy',
        'director': ['Stan'],
        'actors_names': ['Annie', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        "directors": [
            {'id': '111', 'name': 'Stan'}
        ], 'actors': [
            {'id': "56789", 'name': 'Annie'},
            {'id': '222', 'name': 'Bob'}
        ],
        'writers': [
            {'id': '12dc90d2-3806-42ae-8bd7-44029b4c092d', 'name': 'Dan Brown'},
            {'id': '444', 'name': 'Howard'}
        ],
    }
person = {
    'id': '12dc90d2-3806-42ae-8bd7-44029b4c092d',
    'name': 'Dan Brown',
    'film_ids': ['724c72b9-dcfd-435f-8547-bac44d55b7d2'],
    'films': [
        {
            'id': '724c72b9-dcfd-435f-8547-bac44d55b7d2',
            'title': 'Django',
            'imdb_rating': 5.5
        }
    ],
    'roles': ['actor']
}
