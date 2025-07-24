import streamlit as st
import psycopg2
from datetime import datetime, timedelta
import os
debug =True 
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
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"]
    )
    cur = conn.cursor()
    return conn, cur
def close_db(conn, cur):
    try:
        cur.execute(last19477491_query)
        try:
            export_path = r"C:\Users\Ibrahim\Downloads\Internship\Multi-Agentic_Health_Assistant\data\\"
            cur.execute(f"""
            COPY user_profile TO '{export_path}user_profile.csv' WITH CSV HEADER;
            COPY daily_stats TO '{export_path}daily_stats.csv' WITH CSV HEADER;
            COPY other_storage TO '{export_path}other_storage.csv' WITH CSV HEADER;
            """)
            if debug: print(f"Exported")
        except Exception as e:
            if debug: print("Error during export:", e)
            conn.commit()
    except Exception as e:
        if debug: print("Error during export or view:", e)
    finally:
        cur.close()
        conn.close()
        if debug: print("Database connection closed.")
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
#functions ----------------------------------------------------------------------------------------------
def user_registration (
    name: str,
    Age: float,
    gender: str = 'Female',
    height_m: float = 1.700,
    Weight_kg: float = 66.400,
    fitness_goal: str = "Get into better shape",
    dietary_pref: str = "any",
    time_available: list = None,
    mental_health_notes: str = None,
    medical_conditions: str = None,
    time_deadline: int = 90,
    password: str = ''  ):
    conn, cur = connect_db()
    # Build time_arr 2D array
    if not time_available:
        time_arr = [['12:00:00', None, None], ['12:20:00', None, None]]
    else:
        row1, row2 = [], []
        for time_str in time_available[:3]:
            try:
                t1 = datetime.strptime(time_str, "%H:%M")
                t2 = (t1 + timedelta(minutes=20)).time()
                row1.append(t1.strftime("%H:%M:%S"))
                row2.append(t2.strftime("%H:%M:%S"))
            except:
                row1.append(None)
                row2.append(None)
        # Pad with None to make 3 elements
        while len(row1) < 3:
            row1.append(None)
            row2.append(None)
        time_arr = [row1, row2]
    try:
        cur.execute("""
            INSERT INTO user_profile (
                user_information, fitness_goal, diet_pref, time_arr,
                mental_health_background, medical_conditions, time_deadline,
                password 
            ) VALUES (
                ROW(%s, %s, %s, %s, %s),
                %s, %s, %s, %s, %s, %s
            )
            RETURNING id;
        """, (
            name, Age, gender, height_m, Weight_kg,
            fitness_goal, dietary_pref, time_arr,
            mental_health_notes, medical_conditions, time_deadline,
            password  # Include here
        ))
    except Exception as e:
        conn.rollback()
        if debug: print("Registration failed:", e)
    finally:
        close_db(conn, cur)
# user_information table functions
def change_name(old_name: str, new_name: str):
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_profile
            SET user_information = ROW(%s, (user_information).age, (user_information).gender,
                                       (user_information).height, (user_information).weight)
            WHERE (user_information).name = %s;
        """, (new_name, old_name))
        conn.commit()
        if debug: print("Name changed successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error changing name:", e)
    finally:
        close_db(conn, cur)
def change_age(name: str, new_age: float):
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_profile
            SET user_information = ROW((user_information).name, %s, (user_information).gender,
                                       (user_information).height, (user_information).weight)
            WHERE (user_information).name = %s;
        """, (new_age, name))
        conn.commit()
        if debug: print("Age updated successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating age:", e)
    finally:
        close_db(conn, cur)
def change_gender(name: str, new_gender: bool):
    conn, cur = connect_db()
    try:
        gender_value = 'Female' if new_gender else 'Male'
        cur.execute("""
            UPDATE user_profile
            SET user_information = ROW((user_information).name, (user_information).age, %s,
                                       (user_information).height, (user_information).weight)
            WHERE (user_information).name = %s;
        """, (gender_value, name))
        conn.commit()
        if debug: print("Gender updated successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating gender:", e)
    finally:
        close_db(conn, cur)
def change_weight(name: str, new_weight: float):
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_profile
            SET user_information = ROW((user_information).name, (user_information).age, (user_information).gender,
                                       (user_information).height, %s)
            WHERE (user_information).name = %s;
        """, (new_weight, name))
        conn.commit()
        if debug: print("Weight updated successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating weight:", e)
    finally:
        close_db(conn, cur)
def change_height(name: str, new_height: float):
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_profile
            SET user_information = ROW((user_information).name, (user_information).age, (user_information).gender,
                                       %s, (user_information).weight)
            WHERE (user_information).name = %s;
        """, (new_height, name))
        conn.commit()
        if debug: print("Height updated successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating height:", e)
    finally:
        close_db(conn, cur)

def change_dietary_pref(name: str, new_pref: str):
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_profile
            SET diet_pref = %s
            WHERE (user_information).name = %s;
        """, (new_pref, name))
        conn.commit()
        if debug: print("Dietary preference updated successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating dietary preference:", e)
    finally:
        close_db(conn, cur)
def change_time_deadline(name: str, days: int):
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_profile
            SET time_deadline = %s
            WHERE (user_information).name = %s;
        """, (days, name))
        conn.commit()
        if debug: print("Time deadline updated successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating time deadline:", e)
    finally:
        close_db(conn, cur)

def parse_time_string(time_str):
    return datetime.strptime(time_str, "%H:%M").time()
def add_20_minutes(time_obj):
    dt = datetime.combine(datetime.today(), time_obj) + timedelta(minutes=20)
    return dt.time()
def change_time_available(name: str, start_time: str):
    conn, cur = connect_db()
    try:
        t1 = parse_time_string(start_time)
        t2 = add_20_minutes(t1)
        arr = [[t1.strftime('%H:%M:%S'), None, None],
               [t2.strftime('%H:%M:%S'), None, None]] 
        cur.execute("""
            UPDATE user_profile
            SET time_arr = %s
            WHERE (user_information).name = %s;
        """, (arr, name))
        conn.commit()
        if debug: print("Time availability changed successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating time availability:", e)
    finally:
        close_db(conn, cur)
def append_time_available(name: str, start_time: str):
    conn, cur = connect_db()
    try:
        cur.execute("""
            SELECT time_arr FROM user_profile
            WHERE (user_information).name = %s;
        """, (name,))
        result = cur.fetchone()
        
        if not result or not result[0]:
            if debug: print("User not found or time_arr is NULL.")
            return

        t1 = parse_time_string(start_time)
        t2 = add_20_minutes(t1)
        arr = result[0]  # time_arr is a 2D array

        inserted = False
        for col in range(3):
            if arr[0][col] is None and arr[1][col] is None:
                arr[0][col] = t1.strftime('%H:%M:%S')
                arr[1][col] = t2.strftime('%H:%M:%S')
                inserted = True
                break

        if not inserted:
            if debug: print("All 3 time ranges already filled.")
            return

        cur.execute("""
            UPDATE user_profile
            SET time_arr = %s
            WHERE (user_information).name = %s;
        """, (arr, name))
        
        conn.commit()
        if debug: print("Time range appended successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error appending time range:", e)
    finally:
        close_db(conn, cur)

def change_fitness_goal(name: str, new_goal: str):
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_profile
            SET fitness_goal = %s
            WHERE (user_information).name = %s;
        """, (new_goal, name))
        conn.commit()
        if debug: print("Fitness goal updated successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating fitness goal:", e)
    finally:
        close_db(conn, cur)
def append_fitness_goal(name: str, additional_goal: str):
    conn, cur = connect_db()
    try:
        cur.execute("""
            SELECT fitness_goal FROM user_profile
            WHERE (user_information).name = %s;
        """, (name,))
        result = cur.fetchone()
        if not result:
            if debug: print("User not found.")
            return
        goals = result[0]
        if goals:
            goals = goals + "; " + additional_goal
        else:
            goals = additional_goal
        cur.execute("""
            UPDATE user_profile
            SET fitness_goal = %s
            WHERE (user_information).name = %s;
        """, (goals, name))
        conn.commit()
        if debug: print("Fitness goal appended successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error appending fitness goal:", e)
    finally:
        close_db(conn, cur)

def change_mental_health_notes(name: str, notes: str):
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_profile
            SET mental_health_background = %s
            WHERE (user_information).name = %s;
        """, (notes, name))
        conn.commit()
        if debug: print("Mental health notes updated successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating mental health notes:", e)
    finally:
        close_db(conn, cur)
def append_mental_health_notes(name: str, note: str):
    conn, cur = connect_db()
    try:
        cur.execute("""
            SELECT mental_health_background FROM user_profile
            WHERE (user_information).name = %s;
        """, (name,))
        result = cur.fetchone()
        if not result:
            if debug: print("User not found.")
            return
        notes = result[0]
        if notes:
            notes = notes + "\n" + note
        else:
            notes = note
        cur.execute("""
            UPDATE user_profile
            SET mental_health_background = %s
            WHERE (user_information).name = %s;
        """, (notes, name))
        conn.commit()
        if debug: print("Mental health note appended successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error appending mental health note:", e)
    finally:
        close_db(conn, cur)

def change_medical_conditions(name: str, condition: str):
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_profile
            SET medical_conditions = %s
            WHERE (user_information).name = %s;
        """, (condition, name))
        conn.commit()
        if debug: print("Medical condition updated successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating medical condition:", e)
    finally:
        close_db(conn, cur)
def append_medical_conditions(name: str, condition: str):
    conn, cur = connect_db()
    try:
        cur.execute("""
            SELECT medical_conditions FROM user_profile
            WHERE (user_information).name = %s;
        """, (name,))
        result = cur.fetchone()
        if not result:
            if debug: print("User not found.")
            return
        conditions = result[0]
        if conditions:
            conditions = conditions + "\n" + condition
        else:
            conditions = condition
        cur.execute("""
            UPDATE user_profile
            SET medical_conditions = %s
            WHERE (user_information).name = %s;
        """, (conditions, name))
        conn.commit()
        if debug: print("Medical condition appended successfully.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error appending medical condition:", e)
    finally:
        close_db(conn, cur)

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
            "id": result[0],
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
        return profile
    except Exception as e:
        if debug: print("Error fetching user profile:", e)
        return None
    finally:
        close_db(conn, cur)
# daily_stats table functions
def insert_daily_stats_entry(user_id: int, activity_level: str, progress_condition: str):
    conn, cur = connect_db()
    try:
        cur.execute("""
            SELECT insert_daily_stats(%s, %s, %s);
        """, (user_id, activity_level, progress_condition))
        conn.commit()
        if debug: print(f"Daily stats inserted for user ID {user_id}")
    except Exception as e:
        conn.rollback()
        if debug: print("Error inserting daily stats:", e)
    finally:
        close_db(conn, cur)
def get_daily_stats_by_id(user_id: int):
    conn, cur = connect_db()
    try:
        cur.execute("SELECT * FROM daily_stats WHERE id = %s;", (user_id,))
        result = cur.fetchone()
        if debug:
            print("Daily stats fetched:", result)
        return result
    except Exception as e:
        if debug: print("Error fetching daily stats:", e)
        return None
    finally:
        close_db(conn, cur)
# other_storage table functions
def get_picture_analysis(user_id: int):
    conn, cur = connect_db()
    try:
        cur.execute("SELECT picture_analysis FROM other_storage WHERE id = %s;", (user_id,))
        result = cur.fetchone()
        if debug: print("Picture analysis fetched:", result)
        return result[0] if result else None
    except Exception as e:
        if debug: print("Error fetching picture analysis:", e)
        return None
    finally:
        close_db(conn, cur)
def set_picture_analysis(user_id: int, text: str):##maybe promt engineer this later to add something to the standard prompt provided by the llama model
    conn, cur = connect_db()
    try:
        cur.execute("UPDATE other_storage SET picture_analysis = %s WHERE id = %s;", (text, user_id))
        conn.commit()
        if debug: print("Picture analysis updated.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating picture analysis:", e)
    finally:
        close_db(conn, cur)
def remove_picture_analysis(user_id: int):
    conn, cur = connect_db()
    try:
        cur.execute("UPDATE other_storage SET picture_analysis = NULL WHERE id = %s;", (user_id,))
        conn.commit()
        if debug: print("Picture analysis removed.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error removing picture analysis:", e)
    finally:
        close_db(conn, cur)

def get_audio_transcript(user_id: int):
    conn, cur = connect_db()
    try:
        cur.execute("SELECT audio_transcript FROM other_storage WHERE id = %s;", (user_id,))
        result = cur.fetchone()
        if debug: print("Audio transcript fetched:", result)
        return result[0] if result else None
    except Exception as e:
        if debug: print("Error fetching audio transcript:", e)
        return None
    finally:
        close_db(conn, cur)
def set_audio_transcript(user_id: int, text: str):
    conn, cur = connect_db()
    try:
        cur.execute("UPDATE other_storage SET audio_transcript = %s WHERE id = %s;", (text, user_id))
        conn.commit()
        if debug: print("Audio transcript updated.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error updating audio transcript:", e)
    finally:
        close_db(conn, cur)
def remove_audio_transcript(user_id: int):
    conn, cur = connect_db()
    try:
        cur.execute("UPDATE other_storage SET audio_transcript = NULL WHERE id = %s;", (user_id,))
        conn.commit()
        if debug: print("Audio transcript removed.")
    except Exception as e:
        conn.rollback()
        if debug: print("Error removing audio transcript:", e)
    finally:
        close_db(conn, cur)

def get_other_storage_by_id(user_id: int):
    conn, cur = connect_db()
    try:
        cur.execute("SELECT * FROM other_storage WHERE id = %s;", (user_id,))
        result = cur.fetchone()
        if debug:
            print("Other storage fetched:", result)
        return result
    except Exception as e:
        if debug: print("Error fetching other storage:", e)
        return None
    finally:
        close_db(conn, cur)
#functions ----------------------------------------------------------------------------------------------