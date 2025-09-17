import os
import google.generativeai as genai
from bson import ObjectId
from database import db_instance

def get_gemini_response(user_id, user_message, api_key):
    """Generates a contextual response using the Gemini API."""
    if not api_key:
        return "The AI chatbot is currently offline. Please try again later."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        accounts_collection = db_instance.get_collection('accounts')
        balance_info = "unavailable"
        if accounts_collection:
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
        print(f"Error calling Gemini API: {e}")
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment."

