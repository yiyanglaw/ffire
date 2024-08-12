
import json
import os

# Define file paths
json_file_path = 'flask-bae57-firebase-adminsdk-8bvez-858615351e.json'
env_file_path = '.env'

# Read the Firebase credentials JSON file
with open(json_file_path, 'r') as json_file:
    credentials = json.load(json_file)

# Convert the credentials dictionary to a JSON string
credentials_json_string = json.dumps(credentials)

# Prepare the content for the .env file
env_content = f'FIREBASE_CREDENTIALS={credentials_json_string}'

# Write the content to the .env file
with open(env_file_path, 'w') as env_file:
    env_file.write(env_content)

print(f'.env file has been created with FIREBASE_CREDENTIALS.')
