"""Populate the database."""

from app import db, requests
from models import User, Pokemon, assign_rarity, Move, format_move_name, PokemonMove

base_url = "https://pokeapi.co/api/v2/pokemon"
move_url = "https://pokeapi.co/api/v2/move"

db.drop_all()
db.create_all()

r = requests.get(base_url)
r2 = requests.get(move_url)
p = r.json()
m = r2.json()

#pokemon
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

#move
for m in range(1, m['count']):
    try:
        r = requests.get(f"{move_url}/{m}/")
        mov = r.json()

        m_name = format_move_name(mov['name'])
        m_power = int(mov['power'])
        m_pp = int(mov['pp'])
        m_accuracy = int(mov['accuracy'])

        new_move = Move(name=m_name,
                        power=m_power,
                        pp=m_pp,
                        accuracy=m_accuracy)
        db.session.add(new_move)
        print(new_move)

        for i in mov['learned_by_pokemon']:
            try:
                print(i['url'])
                pkm_id = i['url'].replace(base_url,'').replace('/','')
            
                new_pokemon_move = PokemonMove(pokemon_id=int(pkm_id), move_id=m)
                db.session.add(new_pokemon_move)
            except: 
                print('CANT ADD')
                break  

    except: 
        print('INVALID MOVE')
        break



db.session.commit()
