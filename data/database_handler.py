import streamlit as st
import psycopg2
from datetime import datetime, timedelta
debug =True 
last19477491_query = """
ALTER TABLE user_health_info
ALTER COLUMN weight_kg SET DEFAULT 66.40;

ALTER TABLE user_health_info
ALTER COLUMN height_m SET DEFAULT 1.70;

ALTER TABLE user_health_info
ALTER COLUMN fitness_goal SET DEFAULT 'Get into better shape';

ALTER TABLE user_health_info
ALTER COLUMN activity_level SET DEFAULT 'active';

-- === NULL FIX FOR EXISTING RECORDS === --
UPDATE user_health_info SET weight_kg = 66.40 WHERE weight_kg IS NULL;
UPDATE user_health_info SET height_m = 1.70 WHERE height_m IS NULL;
UPDATE user_health_info SET fitness_goal = 'Get into better shape' WHERE fitness_goal IS NULL;
UPDATE user_health_info SET activity_level = 'active' WHERE activity_level IS NULL;
UPDATE user_health_info SET dietary_pref = 'any' WHERE dietary_pref IS NULL;
UPDATE user_health_info SET time_available = '12:00–12:20' WHERE time_available IS NULL;
SELECT * FROM user_health_info;
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
        # if debug: Print all data
        cur.execute(last19477491_query)
        # Export to CSV
        export_path = r"C:\Users\Ibrahim\Downloads\Internship\Multi-Agentic_Health_Assistant\data\user_health_info.csv"
        cur.execute(f"""
        COPY user_health_info TO '{export_path}' WITH CSV HEADER;
        """)
        conn.commit()

        if debug: print(f"Exported")

    except Exception as e:
        if debug: print("Error during export or view:", e)
    finally:
        cur.close()
        conn.close()
        if debug: print("Database connection closed.")

#functions ----------------------------------------------------------------------------------------------
# Helper: Compute 20-minute availability range
def get_time_window(start_time_str):
    try:
        start = datetime.strptime(start_time_str, "%H:%M")
    except ValueError:
        return "12:00–12:20"  # fallback if input is invalid

    end = start + timedelta(minutes=20)
    return f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')}"
def user_registration(
    name: str,                # required
    Age: float,               # required
    gender: bool = True,             # girl=True, boy=False
    height_m: float = 1.65,
    Weight_kg: float = 60.0,
    fitness_goal: str = "Get into better shape",
    Activity_level: str = "active",
    dietary_pref: str = "any",
    time_available: str = "12:00",  # compute window from this
    mental_health_notes: str = None,
    medical_conditions: str = None):
    # Connect to database
    conn, cur = connect_db()
    # Convert boolean gender to 'Female' or 'Male'
    gender_str = 'Female' if gender else 'Male'
    # Compute time range
    time_range = get_time_window(time_available)
    # Insert query
    insert_query = """
        INSERT INTO user_health_info (
            name, age, gender, height_m, weight_kg,
            fitness_goal, activity_level, dietary_pref,
            time_available, mental_health_notes, medical_conditions
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        name, Age, gender_str, height_m, Weight_kg,
        fitness_goal, Activity_level, dietary_pref,
        time_range, mental_health_notes, medical_conditions
    )
    cur.execute(insert_query, values)
    conn.commit()
    # Close connection
    close_db(conn, cur)
    if debug: print(f"User '{name}' registered successfully!")
def change_name(old_name: str, new_name: str):
    # Connect to database
    conn, cur = connect_db()
    try:
        update_query = """
            UPDATE user_health_info
            SET name = %s
            WHERE name = %s
        """
        cur.execute(update_query, (new_name, old_name))
        conn.commit()
        
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{old_name}'.")
        else:
            if debug: print(f"User name changed from '{old_name}' to '{new_name}'.")
    
    except Exception as e:
        if debug: print("Error during name update:", e)
    close_db(conn, cur)
def change_age(name: str, new_age: float):
    # Connect to database
    conn, cur = connect_db()
    try:
        update_query = """
            UPDATE user_health_info
            SET age = %s
            WHERE name = %s
        """
        cur.execute(update_query, (new_age, name))
        conn.commit()
        
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Age updated to {new_age} for '{name}'.")
    except Exception as e:
        if debug: print("Error updating age:", e)
    close_db(conn, cur)
def change_weight(name: str, new_weight: float):
    # Connect to database
    conn, cur = connect_db()
    try:
        update_query = """
            UPDATE user_health_info
            SET weight_kg = %s
            WHERE name = %s
        """
        cur.execute(update_query, (new_weight, name))
        conn.commit()
        
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Weight updated to {new_weight} kg for '{name}'.")
    except Exception as e:
        if debug: print("Error updating weight:", e)
    close_db(conn, cur)
def change_height(name: str, new_height: float):
    # Connect to database
    conn, cur = connect_db()
    try:
        update_query = """
            UPDATE user_health_info
            SET height_m = %s
            WHERE name = %s
        """
        cur.execute(update_query, (new_height, name))
        conn.commit()
        
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Height updated to {new_height} m for '{name}'.")
    except Exception as e:
        if debug: print("Error updating height:", e)
    close_db(conn, cur)
def change_activity_level(name: str, new_level: str):
    # Connect to database
    conn, cur = connect_db()
    allowed = ['not active', 'lightly active', 'active', 'very active']
    if new_level not in allowed:
        if debug: print(f"Invalid activity level. Must be one of: {allowed}")
        return
    try:
        cur.execute("""
            UPDATE user_health_info
            SET activity_level = %s
            WHERE name = %s
        """, (new_level, name))
        conn.commit()
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Activity level updated for '{name}'.")
    except Exception as e:
        if debug: print("Error updating activity level:", e)
    close_db(conn, cur)
def change_dietary_pref(name: str, new_pref: str):
    # Connect to database
    conn, cur = connect_db()
    allowed = ['vegan', 'carnivore', 'both', 'balanced', 'vegetarian', 'pescatarian', 'any']
    if new_pref not in allowed:
        if debug: print(f"Invalid dietary preference. Must be one of: {allowed}")
        return
    try:
        cur.execute("""
            UPDATE user_health_info
            SET dietary_pref = %s
            WHERE name = %s
        """, (new_pref, name))
        conn.commit()
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Dietary preference updated for '{name}'.")
    except Exception as e:
        if debug: print("Error updating dietary preference:", e)
    close_db(conn, cur)

def change_time_available(name: str, start_time: str):
    # Connect to database
    conn, cur = connect_db()
    time_range = get_time_window(start_time)
    try:
        cur.execute("""
            UPDATE user_health_info
            SET time_available = %s
            WHERE name = %s
        """, (time_range, name))
        conn.commit()
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Time availability updated to '{time_range}' for '{name}'.")
    except Exception as e:
        if debug: print("Error updating time availability:", e)
    close_db(conn, cur)
def append_time_available(name: str, start_time: str):
    # Connect to database
    conn, cur = connect_db()
    time_range = get_time_window(start_time)
    try:
        cur.execute("""
            UPDATE user_health_info
            SET time_available = COALESCE(time_available, '') || ' | ' || %s
            WHERE name = %s
        """, (time_range, name))
        conn.commit()
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Appended time availability for '{name}'.")
    except Exception as e:
        if debug: print("Error appending time availability:", e)
    close_db(conn, cur)

def change_fitness_goal(name: str, new_goal: str):
    # Connect to database
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_health_info
            SET fitness_goal = %s
            WHERE name = %s
        """, (new_goal, name))
        conn.commit()
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Fitness goal updated for '{name}'.")
    except Exception as e:
        if debug: print("Error updating fitness goal:", e)
    close_db(conn, cur)
def append_fitness_goal(name: str, additional_goal: str):
    # Connect to database
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_health_info
            SET fitness_goal = COALESCE(fitness_goal, '') || ' | ' || %s
            WHERE name = %s
        """, (additional_goal, name))
        conn.commit()
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Appended fitness goal for '{name}'.")
    except Exception as e:
        if debug: print("Error appending fitness goal:", e)
    close_db(conn, cur)

def change_mental_health_notes(name: str, notes: str):
    # Connect to database
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_health_info
            SET mental_health_notes = %s
            WHERE name = %s
        """, (notes, name))
        conn.commit()
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Mental health notes updated for '{name}'.")
    except Exception as e:
        if debug: print("Error updating mental health notes:", e)
    close_db(conn, cur)
def append_mental_health_notes(name: str, note: str):
    # Connect to database
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_health_info
            SET mental_health_notes = COALESCE(mental_health_notes, '') || ' | ' || %s
            WHERE name = %s
        """, (note, name))
        conn.commit()
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Appended mental health note for '{name}'.")
    except Exception as e:
        if debug: print("Error appending mental health note:", e)
    close_db(conn, cur)

def change_medical_conditions(name: str, condition: str):
    # Connect to database
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_health_info
            SET medical_conditions = %s
            WHERE name = %s
        """, (condition, name))
        conn.commit()
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Medical conditions updated for '{name}'.")
    except Exception as e:
        if debug: print("Error updating medical conditions:", e)
    close_db(conn, cur)
def append_medical_conditions(name: str, condition: str):
    # Connect to database
    conn, cur = connect_db()
    try:
        cur.execute("""
            UPDATE user_health_info
            SET medical_conditions = COALESCE(medical_conditions, '') || ' | ' || %s
            WHERE name = %s
        """, (condition, name))
        conn.commit()
        if cur.rowcount == 0:
            if debug: print(f"No user found with the name '{name}'.")
        else:
            if debug: print(f"Appended medical condition for '{name}'.")
    except Exception as e:
        if debug: print("Error appending medical condition:", e)
    close_db(conn, cur)
   

#functions ----------------------------------------------------------------------------------------------