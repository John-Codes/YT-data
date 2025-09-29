from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def init_db_connection():
    global client
    global db
    client = MongoClient(uri, server_api=ServerApi('1'), ssl=True)
    db = client['CryptoAILED']

# IMPORTANT: Use EXACT CASE from MongoDB Atlas
uri = "mongodb+srv://CryptoAI:CryptoAI@cryptoailed.enlge.mongodb.net/CryptoAILED?retryWrites=true&w=majority&appName=CryptoAILed"

def create_document(collection_name, document):
    try:
        collection = db[collection_name]
        result = collection.insert_one(document)
        print(f"Created document with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"Error creating document: {e}")
        return None

def read_document(collection_name, query):
    try:
        collection = db[collection_name]
        result = collection.find(query)
        documents = list(result)
        print(f"Found {len(documents)} documents")
        return documents
    except Exception as e:
        print(f"Error reading documents: {e}")
        return []

def update_document(collection_name, query, update):
    try:
        collection = db[collection_name]
        result = collection.update_many(query, {'$set': update})
        print(f"Updated {result.modified_count} documents")
        return result.modified_count
    except Exception as e:
        print(f"Error updating documents: {e}")
        return 0

def delete_document(collection_name, query):
    try:
        collection = db[collection_name]
        result = collection.delete_many(query)
        print(f"Deleted {result.deleted_count} documents")
        return result.deleted_count
    except Exception as e:
        print(f"Error deleting documents: {e}")
        return 0

# Initialize connection with explicit case handling
try:
    init_db_connection()
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Connection failed: {e}")
    exit()

if __name__ == "__main__":

    # Test CRUD operations
    print("\n=== Testing CRUD Operations ===")
    
    # Create
    test_doc = {"name": "TestCaseDocument", "value": 100}
    doc_id = create_document("test_collection", test_doc)
    
    if doc_id:
        # Read
        print("\n[READ TEST]")
        found = read_document("test_collection", {"_id": doc_id})
        if found:
            print(f"Found document: {found[0]}")
        
        # Update
        print("\n[UPDATE TEST]")
        update_count = update_document("test_collection", {"_id": doc_id}, {"value": 999})
        if update_count > 0:
            updated = read_document("test_collection", {"_id": doc_id})
            print(f"Updated value: {updated[0]['value']}")
        
        # Delete
        print("\n[DELETE TEST]")
        delete_count = delete_document("test_collection", {"_id": doc_id})
        if delete_count > 0:
            remaining = read_document("test_collection", {"_id": doc_id})
            print("Documents remaining after deletion:", len(remaining))

    print("\n=== Test Complete ===")
