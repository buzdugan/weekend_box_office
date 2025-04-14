-- models/intermediate/int_movie_aggregates.sql

select
    distributor,
    film,
    count(distinct report_date) as num_weeks_in_top_15,
    sum(weekend_gross) as total_weekend_gross,
    max(total_gross_to_date) as latest_total_gross,
    round(avg(site_average), 2) as avg_site_average

from {{ ref('stg_movies') }}
group by 
    distributor,
    film