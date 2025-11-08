 {{ config(materialized='table') }}

select
    cast(date as date) as price_date,
    price as price_usd
from
    {{ source('coingecko', 'raw_coingecko_bitcoin') }}