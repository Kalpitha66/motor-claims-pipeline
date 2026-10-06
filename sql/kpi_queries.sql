-- Claim frequency = number of claims / years of exposure.
-- It is the first building block of a motor premium.

-- name: portfolio_summary
SELECT
    COUNT(*)                                   AS policies,
    ROUND(SUM(Exposure), 0)                    AS exposure_years,
    SUM(ClaimNb)                               AS claims,
    ROUND(SUM(ClaimNb) * 1.0 / SUM(Exposure), 4) AS claim_frequency
FROM policies;

-- name: frequency_by_driver_age
SELECT
    DrivAgeBand,
    COUNT(*)                                   AS policies,
    ROUND(SUM(Exposure), 0)                    AS exposure_years,
    SUM(ClaimNb)                               AS claims,
    ROUND(SUM(ClaimNb) * 1.0 / SUM(Exposure), 4) AS claim_frequency
FROM policies
GROUP BY DrivAgeBand
ORDER BY MIN(DrivAge);  -- sort bands by age, not alphabetically

-- name: frequency_by_bonus_malus
SELECT
    BonusMalusBand,
    COUNT(*)                                   AS policies,
    ROUND(SUM(Exposure), 0)                    AS exposure_years,
    SUM(ClaimNb)                               AS claims,
    ROUND(SUM(ClaimNb) * 1.0 / SUM(Exposure), 4) AS claim_frequency
FROM policies
GROUP BY BonusMalusBand
ORDER BY MIN(BonusMalus);

-- name: frequency_by_area
SELECT
    Area,
    COUNT(*)                                   AS policies,
    ROUND(AVG(Density), 0)                     AS avg_density,
    ROUND(SUM(ClaimNb) * 1.0 / SUM(Exposure), 4) AS claim_frequency
FROM policies
GROUP BY Area
ORDER BY Area;

-- name: frequency_by_vehicle_age
SELECT
    VehAgeBand,
    COUNT(*)                                   AS policies,
    ROUND(SUM(ClaimNb) * 1.0 / SUM(Exposure), 4) AS claim_frequency
FROM policies
GROUP BY VehAgeBand
ORDER BY MIN(VehAge);
