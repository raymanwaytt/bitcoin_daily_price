WITH daily_data AS (
    SELECT * 
    FROM {{ ref('stg_coingecko_bitcoin') }}
),

metrics AS (
    SELECT
        price_date AS date,
        price_usd AS price,

        -- 7-day Moving Average
        AVG(price_usd) OVER (
            ORDER BY price_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS ma_7_day,

        -- 30-day Moving Average
        AVG(price_usd) OVER (
            ORDER BY price_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS ma_30_day,

        -- Previous Day Price
        LAG(price_usd) OVER (
            ORDER BY price_date
        ) AS prev_price,

        -- Running High (max seen so far)
        MAX(price_usd) OVER (
            ORDER BY price_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_high,

        -- 30-day Rolling Standard Deviation
        stddev_samp(price_usd) OVER (
        ORDER BY price_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS rolling_stddev_30_day
    FROM daily_data

)

SELECT
    date,
    price,
    ma_7_day,
    ma_30_day,

    -- Daily Return %
    COALESCE(
        (price - prev_price) / NULLIF(prev_price, 0) * 100,
        0
    ) AS daily_return_pct,

    -- Drawdown %
    COALESCE(
        (price - running_high) / NULLIF(running_high, 0) * 100,
        0
    ) AS drawdown_pct,

    -- 30-day Rolling Std Dev
    rolling_stddev_30_day

FROM metrics
ORDER BY date DESC