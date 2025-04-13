-- models/staging/stg_movies.sql
select
  *
from {{ source('uk_movies', 'weekend_top_15_movies') }}