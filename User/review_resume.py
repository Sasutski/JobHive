import os
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI  

# Define the absolute path to your .env file
dotenv_path = Path("/Users/jonazho/Documents/GitHub/JobHive/ENV's/API.env")

# Load .env file from the specified path
load_dotenv(dotenv_path=dotenv_path)

client = OpenAI(
   api_key = os.getenv("AIKey")
)

chat_completion = client.chat.completions.create(
   messages=[
      {
         "role": "user",
         "content": "Say this is a test",
      }
   ],
   model="gpt-4o"
)


# Print to check if it's loaded

