-- models/staging/stg_movies.sql


with source as (
    select * from {{ source("staging", "weekend_top_15_movies") }}
)
select * from source