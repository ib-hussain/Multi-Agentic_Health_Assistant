import streamlit as st
import base64
import mimetypes
from pathlib import Path
from together import Together
from typing import Dict, Any
from data.database_postgres import get_fitness_goal_diet_gender_age_time_deadline

debug = st.secrets["DEBUGGING_MODE"]

def get_image_description(image_path: str="temp/download.jpeg", prompt: str = str(st.secrets["NULL_STRING"]), user_id: int = 1) -> Dict[str, Any]:
    """
    Takes an image path (PNG, JPG, JPEG, ICO) and returns an image description using LLaMA 3.2 Vision.
    
    Args:
        image_path (str): Path to the image file (png, jpg, jpeg, ico)
        prompt (str): Additional prompt for the AI
        user_id (int): User ID for fetching personal data
        
    Returns:
        Dict containing 'status' ('success' or 'error') and 'description' or 'message'
    """
    try:
        # Get user's fitness data
        fitness_goal, diet_pref, gender, age, time_deadline = get_fitness_goal_diet_gender_age_time_deadline(user_id)
        diet_history = ""
        #put history column in database and then get it over here from the database 
        age = str(age)
        gender = str(gender)
        fitness_goal = str(fitness_goal)
        diet_pref = str(diet_pref)
        time_deadline = str(time_deadline)
        # Build personalized prompt
        personalized_info = (
            # issues: 
            # the prompt might need to be changed and fields might need to be added or subtracted 
            f"User Information:\n"
            f"Diet preferences: {diet_pref}\n"
            f"Age: {age}\n"
            f"Diet History: {diet_history}\n"
            f"Fitness goal: {fitness_goal}\n"
            f"Time deadline: {time_deadline}\n"
            f"You must also provide an analysis of the meal photo and provide the nutrient breakdown and maybe a few nutritional suggestions"
        )
        prompt = f"User Prompt:\n"+prompt + personalized_info
        
        # Read and encode image
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        # Determine MIME type based on file extension
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            # Fallback for common extensions
            extension = Path(image_path).suffix.lower()
            if extension in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif extension == '.png':
                mime_type = 'image/png'
            elif extension == '.ico':
                mime_type = 'image/x-icon'
            else:
                mime_type = 'image/jpeg'  # Default fallback
        # Prepare message for vision model with correct MIME type
        message_content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}"
                }
            },
            {
                "type": "text",
                "text": prompt
            }
        ]
        # Call Together AI's LLaMA 3.2 Vision model
        together_api_key = st.secrets["TOGETHER_API_KEY"]
        client = Together(api_key=together_api_key)
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            messages=[{"role": "user", "content": message_content}],
            max_tokens=int(st.secrets["LARGE_TOKENS"]),
            temperature=float(st.secrets["temperature__T"])
        )
        description = response.choices[0].message.content.strip()
        return {"status":"success", "description": description}
    except Exception as e:
        return {"status":"error", "message": str(e)}

# Example usage:
# result = get_image_description("temp/download.jpeg", user_id=1, prompt = "") 