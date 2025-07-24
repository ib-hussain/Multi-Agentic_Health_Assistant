-- custom types
CREATE TYPE gender_enum AS ENUM ('Female', 'Male');
CREATE TYPE diet_enum AS ENUM ('vegan', 'carnivore', 'both', 'balanced', 'vegetarian', 'pescatarian', 'any');
CREATE TYPE activity_enum AS ENUM ('not active', 'lightly active', 'active', 'very active');
CREATE TYPE progress_enum AS ENUM ('positive', 'negative', 'neutral');
CREATE TYPE user_info AS (
    name VARCHAR(100),
    age NUMERIC(4,1),
    gender gender_enum,
    height NUMERIC(4,3),
    weight NUMERIC(6,3)
);

CREATE TABLE IF NOT EXISTS user_profile (
    id SERIAL PRIMARY KEY,
    user_information user_info NOT NULL DEFAULT ROW(''::VARCHAR, 18.0, 'Female'::gender_enum, 1.700, 62.400),
    fitness_goal VARCHAR(90) NOT NULL DEFAULT 'Get into better shape',
    diet_pref diet_enum NOT NULL DEFAULT 'any',
    time_arr TIME[2][3] DEFAULT 
        '{{"12:00:00", NULL, NULL}, {"12:20:00", NULL, NULL}}',
    mental_health_background TEXT DEFAULT NULL,
    medical_conditions TEXT DEFAULT NULL,
    time_deadline INTEGER NOT NULL DEFAULT 90
);
CREATE TABLE IF NOT EXISTS daily_stats (
    id INTEGER PRIMARY KEY REFERENCES user_profile(id),
    today_date DATE NOT NULL DEFAULT CURRENT_DATE,
    activity_level activity_enum NOT NULL DEFAULT 'active',
    todays_flag BOOLEAN NOT NULL DEFAULT FALSE,
    days_done INTEGER NOT NULL DEFAULT 0,
    progress_condition progress_enum NOT NULL DEFAULT 'positive',
    days_left INTEGER
);
CREATE TABLE IF NOT EXISTS other_storage (
    id INTEGER PRIMARY KEY REFERENCES user_profile(id),
    picture_analysis VARCHAR(1000) DEFAULT '',
    audio_transcript VARCHAR(3000) DEFAULT ''
);

CREATE OR REPLACE FUNCTION insert_daily_stats(
    p_id INTEGER,
    p_activity_level activity_enum,
    p_progress_condition progress_enum)
RETURNS VOID AS $$
DECLARE
    v_days_done INTEGER := 0;
    v_days_left INTEGER;
    v_time_deadline INTEGER;
BEGIN
    -- Check if there's already a record for this user in daily_stats
    SELECT days_done INTO v_days_done
    FROM daily_stats
    WHERE id = p_id;

    -- If no record exists, COALESCE keeps it as 0 (default above)

    -- Increment days_done
    v_days_done := COALESCE(v_days_done, 0) + 1;

    -- Get the user's deadline from user_profile
    SELECT time_deadline INTO v_time_deadline
    FROM user_profile
    WHERE id = p_id;

    -- Calculate days_left
    v_days_left := v_time_deadline - v_days_done;

    -- Insert or update the daily_stats row
    INSERT INTO daily_stats (
        id,
        today_date,
        activity_level,
        todays_flag,
        progress_condition,
        days_done,
        days_left
    )
    VALUES (
        p_id,
        CURRENT_DATE,
        p_activity_level,
        TRUE,
        p_progress_condition,
        v_days_done,
        v_days_left
    )
    ON CONFLICT (id)
    DO UPDATE SET
        today_date = CURRENT_DATE,
        activity_level = EXCLUDED.activity_level,
        todays_flag = TRUE,
        progress_condition = EXCLUDED.progress_condition,
        days_done = EXCLUDED.days_done,
        days_left = EXCLUDED.days_left;
END;
$$ LANGUAGE plpgsql;
DROP FUNCTION insert_daily_stats(INTEGER, activity_enum, progress_enum);--to remove function from db
SELECT insert_daily_stats(1, 'active', 'positive');--dummy


-- user_profile table
UPDATE user_profile
SET user_information = ROW('', 18.0, 'Female', 1.700, 66.400)
WHERE user_information IS NULL;
UPDATE user_profile
SET fitness_goal = 'Get into better shape'
WHERE fitness_goal IS NULL;
UPDATE user_profile
SET diet_pref = 'any'
WHERE diet_pref IS NULL;
UPDATE user_profile
SET time_arr = '{{"12:00:00", NULL, NULL}, {"12:20:00", NULL, NULL}}'
WHERE time_arr IS NULL;
UPDATE user_profile
SET mental_health_background = NULL
WHERE mental_health_background IS NULL;
UPDATE user_profile
SET medical_conditions = NULL
WHERE medical_conditions IS NULL;
UPDATE user_profile
SET time_deadline = 90
WHERE time_deadline IS NULL;

-- daily_stats table
UPDATE daily_stats
SET activity_level = 'active'
WHERE activity_level IS NULL;
UPDATE daily_stats
SET todays_flag = FALSE
WHERE todays_flag IS NULL;
UPDATE daily_stats
SET days_done = 0
WHERE days_done IS NULL;
UPDATE daily_stats
SET progress_condition = 'positive'
WHERE progress_condition IS NULL;

-- other_storage table
UPDATE other_storage
SET picture_analysis = ''
WHERE picture_analysis IS NULL;

UPDATE other_storage
SET audio_transcript = ''
WHERE audio_transcript IS NULL;