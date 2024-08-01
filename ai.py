import openai
from openai import OpenAI

# Set your OpenAI API key here
api_key = 'sk-None-I56MR0Xzg35tT0bS4CbVT3BlbkFJxmC3ZLfP0SJxLBgsP8XW'

# Function to get corrected name and level using GPT-3.5
def get_corrected_name_and_level(text):
    prompt = f"The following text was extracted from an image of a Pokémon game: '{text}'. \
    Can you identify the Pokémon name and level from this text? \
    The displayed pokemon will only be from Generation 3 or earlier. \
    Only return the name, followed by text, in this format: POKEMON_NAME LEVEL \
    If you do not see a pokemon name, return NULL 0."
    client = OpenAI(
        # This is the default and can be omitted
        api_key=api_key,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o-mini",
    )

    message = chat_completion.choices[0].message.content
    print(f"Suggestion from AI: {message}")
    return message