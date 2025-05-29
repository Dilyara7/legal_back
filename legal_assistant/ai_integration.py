import openai
from django.conf import settings

def get_legal_assistance(question):
    openai.api_key = settings.OPENAI_API_KEY
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a legal expert assistant. Provide detailed legal advice."
            }, {
                "role": "user",
                "content": question
            }]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Error: {str(e)}"