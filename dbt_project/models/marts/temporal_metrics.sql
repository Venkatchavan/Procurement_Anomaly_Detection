-- Marts: Temporal analysis of contracts
-- Description: Time-series metrics for procurement activity

{{ config(
    materialized='table',
    tags=['marts', 'kpi', 'temporal']
) }}

WITH contracts AS (
    SELECT * FROM {{ ref('stg_procurement_contracts') }}
),

monthly_stats AS (
    SELECT
        DATE_TRUNC('month', award_date) AS month,
        COUNT(*) AS contract_count,
        SUM(contract_value) AS total_value,
        AVG(contract_value) AS avg_value,
        COUNT(DISTINCT vendor_id) AS unique_vendors,
        COUNT(DISTINCT contracting_authority) AS unique_authorities,
        SUM(CASE WHEN is_sustainable THEN 1 ELSE 0 END) AS sustainable_count
    FROM contracts
    GROUP BY DATE_TRUNC('month', award_date)
)

SELECT
    month,
    contract_count,
    total_value,
    avg_value,
    unique_vendors,
    unique_authorities,
    sustainable_count,
    CAST(sustainable_count AS FLOAT) / contract_count AS sustainability_rate,
    LAG(total_value) OVER (ORDER BY month) AS prev_month_value,
    (total_value - LAG(total_value) OVER (ORDER BY month)) / 
        NULLIF(LAG(total_value) OVER (ORDER BY month), 0) AS value_growth_rate
FROM monthly_stats
ORDER BY month
