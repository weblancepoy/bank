import os
import google.generativeai as genai
from bson import ObjectId
from database import db_instance
import traceback

def get_gemini_response(user_id, user_message, api_key):
    """Generates a contextual response using the Gemini API."""
    if not api_key or api_key == '<your_gemini_api_key>':
        return "The AI chatbot is currently offline. Please ensure your Gemini API key is set correctly."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.0-pro')

        accounts_collection = db_instance.get_collection('accounts')
        balance_info = "unavailable"
        if accounts_collection is not None:
            account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
            if account:
                balance_info = f"${account.get('balance', 0):.2f}"

        prompt = f"""
        You are "SmartBot", a friendly and professional AI banking assistant for SmartBank.
        Your user is currently logged into their account.
        
        Current User Context:
        - Account Balance: {balance_info}

        Your primary goal is to be helpful and secure. Never ask for passwords or personal identification numbers (PINs).
        Always guide users to the correct section of the app to perform actions (e.g., "You can do this in the 'Transactions' section.").
        Keep your answers concise and easy to understand.

        User's question: "{user_message}"
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print("ERROR: An error occurred while communicating with the Gemini API.")
        traceback.print_exc() # This will print the full error traceback to the console.
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment."
