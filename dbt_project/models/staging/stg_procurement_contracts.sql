-- Staging: Raw procurement data cleaning
-- Description: Cleans and standardizes raw procurement contract data

{{ config(
    materialized='view',
    tags=['staging', 'procurement']
) }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'procurement_contracts') }}
),

cleaned AS (
    SELECT
        contract_id,
        TRIM(contract_title) AS contract_title,
        CAST(contract_value AS DECIMAL(15,2)) AS contract_value,
        CAST(award_date AS DATE) AS award_date,
        CAST(publish_date AS DATE) AS publish_date,
        TRIM(vendor_name) AS vendor_name,
        TRIM(vendor_id) AS vendor_id,
        TRIM(contracting_authority) AS contracting_authority,
        TRIM(cpv_code) AS cpv_code,
        TRIM(cpv_description) AS cpv_description,
        TRIM(procedure_type) AS procedure_type,
        CASE 
            WHEN sustainability_label IN ('green', 'eco', 'sustainable') THEN TRUE
            ELSE FALSE
        END AS is_sustainable,
        TRIM(country_code) AS country_code,
        TRIM(region) AS region
    FROM source
    WHERE contract_id IS NOT NULL
      AND contract_value > 0
      AND award_date IS NOT NULL
)

SELECT * FROM cleaned
