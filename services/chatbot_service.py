import os
import google.generativeai as genai
from bson import ObjectId
from database import db_instance
import traceback

def get_gemini_response(user_id, user_message):
    """
    Generates a contextual response using the Gemini API, 
    retrieving the API key from the GEMINI_API_KEY environment variable.
    """
    
    # --- Retrieve API key directly from environment variable ---
    api_key = os.getenv('GEMINI_API_KEY')

    # Check if API key is provided
    if not api_key:
        return "The AI chatbot is currently offline. Please ensure your **GEMINI_API_KEY** is set correctly in your environment or `.env` file."
    
    try:
        # Configure the client with the retrieved API key
        genai.configure(api_key=api_key)
        # Use the modern, fast model for chat
        model = genai.GenerativeModel('gemini-2.5-flash')

        # --- Database Context Retrieval (Unchanged) ---
        accounts_collection = db_instance.get_collection('accounts')
        balance_info = "unavailable"
        if accounts_collection is not None:
            # Note: MongoDB requires ObjectId for _id and user_id fields
            # Check if user_id can be converted to ObjectId before querying
            try:
                account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
                if account:
                    balance_info = f"₹{account.get('balance', 0):.2f}"
            except Exception as db_e:
                # Handle cases where user_id might not be a valid ObjectId format
                print(f"ERROR: Invalid user_id format for MongoDB: {db_e}")


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
        # It's good practice to print the detailed traceback to the server console for debugging
        traceback.print_exc() 
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment."
