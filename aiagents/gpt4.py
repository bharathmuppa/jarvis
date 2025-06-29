import openai
import os

def get_gpt4_response(text, systemMessage="Note: Do not include any explanations or apologies in your responses"):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        return "Error: OPENAI_API_KEY not found. Please set your OpenAI API key."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": systemMessage},
                {"role": "user", "content": text}
            ],
            max_tokens=1000,
            temperature=0.0,
            n=1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error with OpenAI API: {str(e)}"