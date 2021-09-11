"""Populate the database."""

from app import db, requests
from models import User, Pokemon, assign_rarity

base_url = "https://pokeapi.co/api/v2/pokemon"

db.drop_all()
db.create_all()

r = requests.get(base_url)
p = r.json()

for p in range(1, p['count']):
    try:
        r = requests.get(f"{base_url}/{p}/")
        pkm = r.json()
        p_name = pkm['name']
        p_rarity = assign_rarity(pkm['base_experience'])

        #p_image = f'https://pokeres.bastionbot.org/images/pokemon/{p}.png'   (not functional at the moment)
        p_image = f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{p}.png' #temp
        
        if len(pkm['types']) == 2:
            p_type = pkm['types'][0]['type']['name']
            p_subtype = pkm['types'][1]['type']['name']

            new_pokemon = Pokemon(name=p_name.capitalize(),
                                  type=p_type.capitalize(),
                                  subtype=p_subtype.capitalize(),
                                  rarity=p_rarity,
                                  image=p_image)
        else:
            p_type = pkm['types'][0]['type']['name']  
            new_pokemon = Pokemon(name=p_name.capitalize(),
                                  type=p_type.capitalize(),
                                  rarity=p_rarity,
                                  image=p_image)       
        db.session.add(new_pokemon)
        print(new_pokemon)
    except:
        print('INVALID')
        break


db.session.commit()
