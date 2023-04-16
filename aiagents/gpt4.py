import openai
import os

def get_gpt4_response(text):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a PolyMathGPT goes by name Tony Stark"},
            {"role":"user","content": text}
        ],
        max_tokens=200,
        
        n=1
    )
    return response.choices[0].message.content