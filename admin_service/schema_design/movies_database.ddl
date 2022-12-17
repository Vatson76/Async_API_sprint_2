CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid,
    film_work_id uuid,
    created timestamp with time zone,
    modified timestamp with time zone,
    FOREIGN KEY (genre_id) references content.genre (id) ON DELETE CASCADE,
    FOREIGN KEY (film_work_id) references content.film_work (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    person_id uuid,
    film_work_id uuid,
    role TEXT NOT NULL,
    created timestamp with time zone,
    FOREIGN KEY (person_id) references content.person (id) ON DELETE CASCADE,
    FOREIGN KEY (film_work_id) references content.film_work (id) ON DELETE CASCADE
);


CREATE INDEX film_work_creation_date_idx ON content.film_work(creation_date);
CREATE INDEX ON content.film_work (creation_date, rating);

CREATE UNIQUE INDEX film_work_person_idx ON content.person_film_work (film_work_id, person_id);
CREATE UNIQUE INDEX film_work_genre_idx ON content.genre_film_work (film_work_id, genre_id);