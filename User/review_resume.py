import os
from openai import OpenAI  
#run this code in terminal export AIKEY="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"
client = OpenAI(
   api_key = os.getenv("AIKEY")
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
print(chat_completion)
