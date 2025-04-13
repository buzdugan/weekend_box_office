-- models/marts/mart_distributor_performance.sql

select
    distributor,
    count(distinct film) as total_films,
    sum(total_weekend_gross) as total_grossed_weekends,
    max(latest_total_gross) as top_film_gross,
    round(avg(avg_site_average), 0) as average_site_score

from {{ ref('int_movie_aggregates') }}
group by distributor
order by total_grossed_weekends desc
