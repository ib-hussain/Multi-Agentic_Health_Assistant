'''
analyse nutrient breakdown and the meal photos to provide an analysis
'''
import streamlit as st
import base64
from pathlib import Path
from together import Together
from typing import Dict, Any
from data.database_postgres import get_fitness_goal_diet_gender_age_time_deadline
debug = st.secrets["DEBUGGING_MODE"]
def get_image_description(image_path: str, prompt: str = str(st.secrets["NULL_STRING"]), user_id: int = 1) -> Dict[str, Any]:
    """
    Takes a JPEG image path and returns an image description using LLaMA 3.2 Vision.
    Args:
        image_path (str): Path to the JPEG image file  
    Returns:
        Dict containing 'status' ('success' or 'error') and 'description' or 'message'
    """
    fitness_goal, diet_pref, gender, age, time_deadline = get_fitness_goal_diet_gender_age_time_deadline(user_id)
    age = str(age)
    gender = str(gender)
    fitness_goal  = str(fitness_goal)
    diet_pref = str(diet_pref)
    time_deadline = str(time_deadline)
    diet_pref = "\nMy diet preferences are: "+diet_pref+"\n"+"my age is: "+age +"\n"+"my fitness goal is: "+fitness_goal+"\n"+"my time deadline is: "+time_deadline+"\n"+"and also\nprovide an analysis of the meal photos and provide the nutrient breakdown and maybe a few nutritional suggestions "
    together_api_key = st.secrets["TOGETHER_API_KEY"]
    prompt = prompt+ diet_pref

    try:
        # Read and encode image
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        # Prepare message for vision model
        message_content = [
            {
                "type": "image_url",
                "image_url": {
                    # Make sure it starts with 'data:' and includes the correct MIME type
                    "url": f"data:image/jpeg;base64,{base64_image}"
                    # Use 'image/png' if your image is a PNG.
                }
            },
            {
                "type": "text",
                "text": f"{prompt}"
            }
        ]
        
        # Call Together AI's LLaMA 3.2 Vision model
        client = Together(api_key=together_api_key)
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            messages=[{"role": "user", "content": message_content}],
            max_tokens=int(st.secrets["LARGE_TOKENS"]),
            temperature=float(st.secrets["temperature__T"])
        )
        
        description = response.choices[0].message.content.strip()
        return {"status": "success", "description": description}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Example usage:
result = get_image_description("temp/download.jpeg", user_id=1)
if result["status"] == "success":
    print(result["description"])
else:
    if debug: print(f"Error: {result['message']}") 