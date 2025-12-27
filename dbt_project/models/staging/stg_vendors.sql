-- Staging: Vendor master data
-- Description: Standardizes vendor information

{{ config(
    materialized='view',
    tags=['staging', 'vendors']
) }}

WITH source AS (
    SELECT DISTINCT
        vendor_id,
        vendor_name,
        country_code
    FROM {{ source('raw', 'procurement_contracts') }}
),

cleaned AS (
    SELECT
        TRIM(vendor_id) AS vendor_id,
        TRIM(vendor_name) AS vendor_name,
        UPPER(TRIM(country_code)) AS country_code,
        CASE 
            WHEN vendor_name LIKE '%SME%' OR vendor_name LIKE '%small%' THEN 'SME'
            WHEN vendor_name LIKE '%Corp%' OR vendor_name LIKE '%Inc%' THEN 'Large'
            ELSE 'Unknown'
        END AS vendor_size
    FROM source
    WHERE vendor_id IS NOT NULL
)

SELECT * FROM cleaned
