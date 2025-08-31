import base64
import os
import mimetypes
from pathlib import Path
from together import Together
from typing import Dict, Any
from data.database_postgres import (
    get_fitness_goal_diet_gender_age_time_deadline, daily_height_weight_diet_hist, store_chat_postgres
    )

debug = True

def get_image_description(image_path: str="temp/download.jpeg", prompt: str = " ", user_id: int = 1) -> Dict[str, Any]:
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
        fitness_goal, diet_pref, gender, name, age, medical_cond, time_deadline, conn, cur   = get_fitness_goal_diet_gender_age_time_deadline(user_id)
        # if debug: print("no Problem detected here 0")
        height, weight, diet_history = daily_height_weight_diet_hist(user_id,conn, cur)
        # if debug: print("no Problem detected here 1")
        age = str(age)
        gender = str(gender)
        fitness_goal = str(fitness_goal)
        diet_pref = str(diet_pref)
        time_deadline = str(time_deadline)
        personalized_info = (
            f"User Information:\n"
            f"Name: {name}\n"
            f"Diet preferences: {diet_pref}\n"
            f"Age: {age}\n"
            f"User Weight: {height}\n"#change this to daily stats table
            f"User Height: {weight}\n"#change this to daily stats table
            f"Diet History: {diet_history}\n"
            f"Previous Medical History/Medical Conditions: {medical_cond}\n"
            f"The Fitness goal of the user: {fitness_goal}\n"
            f"Time deadline for completing goal: {time_deadline}\n"
            f"First check if the image is of a meal or something edible, if not then tell the user what the picture is and thats it, nothing more should be said by you.\n"
            f"You are a AI Diet agent for nutrition analysis and meal planning that must do the following tasks, no matter what:\n"
            f"- Meal planning and nutritional suggestions\n"
            f"- Vision-based analysis of food photos\n"
            f"- Nutrient breakdown and diet goal comparison\n"
            f"- Dietary preference accommodation\n"
            f"- Calorie and macro tracking\n"
            f"(Your given output should be properly formatted markdown, addressed to the user, make no mistakes!)"
        )
        prompt = f"User Prompt:\n"+prompt + personalized_info
        if debug: print(" no Problem detected here 2")
        
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
        together_api_key = str(os.getenv("TOGETHER_API_KEY"))
        client = Together(api_key=together_api_key)
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            messages=[{"role": "user", "content": message_content}],
            max_tokens=int(os.getenv("LARGE_TOKENS")),
            temperature=float(os.getenv("temperature__T"))
        )
        description = response.choices[0].message.content.strip()
        if debug: print(description)
        store_chat_postgres(user_id=user_id, user_prompt=prompt, response=description, has_image=True)
        return {"status":"success", "description": description}
    except Exception as e:
        return {"status":"error", "message": str(e)}
# Example usage:
# result = get_image_description("temp/download.jpeg", user_id=1, prompt = "") 
def get_diet_info(prompt:str, user_id:int=1) -> Dict[str, Any]:
    """
    Takes a text prompt and returns diet-related information using openai/gpt-oss-20b
    Args:
        prompt (str): User's text prompt
        user_id (int): User ID for fetching personal data
        
    Returns:
        Dict containing 'status' ('success' or 'error') and 'response' or 'message'
    """