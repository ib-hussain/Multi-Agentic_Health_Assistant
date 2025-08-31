'''
Database handler for the Multi-Agentic Health Assistant project.
This header provides functions to interact with the PostgreSQL database,
including user registration, profile management, daily stats, and other storage functionalities.
'''
import psycopg2
from datetime import datetime, timedelta, time
import os
import threading
debug = True  
# issues:
# add some alarm functionality that makes everything happen at the required times and maybe some alarm functionality
# add some 24 hour cycle routine that puts in changes in the database

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
                password 
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
            "password": result[12]  
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
def change_everything(
    user_id: int,
    new_name: str,
    new_age: float,
    new_gender: bool,   # True -> 'Female', False -> 'Male'
    new_weight: float,
    new_height: float,
    new_pref: str,
    days: int,
    new_goal: str,
    notes: str,
    condition: str,
    new_password: str,   # REQUIRED
    time_arr: list       # REQUIRED, e.g. ["06:00","09:00"]
    ):
    """
    Updates ALL profile fields for the given user_id.
    - Uses id in WHERE (so name can change safely).
    - Coerces "HH:MM" strings to TIME objects for Postgres.
    """
    from datetime import time as dt_time 
    conn, cur = connect_db()
    try:
        gender_value = 'Female' if new_gender else 'Male'
        # coerce incoming strings -> TIME[]
        time_objects = None
        if time_arr:
            time_objects = []
            for t in time_arr:
                s = str(t).strip()
                if not s:
                    continue
                hh, mm = s.split(':')[0:2]
                time_objects.append(dt_time(int(hh), int(mm)))
        sql = """
            UPDATE user_profile
            SET user_information = ROW(%s, %s, %s, %s, %s),
                diet_pref = %s,
                time_deadline = %s,
                fitness_goal = %s,
                mental_health_background = %s,
                medical_conditions = %s,
                password = %s,
                time_arr = %s
            WHERE id = %s;
        """
        params = (
            new_name, new_age, gender_value, new_height, new_weight,
            new_pref, days, new_goal, notes, condition,
            new_password, time_objects,
            user_id
        )
        cur.execute(sql, params)
        conn.commit()
        if debug:
            print("All user profile fields updated successfully (by id).")
    except Exception as e:
        conn.rollback()
        if debug:
            print("Error updating user profile:", e)
        raise
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
# Chat History Storage
def store_chat_postgres(user_id:int, user_prompt:str, response:str, has_image: bool = False):
    """Fire-and-forget function to store chat in database without waiting"""
    def store_chat_thread():
        try:
            # Add image indicator to the user prompt if an image was attached
            final_user_prompt = user_prompt
            if has_image:
                final_user_prompt = user_prompt + " [Image Attached]"
            conn, cur = connect_db()
            insert_query = """
                INSERT INTO chat_history (id, user_prompt, system_response, time_entered)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """
            cur.execute(insert_query, (user_id, final_user_prompt, response))
            conn.commit()
            if debug: print("Chat stored successfully.")
        except Exception as e:
            if debug: print(f"Error storing chat: {e}")
        finally:
            close_db(conn, cur)
    # Start the database operation in a separate thread and don't wait for it
    thread = threading.Thread(target=store_chat_thread, daemon=True)
    thread.start()
def get_chat_history_by_date(user_id: int, year: int = None, month: int = None, day: int = None) :
    """
    Retrieves chat history for a specific user and date, ordered by time (oldest first).
    Defaults to today's date if no date parameters are provided.
    
    Args:
        user_id (int): The user ID to fetch chat history for
        year (int): Year (e.g., 2024) - defaults to current year
        month (int): Month (1-12) - defaults to current month
        day (int): Day (1-31) - defaults to current day
        
    Returns:
        List of dictionaries containing chat records with 'time_entered', 'user_prompt', and 'system_response'
    """
    try:
        # Get current date if any parameter is None
        if year is None or month is None or day is None:
            today = datetime.now()
            year = today.year
            month = today.month
            day = today.day
        conn, cur = connect_db()
        # Construct the query to get chat history for a specific date
        query = """
            SELECT time_entered, user_prompt, system_response
            FROM chat_history
            WHERE id = %s
            AND DATE(time_entered) = %s
            ORDER BY time_entered ASC
        """
        target_date = f"{year:04d}-{month:02d}-{day:02d}"
        cur.execute(query, (user_id, target_date))
        results = cur.fetchall()
        chat_history = []
        for record in results:
            chat_history.append({
                'time_entered': record[0],
                'user_prompt': record[1],
                'system_response': record[2]
            })
        return chat_history
    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        return []
    finally:
        close_db(conn, cur)
# Example usage:
# history = get_chat_history_by_date(1, 2024, 12, 15)
# for chat in history:
#     print(f"User: {chat['user_prompt']}")
#     print(f"System: {chat['system_response']}")
#functions ----------------------------------------------------------------------------------------------