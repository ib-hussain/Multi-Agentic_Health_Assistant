'''
Database handler for the Multi-Agentic Health Assistant project.
This header provides functions to interact with the PostgreSQL database,
including user registration, profile management, daily stats, and other storage functionalities.
'''

import streamlit as st
import psycopg2
from datetime import datetime, timedelta, time
import os
debug = True  

# issues:
# use the other storage table to store old chats of user in some form so that they can be loaded later
# put a change password function and then put a password changing field in the website.py file
# put a change time function and field in the interface
# add some alarm functionality that makes everything happen at the required times and maybe some alarm functionality
# add some 24 hour cycle routine that puts in changes in the database

last19477491_query = """
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
UPDATE user_profile
SET password = ''
WHERE password IS NULL;

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
"""

def connect_db():
    # Establish connection to PostgreSQL
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cur = conn.cursor()
    return conn, cur
def close_db(conn, cur):
    cur.close()
    conn.close()
    if debug: print("Database connection closed.")
    # try:
        # cur.execute(last19477491_query)
    #     try:
    #         export_path = r"C:\Users\Ibrahim\Downloads\Internship\Multi-Agentic_Health_Assistant\data\\"
    #         # cur.execute(f"""
    #         # {"--" if debug else""}COPY user_profile TO '{export_path}user_profile.csv' WITH CSV HEADER;
    #         # {"--" if debug else""}COPY daily_stats TO '{export_path}daily_stats.csv' WITH CSV HEADER;
    #         # {"--" if debug else""}COPY other_storage TO '{export_path}other_storage.csv' WITH CSV HEADER;
    #         # """)
    #         # if debug: print(f"Exported")
    #     except Exception as e:
    #         if debug: print("Error during export:", e)
    #         # conn.commit()
    # except Exception as e:
    #     if debug: print("Error during export or view:", e)
    # finally:
    #     cur.close()
    #     conn.close()
    #     if debug: print("Database connection closed.")
    # cur.close()
    # conn.close()
    # if debug: print("Database connection closed.")
# Login:
def get_id(name: str, password: str):
    conn, cur = connect_db()
    try:
        cur.execute("""
            SELECT * FROM user_profile 
            WHERE (user_information).name = %s 
            AND 
            password = %s;
        """, (name, password))
        result = cur.fetchone()
        if result:
            if debug: print(f"ID found for user '{name}'.")
            return result[0]
        else:
            if debug: print("Invalid name or password.")
            return None
    except Exception as e:
        if debug: print("Error validating user:", e)
        return None
    finally:
        close_db(conn, cur)
# Signup:
def user_registration(
    name: str,
    Age: float,
    gender: str = 'Female',
    height_m: float = 1.700,
    Weight_kg: float = 66.400,
    fitness_goal: str = "Get into better shape",
    dietary_pref: str = "any",
    time_available=None,
    mental_health_notes: str = None,
    medical_conditions: str = None,
    time_deadline: int = 90,
    password: str = '12345678'):
    conn, cur = connect_db()
    if gender=="female": gender = "Female"
    if gender=="male": gender = "Male"
    else: gender = "Female"
    try:
        # Convert time strings to time objects
        time_objects = None
        if time_available:
            time_objects = []
            for time_str in time_available:
                # Parse '09:00' format
                hour, minute = map(int, time_str.split(':'))
                time_objects.append(time(hour, minute))
        
        cur.execute("""
            INSERT INTO user_profile (
                user_information, 
                fitness_goal, diet_pref, time_arr,
                mental_health_background, medical_conditions, time_deadline,
                password 
            ) VALUES (
                ROW(%s, %s, %s, %s, %s),
                %s, %s, %s, 
                %s, %s, %s,
                %s
            )
            RETURNING id;
        """, (
            name, Age, gender, height_m, Weight_kg,
            fitness_goal, dietary_pref, time_objects,
            mental_health_notes, medical_conditions, time_deadline,
            password
        ))
        result = cur.fetchone()
        conn.commit()
        if debug: 
            print(f"User {name} registered successfully with ID: {result[0]}")
        return result[0]
    except Exception as e:
        conn.rollback()
        if debug:
            print("Registration failed:", e)
        raise e
    finally:
        close_db(conn, cur)
# Diet Agent:
def get_fitness_goal_diet_gender_age_time_deadline(user_id: int):
    conn, cur = connect_db()
    try:
        cur.execute("SELECT fitness_goal, diet_pref, (user_information).gender, (user_information).name, (user_information).age, medical_conditions, time_deadline FROM user_profile WHERE id = %s;", (user_id,))
        result = cur.fetchone()
        result2 =  result+(conn, cur)
        return result2
    except Exception as e:  
        if debug: print("Error fetching one of fitness goal, diet preferences, gender, age, medical conditions and time deadline:", e)
        return tuple('Get into better shape', 'any', 'Female', 18.0, " ", 90 )
def daily_height_weight_diet_hist(user_id: int, conn, cur):
    try:
        cur.execute("""
                    SELECT height, weight, diet_history
                    FROM daily_stats 
                    WHERE id = %s AND days_done = (
                        SELECT MAX(days_done) 
                        FROM daily_stats 
                        WHERE id = %s
                    );
                """, (user_id, user_id))
        result = cur.fetchone()
        if debug: print(result)
        if not result:
            cur.execute("""
                    SELECT (user_information).height, (user_information).weight, diet_pref 
                    FROM user_profile 
                    WHERE id = %s;
                """, (user_id,))
            result = cur.fetchone()
            if debug: print(result)
        close_db(conn, cur)
        return result
    except Exception as e:  
        if debug: print("Error fetching one of height, weight, diet history:", e)
        return tuple(1.700, 66.400, ' ')
    finally:
        close_db(conn, cur)


# Profile Management: 
def get_user_profile_by_id(user_id: int):
    conn, cur = connect_db()
    try:
        cur.execute("""
            SELECT 
                id,
                (user_information).name,
                (user_information).age,
                (user_information).gender,
                (user_information).height,
                (user_information).weight,
                fitness_goal,
                diet_pref,
                time_arr,
                mental_health_background,
                medical_conditions,
                time_deadline,
                password  -- explicitly selecting password
            FROM user_profile
            WHERE id = %s;
        """, (user_id,))
        result = cur.fetchone()
        if not result:
            if debug: print("No user found with that ID.")
            return None
        profile = {
            "name": result[1],
            "age": result[2],
            "gender": result[3],
            "height": result[4],
            "weight": result[5],
            "fitness_goal": result[6],
            "diet_pref": result[7],
            "time_arr": result[8],
            "mental_health_background": result[9],
            "medical_conditions": result[10],
            "time_deadline": result[11],
            "password": result[12]  # Include password here
        }
        if debug:
            print("User profile fetched:", profile)
        close_db(conn, cur)
        return profile
    except Exception as e:
        if debug: print("Error fetching user profile:", e)
        return None
    finally:
        close_db(conn, cur)

# not good:
def change_everything(
    name: str,
    new_age: float,
    new_gender: bool, 
    new_weight: float, 
    new_height: float, 
    new_pref: str, 
    days: int, 
    new_goal: str, 
    notes: str, 
    condition: str):
    conn, cur = connect_db()
    try:
        # Convert gender boolean to string once
        gender_value = 'Female' if new_gender else 'Male'
        # Single query to update all fields at once
        cur.execute("""
            UPDATE user_profile
            SET user_information = ROW(%s, %s, %s, %s, %s),
                diet_pref = %s,
                time_deadline = %s,
                fitness_goal = %s,
                mental_health_background = %s,
                medical_conditions = %s
            WHERE (user_information).name = %s;
        """, (name, new_age, gender_value, new_height, new_weight, 
              new_pref, days, new_goal, notes, condition, name))
        # Single commit for all changes
        conn.commit()
        if debug: 
            print("All user profile fields updated successfully.")
    except Exception as e:
        conn.rollback()
        if debug: 
            print("Error updating user profile:", e)
        raise  # Re-raise the exception to maintain error handling behavior
    finally:
        close_db(conn, cur)


# Progress Page: 
def create_daily_entry(user_id: int, activity_level: str) -> bool:
    """Creates new daily entry with activity level and today's date, other fields NULL"""
    conn, cur = None, None
    try:
        conn, cur = connect_db()
        cur.execute("""
            INSERT INTO daily_stats 
            (id, today_date, activity_level, 
             height, weight, progress_condition, diet_history, todays_flag)
            VALUES (%s, CURRENT_DATE, %s, NULL, NULL, NULL, NULL, FALSE)
            RETURNING entry_id;
        """, (user_id, activity_level))
        conn.commit()
        if debug: 
            entry_id = cur.fetchone()[0]
            print(f"Created new daily entry for user {user_id}, entry ID: {entry_id}")
        return True
    except Exception as e:
        if conn: conn.rollback()
        if debug: print(f"Error creating daily entry: {e}")
        return False
    finally:
        close_db(conn, cur)
def update_height_if_empty(user_id: int, height: float) -> bool:
    """Updates height only if current value is NULL"""
    conn, cur = None, None
    try:
        conn, cur = connect_db()
        cur.execute("""
            UPDATE daily_stats
            SET height = %s
            WHERE id = %s 
              AND today_date = CURRENT_DATE 
              AND height IS NULL
            RETURNING entry_id;
        """, (height, user_id))
        updated = cur.rowcount > 0
        conn.commit()
        if debug: 
            if updated:
                print(f"Height updated for user {user_id}")
            else:
                print(f"Height not updated (already set) for user {user_id}")
        return updated
    except Exception as e:
        if conn: conn.rollback()
        if debug: print(f"Error updating height: {e}")
        return False
    finally:
        close_db(conn, cur)
def update_weight_if_empty(user_id: int, weight: float) -> bool:
    """Updates weight only if current value is NULL"""
    conn, cur = None, None
    try:
        conn, cur = connect_db()
        cur.execute("""
            UPDATE daily_stats
            SET weight = %s
            WHERE id = %s 
              AND today_date = CURRENT_DATE 
              AND weight IS NULL
            RETURNING entry_id;
        """, (weight, user_id))
        updated = cur.rowcount > 0
        conn.commit()
        if debug: 
            if updated:
                print(f"Weight updated for user {user_id}")
            else:
                print(f"Weight not updated (already set) for user {user_id}")
        return updated
    except Exception as e:
        if conn: conn.rollback()
        if debug: print(f"Error updating weight: {e}")
        return False
    finally:
        close_db(conn, cur)
def update_progress_if_empty(user_id: int, progress_condition: str) -> bool:
    """Updates progress condition only if current value is NULL"""
    conn, cur = None, None
    try:
        conn, cur = connect_db()
        cur.execute("""
            UPDATE daily_stats
            SET progress_condition = %s
            WHERE id = %s 
              AND today_date = CURRENT_DATE 
              AND progress_condition IS NULL
            RETURNING entry_id;
        """, (progress_condition, user_id))
        updated = cur.rowcount > 0
        conn.commit()
        if debug: 
            if updated:
                print(f"Progress updated for user {user_id}")
            else:
                print(f"Progress not updated (already set) for user {user_id}")
        return updated
    except Exception as e:
        if conn: conn.rollback()
        if debug: print(f"Error updating progress: {e}")
        return False
    finally:
        close_db(conn, cur)
def complete_entry_if_empty(user_id: int, diet_history: str) -> bool:
    """Completes entry by setting diet history and flag, only if currently NULL/FALSE"""
    conn, cur = None, None
    try:
        conn, cur = connect_db()
        cur.execute("""
            UPDATE daily_stats
            SET diet_history = %s, 
                todays_flag = TRUE
            WHERE id = %s 
              AND today_date = CURRENT_DATE 
              AND (diet_history IS NULL OR todays_flag = FALSE)
            RETURNING entry_id;
        """, (diet_history, user_id))
        updated = cur.rowcount > 0
        conn.commit()
        if debug: 
            if updated:
                print(f"Entry completed for user {user_id}")
            else:
                print(f"Entry already completed for user {user_id}")
        return updated
    except Exception as e:
        if conn: conn.rollback()
        if debug: print(f"Error completing entry: {e}")
        return False
    finally:
        close_db(conn, cur)
# Perfect:
def get_daily_stats_by_id(user_id: int) -> list[list]:
    """
    Fetch all daily stats for a user, ordered by days_done (ascending).
    Returns 2D list in specified order excluding entry_id, id, and todays_flag.
    Args:
        user_id: The user ID to fetch stats for
        debug: Whether to print debug messages
    Returns:
        List of rows in this order:
        [today_date, progress_condition, activity_level, days_done, 
         days_left, height, weight, diet_history]
        Returns empty list if no results or error occurs
    """
    try:
        conn, cur = connect_db()
        # Query with columns in specified order, excluding todays_flag
        query = """
        SELECT 
            today_date, progress_condition, activity_level, 
            days_done, days_left, height, weight, diet_history
        FROM daily_stats 
        WHERE id = %s
        ORDER BY days_done ASC;
        """
        cur.execute(query, (user_id,))
        rows = cur.fetchall()
        if debug:
            print(f"Fetched {len(rows)} rows for user {user_id}")
            for row in rows:
                print(row)
        # Convert each row tuple to a list
        return [list(row) for row in rows]
    except Exception as e:
        if debug:
            print(f"Error fetching daily stats for user {user_id}: {e}")
        return []  # Return empty list on error (not [[], []])
    finally:
        close_db(conn, cur)


# other_storage table functions
def get_other_storage_by_id(user_id: int):
    conn, cur = connect_db()
    # this has nothing
    close_db(conn, cur)
#functions ----------------------------------------------------------------------------------------------