



















-- -- === EXISTING COLUMN DEFAULTS === --
-- ALTER TABLE user_health_info
-- ALTER COLUMN weight_kg SET DEFAULT 66.40;

-- ALTER TABLE user_health_info
-- ALTER COLUMN height_m SET DEFAULT 1.70;

-- ALTER TABLE user_health_info
-- ALTER COLUMN fitness_goal SET DEFAULT 'Get into better shape';

-- ALTER TABLE user_health_info
-- ALTER COLUMN activity_level SET DEFAULT 'active';

-- -- === NULL FIX FOR EXISTING RECORDS === --
-- UPDATE user_health_info
-- SET weight_kg = 66.40
-- WHERE weight_kg IS NULL;

-- UPDATE user_health_info
-- SET height_m = 1.70
-- WHERE height_m IS NULL;

-- UPDATE user_health_info
-- SET fitness_goal = 'Get into better shape'
-- WHERE fitness_goal IS NULL;

-- UPDATE user_health_info
-- SET activity_level = 'active'
-- WHERE activity_level IS NULL;

-- UPDATE user_health_info
-- SET dietary_pref = 'any'
-- WHERE dietary_pref IS NULL;

-- UPDATE user_health_info
-- SET time_available = '12:00–12:20'
-- WHERE time_available IS NULL;
-- -- === OUTPUT FINAL TABLE AND EXPORT === --
-- SELECT * FROM user_health_info;
-- COPY user_health_info TO 'C:\Users\Ibrahim\Downloads\Internship\Multi-Agentic_Health_Assistant\data\user_health_info.csv' WITH CSV HEADER;