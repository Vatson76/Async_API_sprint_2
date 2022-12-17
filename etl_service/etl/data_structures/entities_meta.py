from collections import namedtuple
from etl.data_structures.indices import movies_index, genres_index, persons_index
from etl.data_structures.sql_queries import movies_sql_query, genres_sql_query, persons_sql_query

EntityMeta = namedtuple("EntityMeta", ["index_data", "sql_query"])

movies_meta = EntityMeta(
    index_data=movies_index,
    sql_query=movies_sql_query
)

genres_meta = EntityMeta(
    index_data=genres_index,
    sql_query=genres_sql_query
)

persons_meta = EntityMeta(
    index_data=persons_index,
    sql_query=persons_sql_query
)

entities_meta = (movies_meta, genres_meta, persons_meta)
