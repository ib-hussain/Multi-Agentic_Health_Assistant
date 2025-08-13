def respond(stringi):
    # print(f"**{stringi}**\n hey  so the thing is that as of yet i have just integrated the picture analysis chatbot yet, but i am working on integrating the other chatbots as well dont worry ")
    a= f"**{stringi}**\n hey  so the thing is that as of yet i have just integrated the picture analysis chatbot yet, but i am working on integrating the other chatbots as well dont worry "
    return a
import os
import logging
from typing import Dict, Any, Optional
from langchain_together import Together
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel, Field 

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

debug = True

class AgentClassificationParser(BaseOutputParser):
    """Custom parser for agent classification output"""
    
    def parse(self, text: str) -> str:
        """Parse the LLM output and extract the agent type"""
        text = text.strip().lower()
        
        # Look for explicit agent mentions
        if 'diet' in text or 'nutrition' in text or 'food' in text or 'meal' in text:
            return 'diet'
        elif 'exercise' in text or 'workout' in text or 'fitness' in text:
            return 'exercise'
        elif 'mental' in text or 'emotional' in text or 'mood' in text:
            return 'mental'
        
        # Fallback: look for the first occurrence of any agent type
        for agent in ['diet', 'exercise', 'mental']:
            if agent in text:
                return agent
                
        # Default fallback
        logger.warning(f"Could not classify text: {text}. Defaulting to 'mental'")
        return 'mental'
def create_classification_chain():
    """Create the LangChain classification chain"""
    
    # Initialize Together AI LLM with Gemma Instruct 2B
    llm = Together(
        model="google/gemma-2-2b-it",
        temperature=0.3,
        max_tokens=150,
        api_key=str(os.getenv("TOGETHER_API_KEY"))
    )
    
    # Create the classification prompt
    classification_prompt = PromptTemplate(
        input_variables=["user_prompt"],
        template="""You are an intelligent agent classifier that determines which specialized agent should handle a user's request.

Available Agents and Their Capabilities:

DIET AGENT:
- Meal planning and nutritional suggestions
- Nutrient breakdown and diet goal comparison
- Dietary preference accommodation
- Calorie and macro tracking
- Food identification and nutritional analysis

EXERCISE AGENT:
- Personalised workout routine generation
- Workout completion and calorie tracking
- Weekly difficulty and goal adjustments
- Performance data logging
- Progress monitoring and analytics
- Fitness planning and exercise recommendations

MENTAL HEALTH AGENT:
- Daily check-ins and emotional support
- Guided journaling and motivational prompts
- Sentiment analysis and emotion classification
- Secure conversation memory with flagging system
- Long-term interaction tracking
- Emotional wellness and mental health support

User Prompt: "{user_prompt}"

Analyze the user prompt carefully and determine which agent is most appropriate to handle this request.

Classification Rules:
1. If the prompt mentions food, meals, nutrition, calories, diet, eating, recipes, ingredients, or asks about food photos → diet
2. If the prompt mentions workouts, exercise, fitness, training, physical activity, muscle building, weight lifting, cardio → exercise  
3. If the prompt mentions emotions, feelings, mental health, stress, anxiety, mood, motivation, journaling, emotional support → mental

Respond with ONLY ONE WORD: diet, exercise, or mental

Classification:"""
    )
    
    # Create chain the traditional way
    return classification_prompt, llm
def fallback_classifier(user_prompt: str) -> str:
    """
    Simple keyword-based fallback classifier if LLM fails
    """
    prompt_lower = user_prompt.lower()
    
    # Diet keywords
    diet_keywords = [
        'food', 'eat', 'meal', 'nutrition', 'diet', 'calorie', 'recipe', 
        'ingredient', 'cook', 'hungry', 'breakfast', 'lunch', 'dinner',
        'snack', 'protein', 'carb', 'fat', 'vitamin', 'nutrient'
    ]
    
    # Exercise keywords
    exercise_keywords = [
        'workout', 'exercise', 'fitness', 'gym', 'train', 'run', 'lift',
        'cardio', 'strength', 'muscle', 'weight', 'rep', 'set', 'sport',
        'physical', 'activity', 'movement', 'stretch', 'yoga'
    ]
    
    # Mental health keywords
    mental_keywords = [
        'feel', 'emotion', 'mood', 'stress', 'anxiety', 'happy', 'sad',
        'depressed', 'motivation', 'mental', 'mind', 'think', 'worry',
        'support', 'help', 'journal', 'wellness', 'therapy'
    ]
    # Count keyword matches
    diet_score = sum(1 for keyword in diet_keywords if keyword in prompt_lower)
    exercise_score = sum(1 for keyword in exercise_keywords if keyword in prompt_lower)
    mental_score = sum(1 for keyword in mental_keywords if keyword in prompt_lower)
    # Return the category with highest score
    scores = {'diet': diet_score, 'exercise': exercise_score, 'mental': mental_score}
    return max(scores, key=scores.get)
def classify_user_prompt(user_prompt: str, user_id: int = 1) -> Dict[str, Any]:
    """
    Runs the classification chain and gets the agent's name
    
    Args:
        user_prompt (str): The user's input prompt
        user_id (int): User ID for logging purposes
        
    Returns:
        Dict containing 'status', 'agent_type', and optional 'message'
    """
    try:
        if debug:
            logger.info(f"Classifying prompt for user {user_id}: {user_prompt[:100]}...")
        
        # Handle empty prompts
        if not user_prompt or not user_prompt.strip():
            return {
                "status": "success",
                "agent_type": 'mental',
                "user_id": user_id,
                "original_prompt": user_prompt
            }
        
        # Create classification chain
        prompt_template, llm = create_classification_chain()
        
        # Format the prompt and call the LLM directly
        formatted_prompt = prompt_template.format(user_prompt=user_prompt.strip())
        llm_response = llm.invoke(formatted_prompt)
        
        # Parse the response
        parser = AgentClassificationParser()
        agent_type = parser.parse(llm_response)
        
        # Validate output
        valid_agents = ['diet', 'exercise', 'mental']
        if agent_type not in valid_agents:
            if debug:
                logger.warning(f"Invalid agent type returned: {agent_type}. Using fallback classifier.")
            agent_type = fallback_classifier(user_prompt)
        
        if debug:
            logger.info(f"Classified prompt as: {agent_type}")
        
        return {
            "status": "success",
            "agent_type": agent_type,
            "user_id": user_id,
            "original_prompt": user_prompt
        }
        
    except Exception as e:
        if debug:
            logger.error(f"Error in classify_user_prompt: {str(e)}")
        
        # Use fallback classifier in case of error
        fallback_agent = fallback_classifier(user_prompt)
        
        return {
            "status": "success",
            "message": f"Used fallback classifier due to error: {str(e)}",
            "agent_type": fallback_agent,
            "user_id": user_id,
            "original_prompt": user_prompt
        }
# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_prompts = [
        "What should I eat for breakfast?",
        "I need a workout routine for building muscle",
        "I'm feeling really stressed lately and need some support",
        "How many calories are in this sandwich?",
        "Can you help me with my squat form?",
        "I'm having trouble sleeping and feel anxious"
    ]
    print("Testing Agent Classifier (Modern LangChain):")
    print("=" * 50)
    for prompt in test_prompts:
        result = classify_user_prompt(prompt)
        print(f"Prompt: {prompt}")
        print(f"Classification: {result.get('agent_type', 'unknown')}")
        print(f"Status: {result.get('status', 'unknown')}")
        if 'message' in result:
            print(f"Message: {result['message']}")
        print("-" * 30)

