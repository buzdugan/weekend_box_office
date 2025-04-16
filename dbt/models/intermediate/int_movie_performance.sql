-- models/intermediate/int_movie_performance.sql

select
    report_date,
    film,
    distributor,
    country_of_origin,
    -- number of countries
    array_length(split(country_of_origin, '/')) as number_of_countries,
    rank,
    -- rank category
    case
        when rank between 1 and 5 then 'top 5'
        when rank between 6 and 10 then 'top 10'
        else 'top 15'
    end as rank_category,
    weekend_gross,
    total_gross_to_date,
    round(percent_change_on_last_week, 2) as percent_change_on_last_week,
    -- week trend
    case
        when percent_change_on_last_week > 0 then 'up'
        when percent_change_on_last_week < 0 then 'down'
        else 'no change'
    end as week_trend,
    weeks_on_release,
    -- release phase
    case
        when weeks_on_release = 1 then 'new release'
        when weeks_on_release between 2 and 4 then 'early run'
        else 'extended run'
    end as release_phase,
    number_of_cinemas,
    site_average

from {{ ref('stg_movies') }}