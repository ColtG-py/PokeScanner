import requests
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
def process_image_and_get_moveset(pokemon_name, level):
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
