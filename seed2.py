from app import db, requests
from models import User, Pokemon, assign_rarity, Move, format_move_name, PokemonMove

base_url = "https://pokeapi.co/api/v2/pokemon"
move_url = "https://pokeapi.co/api/v2/move"

r2 = requests.get(move_url)
m = r2.json()

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
        print(f"Owners: {len(mov['learned_by_pokemon'])}")

        for i in mov['learned_by_pokemon']:
            try:
                pkm_id = i['url'].replace(base_url,'').replace('/','')
                pokemon = Pokemon.query.get(pkm_id)
                print(pkm_id)

                if pokemon: 
                    new_pokemon_move = PokemonMove(pokemon_id=int(pkm_id), move_id=mov['id'])
                    db.session.add(new_pokemon_move)
            except: 
                print('CANT ADD')
                break  

    except: 
        print('INVALID MOVE')
        break


db.session.commit()