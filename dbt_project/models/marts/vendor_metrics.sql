-- Marts: Vendor performance metrics
-- Description: Aggregates vendor-level KPIs

{{ config(
    materialized='table',
    tags=['marts', 'kpi']
) }}

WITH contracts AS (
    SELECT * FROM {{ ref('stg_procurement_contracts') }}
),

vendor_stats AS (
    SELECT
        vendor_id,
        vendor_name,
        COUNT(*) AS total_contracts,
        SUM(contract_value) AS total_value,
        AVG(contract_value) AS avg_contract_value,
        MIN(contract_value) AS min_contract_value,
        MAX(contract_value) AS max_contract_value,
        STDDEV(contract_value) AS stddev_contract_value,
        MIN(award_date) AS first_contract_date,
        MAX(award_date) AS latest_contract_date,
        SUM(CASE WHEN is_sustainable THEN 1 ELSE 0 END) AS sustainable_contracts,
        COUNT(DISTINCT contracting_authority) AS unique_authorities,
        COUNT(DISTINCT cpv_code) AS unique_categories
    FROM contracts
    GROUP BY vendor_id, vendor_name
),

vendor_metrics AS (
    SELECT
        *,
        CAST(sustainable_contracts AS FLOAT) / total_contracts AS sustainability_rate,
        DATEDIFF('day', first_contract_date, latest_contract_date) AS active_days,
        CASE 
            WHEN total_contracts >= 50 THEN 'High Volume'
            WHEN total_contracts >= 10 THEN 'Medium Volume'
            ELSE 'Low Volume'
        END AS volume_category
    FROM vendor_stats
)

SELECT * FROM vendor_metrics
ORDER BY total_value DESC
