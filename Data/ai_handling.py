from google import genai
import json

def ai(Prompt,summary):
    try:
     summary=str(summary)
     summary=json.dumps(summary)
     client = genai.Client(api_key="AQ.Ab8RN6I3lzSTKqtkIChKNe0cOpUQ0Q6BubIZFXTGvxUTgaQswA")
     response = client.models.generate_content(model="gemini-2.5-flash", contents=f'''Act as business consultant and 
                                               I want you to answer the questions based on only the following information do not make changes to original data or invent anything : {summary}
                                                Question: {Prompt}
    Write atleast 200 to 300 words''',config={"max_output_tokens": 500})                
     return response.usage_metadata.prompt_token_count
    except Exception as e:
        return f"An error occurred: {str(e)}"

