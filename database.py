import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

class Database:
    """Manages the connection to the MongoDB database and ensures collections exist."""
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Connects to the MongoDB Atlas cluster and initializes collections."""
        uri = os.environ.get("MONGO_URI")
        if not uri:
            print("WARNING: MONGO_URI environment variable is not set. Falling back to local MongoDB.")
            uri = "mongodb://localhost:27017/"

        try:
            self.client = MongoClient(uri, server_api=ServerApi('1'))
            # Use a specific database name. MongoDB creates it on first use.
            self.db = self.client['smart_ebanking']
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            
            # Explicitly create collections if they don't exist.
            self._initialize_collections()

        except Exception as e:
            print(f"ERROR: Could not connect to MongoDB. Details: {e}")
            self.client = None
            self.db = None

    def _initialize_collections(self):
        """Checks for and creates required collections if they are missing."""
        if self.db is None:
            return

        required_collections = ['users', 'accounts', 'transactions', 'billers']
        existing_collections = self.db.list_collection_names()

        for collection_name in required_collections:
            if collection_name not in existing_collections:
                try:
                    self.db.create_collection(collection_name)
                    print(f"Created collection: '{collection_name}'")
                except Exception as e:
                    print(f"Error creating collection '{collection_name}': {e}")

    def get_collection(self, collection_name):
        """Safely retrieves a collection from the database."""
        if self.db is not None:
            return self.db[collection_name]
        return None

# Create a single, globally accessible instance of the database connection.
db_instance = Database()
