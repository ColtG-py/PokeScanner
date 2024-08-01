import requests
from image_processing import extract_text_from_image
from ai import get_corrected_name_and_level

# Function to fetch moveset and types
def get_pokemon_info(pokemon_name, level):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)
    if response.status_code != 200:
        return f"Error fetching data for {pokemon_name}."

    data = response.json()
    moveset = {}
    types = [type_info['type']['name'] for type_info in data['types']]
    pokedex_number = data['id']

    for move in data['moves']:
        for version_group in move['version_group_details']:
            if version_group['version_group']['name'] in ['ruby-sapphire', 'emerald', 'firered-leafgreen']:
                if version_group['level_learned_at'] <= level and version_group['level_learned_at'] > 0:
                    move_name = move['move']['name']
                    if move_name not in moveset:
                        move_power = get_move_details(move['move']['url'])
                        moveset[move_name] = move_power

    sorted_moveset = sorted(moveset.items(), key=lambda x: x[0], reverse=True)
    return {
        'pokedex_number': pokedex_number,
        'types': types,
        'moveset': sorted_moveset
    }

# Function to fetch move details
def get_move_details(move_url):
    response = requests.get(move_url)
    if response.status_code == 200:
        move_data = response.json()
        power = move_data['power'] if move_data['power'] else 'N/A'
        return power
    else:
        return 'N/A'

# Main function to process the image and fetch moveset and types
def process_image_and_get_moveset(image):
    text = extract_text_from_image(image)
    if text.startswith("Tesseract is not installed"):
        print(text)
        return text

    print(f"Extracted Text: {text}")

    # Basic parsing to extract Pokémon name and level from the OCR output
    lines = text.split('\n')
    pokemon_name = None
    level = None

    for line in lines:
        if "Lv" in line or "Lv." in line or "Lu" in line:
            line = line.replace(":", "")  # Remove any semicolons
            parts = line.split()
            if len(parts) > 1:
                pokemon_name = parts[0]
                
                # Extract level by finding the part after "Lv" or "Lu"
                for part in parts:
                    if part.startswith("Lv") or part.startswith("Lu"):
                        level_str = part.replace('Lv', '').replace('Lu', '').replace('Lv.', '')
                        if level_str.isdigit():
                            level = int(level_str)

    if not pokemon_name or not level:
        corrected_text = get_corrected_name_and_level(text) # AI Suggestion based on text.
        corrected_parts = corrected_text.split() # split on space.
        if (corrected_parts[0] == "NULL"): #jank
            time.sleep(5)
            return 
        if len(corrected_parts) >= 2:
            pokemon_name = corrected_parts[0]
            level = int(corrected_parts[-1].replace('Lv', '').replace('Lv.', '').replace('Lu', ''))

    if pokemon_name and level:
        pokemon_info = get_pokemon_info(pokemon_name, level)
        if isinstance(pokemon_info, dict):
            return {
                'pokemon_name': pokemon_name,
                'level': level,
                'pokedex_number': pokemon_info['pokedex_number'],
                'types': pokemon_info['types'],
                'moveset': pokemon_info['moveset']
            }
        else:
            return pokemon_info
    else:
        return "Failed to extract Pokémon name or level."
