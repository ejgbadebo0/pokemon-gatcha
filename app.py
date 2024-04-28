from forms import RegisterForm, LoginForm
from flask import Flask, render_template, redirect, request, session, jsonify, flash
from flask_debugtoolbar import DebugToolbarExtension
import requests, random, copy, datetime
import os

from models import db, connect_db, Pokemon, User, Move, Capture, PokemonMove

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///pokemon_gatcha')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'SECRETKEY')

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

# Issue1: Pokemon can have duplicates in the Pokedex when summoned
# Issue2: On computer devices, when using Capture, the animation 
#         and result screen show different results. (runs twice)
#         *when done on a mobile device, only runs one time?*
# TestAcc1: FishMan123 pass: trilobite
# TestAcc2: exampleuser1 pass: password1
#------------------------
#Draw Rates 
base_r = 85
pity_r = 0

base_sr = 11
pity_sr = 96

base_ssr = 4
#------------------------
#Images
r_img = 'https://static.wikia.nocookie.net/pokemon/images/8/87/Pok%C3%A9_Ball.png'
sr_img = 'https://static.wikia.nocookie.net/pokemon/images/a/ac/Great_Ball_Artwork.png'
ssr_img = 'https://static.wikia.nocookie.net/pokemon/images/f/f1/UltraBallArt.png'

ex_pkm = 'https://pokeres.bastionbot.org/images/pokemon/1.png'
#------------------------
#Misc


#------------------------
#Main
@app.route('/')
def default():
    """
    Default route.
    """
    if "user_id" in session:
        return redirect('/landing')
    else: 
        return render_template('base.html')

@app.route('/logout')
def logout():
    """
    Sign current user out of the session.
    """
    session.pop("user_id")
    return redirect('/')

@app.route('/landing')
def front_page():
    """
    User's home page. 
    """
    if "user_id" not in session:
        flash("You must be logged in to view this page.")
        return redirect('/')
    else:
        return render_template('landing.html')

@app.route('/capture')
def capture_page():
    """
    Page for capturing pokemon.
    """
    if "user_id" not in session:
        flash("You must be logged in to view this page.")
        return redirect('/')
    else:
        return render_template('capture.html')

@app.route('/details')
def details_page():
    """
    Details page for capturing pokemon.
    """
    if "user_id" not in session:
        flash("You must be logged in to view this page.")
        return redirect('/')
    else:
        pokemon = Pokemon.query.all()
        return render_template('details.html', pokemon=pokemon, repr=repr)
        


@app.route('/one_pull')
def one_pull():
    """
    Performs a 1x capture. 
    """
    
    if "user_id" not in session:
        flash("You must be logged in to view this page.")
        return redirect('/')
    else:
        
        pokemon = [ roll(base_r, base_sr, base_ssr) ] 
        capture = Capture( user_id=session['user_id'], pokemon_id=pokemon[0].id )
        db.session.add(capture)
        db.session.commit()

        session['last_pull'] = 1
        return render_template('/gacha.html', pokemon=pokemon, repr=repr, get_rarity=get_rarity)

@app.route('/multi_pull')
def multi_pull():
    """
    Performs a 10x capture.
    """
    if "user_id" not in session:
        flash("You must be logged in to view this page.")
        return redirect('/')
    else:
        pokemon = []
        captures = []
        pity = True

        for r in range(0, 10):
            if pity == True and r == 9:
                p = roll(pity_r, pity_sr, base_ssr)
                c = Capture( user_id=session['user_id'], pokemon_id=p.id )
            else:
                p = roll(base_r, base_sr, base_ssr)
                c = Capture( user_id=session['user_id'], pokemon_id=p.id )
                if p.rarity == 'SR' or p.rarity == 'SSR':
                    pity = False
            pokemon.append(p)
            captures.append(c)

        for capture in captures:
            db.session.add(capture)
            db.session.commit()
        
        session['last_pull'] = 10
        return render_template('/gacha.html', pokemon=pokemon, repr=repr, get_rarity=get_rarity)

@app.route('/capture_results')
def captures():
    """
    Displays current user's capture results for the previous 1x/10x capture.
    """
    if "user_id" not in session:
        flash("You must be logged in to view this page.")
        return redirect('/')
    else:
    #maybe try saving the pull to the user before and listing the user's last pull
        pokemon = []

        captures = Capture.query \
            .filter_by(user_id=session['user_id']) \
            .order_by(Capture.time_captured.desc()) \
            .limit(session['last_pull']).all() 
        
        for capture in captures:
            p = Pokemon.query.filter_by(id=capture.pokemon_id).first()  
            pokemon.append(p)

        return render_template('/captures.html', pokemon=pokemon, repr=repr)

@app.route('/info')
def account_info():
    """
    Current user's account info page.
    """
    if "user_id" not in session:
        flash("You must be logged in to view this page.")
        return redirect('/')
    else:
        user = User.query.filter_by(id=session['user_id']).first()
        
        pokemon = pokemon = Pokemon.query \
            .join(Capture) \
            .filter((Capture.user_id == session['user_id']) & (Capture.pokemon_id == Pokemon.id)) \
            .distinct() \
            .count()
        total = Pokemon.query.count()
        return render_template('/info.html', user=user, pokemon=pokemon, total=total)

@app.route('/pokedex')
def pokedex():
    """
    Page to display pokemon user has captured.
    """
    if "user_id" not in session:
        flash("You must be logged in to view this page.")
        return redirect('/')
    else:
        page = request.args.get('page', default=1, type=int)
        pokemon = Pokemon.query \
            .join(Capture) \
            .filter((Capture.user_id == session['user_id']) & (Capture.pokemon_id == Pokemon.id)) \
            .distinct() \
            .order_by(Capture.time_captured.desc()) \
            .paginate(page=page)
        return render_template('/pokedex.html', pokemon=pokemon)

@app.route('/pokedex/<int:pid>')
def show_pokemon(pid):
    """
    Pokedex page for a specific pokemon.
    pid: id of the pokemon.
    """
    pokemon = Pokemon.query.get(pid)
    return render_template('pokemon.html', pokemon_id=pid, pokemon=pokemon)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register user.
    """
    
    form = RegisterForm()

    if form.validate_on_submit():
        
        username = form.username.data
        password = form.password.data

        if User.query.filter_by(username=username).first():
            form.username.errors = ["Username already in use."]

        else:
            new_user = User.register(username, password)
            db.session.add(new_user)
            db.session.commit()

            return render_template('/base.html')

    return render_template('/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """
    Log a user into the session.
    """

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        
        if user:
            session['user_id'] = user.id 
            return redirect('/landing')

        else:
            form.password.errors = ["Invalid username/password."]

    return render_template('login.html', form=form)

#------------------------
#API

@app.route('/api/pokemon')
def get_all_pokemon():
    """
    Get all Pokemon in the database.
    """
    pokemon = [p.serialize() for p in Pokemon.query.all()]
    return jsonify(pokemon=pokemon)

@app.route('/api/pokemon/<int:pid>')
def get_pokemon(pid):
    """
    Get a Pokemon.
    """
    pokemon = Pokemon.query.get(pid).serialize()
    return jsonify(pokemon=pokemon)

@app.route('/api/move')
def get_all_moves():
    """
    Get all Pokemon moves.
    """
    moves = [m.serialize() for m in Move.query.all()]
    return jsonify(moves=moves)
    
@app.route('/api/move/<int:mid>')
def get_move(mid):
    """
    Get a Move.
    """
    move = Move.query.get(mid).serialize()
    return jsonify(move=move)

@app.route('/api/pokemon/<int:pid>/moves')
def get_pokemon_moves(pid):
    """
    Get the list of moves a Pokemon owns.
    """
    pokemon = Pokemon.query.get_or_404(pid)
    moves = [m.serialize() for m in Move.query \
            .join(PokemonMove) \
            .filter((PokemonMove.pokemon_id == pid) & (PokemonMove.move_id == Move.id)) \
            .distinct() \
            .order_by(Move.id)]

    return jsonify(pokemon_moves=moves)

@app.route('/api/login', methods=['GET', 'POST'])
def external_login():
    """
    Get user information from an external source.
    """
    username = request.json['username']
    password = request.json['password']
    user = User.authenticate(username, password)

    if user:
        pokemon = [p.serialize() for p in Pokemon.query \
                .join(Capture) \
                .filter((Capture.user_id == user.id) & (Capture.pokemon_id == Pokemon.id)) \
                .distinct() \
                .order_by(Capture.time_captured.desc())]
        
        return jsonify(user=
                {
                'id': user.id,
                'username': user.username,
                'pokemon': pokemon
                })
        
    else:
        return jsonify(message="unauthorized")

#------------------------
#Helper

def roll(r_rate, sr_rate, ssr_rate):
    """
    Draw random Pokemon from the database, based on set draw rate.
    r_rate, sr_rate, ssr_rate: 0 - 100, sum should equal 100.
    """
    rng = random.randint(0, 100)

    if rng < r_rate:
        p = random.choice(Pokemon.query.filter_by(rarity='R').all())
        return p
    if rng >= r_rate and rng < (r_rate + sr_rate):
        p = random.choice(Pokemon.query.filter_by(rarity='SR').all())
        return p
    if rng >= (100 - ssr_rate):
        p = random.choice(Pokemon.query.filter_by(rarity='SSR').all())
        return p

def get_rarity(rarity):
    """
    Return the correct ball image for a given rarity.
    rarity: 'R'/'SR'/'SSR'
    """
    if rarity == 'R':
        return r_img
    if rarity == 'SR':
        return sr_img
    if rarity == 'SSR':
        return ssr_img
    

    