-- models/mart/mart_distributor_performance.sql

select
    distributor,
    report_date,
    count(distinct film) as num_films,
    max(number_of_countries) as max_number_of_countries,
    -- rank
    min(rank) as top_rank,
    case
        when min(rank) between 1 and 5 then 'top 5'
        when min(rank) between 6 and 10 then 'top 10'
        else 'top 15'
    end as top_rank_category,
    array_agg(distinct rank_category) as rank_categories,
    -- weeks on release
    max(weeks_on_release) as max_weeks_on_release,
    case
        when max(weeks_on_release) = 1 then 'new release'
        when max(weeks_on_release) between 2 and 4 then 'early run'
        else 'extended run'
    end as max_release_phase,
    array_agg(distinct release_phase) as release_phases,
    -- earnings
    avg(percent_change_on_last_week) as avg_change_vs_last_week,
    max(site_average) as max_site_average,
    max(number_of_cinemas) as max_number_of_cinemas,
    sum(weekend_gross) as total_weekend_gross,
    sum(total_gross_to_date) as total_gross_to_date

from {{ ref('int_movie_performance') }}
where distributor is not null
group by 
    distributor, 
    report_date
