import openai
from openai import OpenAI
import os

# Set your OpenAI API key here
api_key = os.environ['OPENAI_API_KEY']

# Function to get corrected name and level using GPT-3.5
def get_corrected_name_and_level(text):
    prompt = f"The following text was extracted from an image of a Pokémon game: '{text}'. \
    Can you identify the Pokémon name and level from this text? \
    The displayed pokemon will only be from Generation 3 or earlier. \
    The name will be slightly incorrect. You'll need to make a change. \
    Only return the name, followed by text, in this format: POKEMON_NAME LEVEL \
    It is not possible to have a level be 0, so return nothing less than 1 and nothing greater than 100. \
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