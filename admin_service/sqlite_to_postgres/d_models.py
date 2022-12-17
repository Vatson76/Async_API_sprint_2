import uuid
from dataclasses import dataclass, field, InitVar
from datetime import datetime, date


@dataclass
class Filmwork:
    title: str
    creation_date: date
    type: str
    description: str
    file_path: str
    id: uuid.UUID
    rating: float = field(default=0.0)
    certificate: str = None
    created: datetime = None
    modified: datetime = None
    created_at: InitVar[str] = None
    updated_at: InitVar[str] = None

    def __post_init__(self, created_at: str, updated_at: str):
        if created_at is not None:
            self.created = datetime.strptime(
                created_at.replace('+00', ' +0000'), "%Y-%m-%d %H:%M:%S.%f %z"
            )
        if updated_at is not None:
            self.modified = datetime.strptime(
                updated_at.replace('+00', ' +0000'), "%Y-%m-%d %H:%M:%S.%f %z"
            )


@dataclass
class Genre:
    name: str
    description: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: InitVar[str] = None
    updated_at: InitVar[str] = None
    created: datetime = None
    modified: datetime = None

    def __post_init__(self, created_at: str, updated_at: str):
        if created_at is not None:
            self.created = datetime.strptime(
                created_at.replace('+00', ' +0000'), "%Y-%m-%d %H:%M:%S.%f %z"
            )
        if updated_at is not None:
            self.modified = datetime.strptime(
                updated_at.replace('+00', ' +0000'), "%Y-%m-%d %H:%M:%S.%f %z"
            )


@dataclass
class GenreFilmwork:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    genre_id: uuid.UUID = field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: InitVar[str] = None
    updated_at: InitVar[str] = None
    created: datetime = None
    modified: datetime = None

    def __post_init__(self, created_at: str, updated_at: str):
        if created_at is not None:
            self.created = datetime.strptime(
                created_at.replace('+00', ' +0000'), "%Y-%m-%d %H:%M:%S.%f %z"
            )
        if updated_at is not None:
            self.modified = datetime.strptime(
                updated_at.replace('+00', ' +0000'), "%Y-%m-%d %H:%M:%S.%f %z"
            )


@dataclass
class Person:
    full_name: str
    gender: str = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: InitVar[str] = None
    updated_at: InitVar[str] = None
    created: datetime = None
    modified: datetime = None

    def __post_init__(self, created_at: str, updated_at: str):
        if created_at is not None:
            self.created = datetime.strptime(
                created_at.replace('+00', ' +0000'), "%Y-%m-%d %H:%M:%S.%f %z"
            )
        if updated_at is not None:
            self.modified = datetime.strptime(
                updated_at.replace('+00', ' +0000'), "%Y-%m-%d %H:%M:%S.%f %z"
            )


@dataclass
class PersonFilmwork:
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    person_id: uuid.UUID = field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: InitVar[str] = None
    created: datetime = None

    def __post_init__(self, created_at: str):
        if created_at is not None: 
            self.created = datetime.strptime(
                created_at.replace('+00', ' +0000'), "%Y-%m-%d %H:%M:%S.%f %z"
            )
