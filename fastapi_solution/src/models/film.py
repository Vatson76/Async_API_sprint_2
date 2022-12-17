from typing import Optional

from pydantic import Field

from app.models import BaseMixin
from models.genre import ESFilmGenre
from models.person import ESFilmPerson


class Film(BaseMixin):
    """Filmworks on the homepage and search."""
    uuid: str = Field(..., alias='id')
    title: str
    imdb_rating: float


class FilmDetailed(Film):
    """All information about the filmwork"""
    description: Optional[str]
    genres: Optional[list[ESFilmGenre]]
    actors: Optional[list[ESFilmPerson]]
    writers: Optional[list[ESFilmPerson]]
    directors: Optional[list[ESFilmPerson]]


class ESFilm(BaseMixin):
    """Модель описывающая document в Elasticserch."""
    uuid: str = Field(..., alias='id')
    imdb_rating: Optional[float]
    genres: Optional[list[ESFilmGenre]]
    genre: Optional[list[str]]
    title: str
    description: Optional[str]
    director: Optional[list[str]]
    actors_names: Optional[list[str]]
    writers_names: Optional[list[str]]
    directors: Optional[list[ESFilmPerson]]
    actors: Optional[list[ESFilmPerson]]
    writers: Optional[list[ESFilmPerson]]
