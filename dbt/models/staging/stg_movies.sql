-- models/staging/stg_movies.sql
{{ log("Building stg_movies from weekend_top_15_movies", info=True) }}

with source as (
    select * from {{ source("staging", "weekend_top_15_movies") }}
)
select * from source