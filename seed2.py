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
        print(f"GET SUCCEEDED: {mov['id']}")
        m_name = format_move_name(mov['name'])
        print(m_name)
        m_power = int(mov['power'])
        print(m_power)
        m_pp = int(mov['pp'])
        print(m_pp)
        m_accuracy = int(mov['accuracy'])
        print(m_accuracy)
        new_move = Move(name=m_name,
                        power=m_power,
                        pp=m_pp,
                        accuracy=m_accuracy)
        if new_move:
            db.session.add(new_move)
            print(new_move)
            print(f"Owners: {len(mov['learned_by_pokemon'])}")

            for i in mov['learned_by_pokemon']:
                try:
                    pkm_id = i['url'].replace(base_url,'').replace('/','')
                    print(f"PID:<{pkm_id}>")
                    q_pokemon = Pokemon.query.get(int(pkm_id))
                    print(f"GOT:<{q_pokemon.id}>")
                    if q_pokemon: 
                        new_pokemon_move = PokemonMove(pokemon_id=q_pokemon.id, move_id=new_move.id)
                        db.session.add(new_pokemon_move)
                except: 
                    print('CANT ADD')  

    except: 
        print('INVALID MOVE')


db.session.commit()