import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini API client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini 1.5 Pro for structured, complex workout logic
pro_model = genai.GenerativeModel("gemini-1.5-pro")
# Gemini 1.5 Flash for fast, low-latency tips
flash_model = genai.GenerativeModel("gemini-1.5-flash")

def generate_workout_plan(age: int, weight: float, goal: str, intensity: str) -> str:
    prompt = f"""
    Act as an expert fitness trainer. Generate a structured 7-day workout plan for a {age}-year-old weighing {weight}kg.
    Their primary goal is '{goal}' and they prefer a '{intensity}' workout intensity.
    Include warm-ups, exercises, sets, repetitions, cooldowns, and rest days. 
    Format the output cleanly in Markdown.
    """
    response = pro_model.generate_content(prompt)
    return response.text

def generate_nutrition_tip(goal: str) -> str:
    prompt = f"Provide one highly effective and concise nutrition or recovery tip for someone whose fitness goal is: {goal}."
    response = flash_model.generate_content(prompt)
    return response.text

def refine_workout_plan(existing_plan: str, feedback: str) -> str:
    prompt = f"""
    Here is an existing 7-day workout plan:
    {existing_plan}
    
    The user has provided the following feedback to update the plan:
    "{feedback}"
    
    Regenerate the complete 7-day workout plan incorporating this feedback while maintaining a clean Markdown structure.
    """
    response = pro_model.generate_content(prompt)
    return response.text