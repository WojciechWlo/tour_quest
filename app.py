import os
import json
import requests
from flask import Flask,render_template,redirect, session,jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased
from flask_session import Session

from helpers import login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
bcrypt = Bcrypt(app) 


def read_json(source):
    """
    Reads JSON data from a local file or a URL.
    
    Args:
        source (str): The path to the local JSON file or the URL of the JSON data.
        
    Returns:
        dict: The JSON data parsed into a Python dictionary.
    """
    if os.path.isfile(source):
        # Source is a local file path
        with open(source, 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        # Source is a URL
        response = requests.get(source)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
    
    return data


def get_connection_string():

    db_host = os.environ.get('POSTGRES_HOST')
    db_name = os.environ.get('POSTGRES_DB')
    db_user = os.environ.get('POSTGRES_USER')
    db_password = os.environ.get('POSTGRES_PASSWORD')
    connection_string = f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}'

    return connection_string

# Construct the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = get_connection_string()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)

class Game(db.Model):
    __tablename__ = 'games'
    game_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    pathtofile = db.Column(db.String, unique=False, nullable=False)

class Stage(db.Model):
    __tablename__ = 'stages'
    stage_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    pathtofile = db.Column(db.String, unique=False, nullable=False)

class GameHasStage(db.Model):
    __tablename__ = 'gamehasstage'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, unique=True, nullable=False)
    stage_id = db.Column(db.Integer, unique=False, nullable=False)

class NextStage(db.Model):
    __tablename__ = 'nextstage'
    id = db.Column(db.Integer, primary_key=True)
    stage_id = db.Column(db.Integer, unique=False, nullable=True)
    nextstage_id = db.Column(db.Integer, unique=False, nullable=True)


def getNullToFirstStageOfGame(game_index):
    # Aliases for tables
    ghs = aliased(GameHasStage)

    # Perform the query
    nullToFirstStage = db.session.query(
        NextStage.id,
        NextStage.stage_id,
        NextStage.nextstage_id
    ).join(
        ghs, NextStage.nextstage_id == ghs.stage_id
    ).filter(
        NextStage.stage_id == None,
        ghs.game_id == game_index
    ).all()
    
    if len(nullToFirstStage)>0:
        nullToFirstStage = nullToFirstStage[0]
    else:
        nullToFirstStage = None

    return nullToFirstStage

def getFirstStageOfGame(game_index):
    NullToFirstStage = getNullToFirstStageOfGame(game_index)
    if NullToFirstStage!=None:
        FirstStage = NullToFirstStage.nextstage_id
    else:
        FirstStage = None
    return FirstStage


def get_previous_current_next_stages(current_stage_id):
    prev = aliased(NextStage)
    next = aliased(NextStage)

    prev_curr_next_stages = db.session.query(
        prev.stage_id.label('previous_stage_id'),
        NextStage.stage_id.label('current_stage_id'),
        next.stage_id.label('next_stage_id')
    ).select_from(
        NextStage
    ).outerjoin(
        prev, prev.nextstage_id == NextStage.stage_id
    ).outerjoin(
        next, NextStage.nextstage_id == next.stage_id
    ).filter(
        NextStage.stage_id == current_stage_id
    ).first()

    return [prev_curr_next_stages.previous_stage_id, prev_curr_next_stages.current_stage_id,prev_curr_next_stages.next_stage_id]



def setFirstStageOfGame(game_index):
    FirstStage = getFirstStageOfGame(game_index)

    session["stage"] = [None, None, None]

    session["stage"] = get_previous_current_next_stages(FirstStage)





@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/check_hint',methods=["POST"])
@login_required
def check_hint():
    result = Stage.query.filter_by(stage_id=f'{session["stage"][1]}').all()[0]
    stage = read_json(result.pathtofile)

    hints = stage["hint_images"]

    return jsonify(hints)


@app.route('/')
@login_required
def index():
    session["direction"] = None
    session["game_index"] = None


    result = Game.query.all()

    # Convert the result to a list of dictionaries
    games = [{'name': game.name} for game in result]

    

    return render_template("index.html", login = session["login"], games = games)

@app.route('/game_details', methods=["POST", "GET"])
@login_required
def game_details():

    if request.method =="POST":
        if session["game_index"]:
            game = Game.query.filter_by(game_id=f'{session["game_index"]}').all()[0]
        else:
            game = Game.query.filter_by(name=f'{request.form.get("game_name")}').all()[0]
            game_index = game.game_id
            session["game_index"] = game_index

        game_data = read_json(game.pathtofile)

        setFirstStageOfGame(game.game_id)
            
        return render_template("game_details.html", game_data = game_data)


    if session["game_index"]!=None:
        game = Game.query.filter_by(game_id=f'{session["game_index"]}').all()[0]
        game_data = read_json(game.pathtofile)

        if "stage" in session.keys():
            setFirstStageOfGame(game.game_id)

        return render_template("game_details.html", game_data = game_data)
    
    return redirect('/')


@app.route('/answer',methods=["POST"])
@login_required
def answer():
    user_answer = request.form.get("answer")
    if user_answer == session["answer"]:
        return redirect("/next")
    return redirect("/game")


@app.route('/previous')
@login_required
def previous():
    session["direction"] = -1
    return redirect("/game")

@app.route('/next')
@login_required
def next():
    session["direction"] = 1
    return redirect("/game")


@app.route('/game', methods=["POST", "GET"])
@login_required
def game():
    
    '''
    result = GameHasStage.query.filter_by(game_id=f'{session["game_index"]}').all()
    print(result)
    '''

    '''
    next_stage_null = NextStage.query \
        .outerjoin(GameHasStage, NextStage.Stage_ID == GameHasStage.Stage_ID) \
        .filter(GameHasStage.Game_ID == f'{session["game_index"]}') \
        .filter(NextStage.Stage_ID.is_(None)) \
        .all()

    next_stage_null_ids = [{"id" : ns.id, "stage_id":ns.stage_id ,"next_stage_id": ns.nextstage.id} for ns in next_stage_null]

    print(next_stage_null_ids)
    '''

    #scenario = games_scenarios["scenarios"][session["game_index"]]["scenario"]



    if not session["direction"] in [-1,1]:
        session["direction"] = 0

    if not "stage" in session.keys():# or session["stage"] == None:
        setFirstStageOfGame(game.game_id)
    else:

        if session["direction"] == 1 and session["stage"][2] != None:
            session["stage"] = get_previous_current_next_stages(session["stage"][2])
        elif session["direction"] == -1 and session["stage"][0] != None:
            session["stage"] = get_previous_current_next_stages(session["stage"][0])
        '''
        session["stage"] +=session["direction"]
        if session["stage"] <0:
            session["stage"] =0
        elif session["stage"]>len(scenario)-1:
            session["stage"] = len(scenario)-1
        '''
        session["direction"] = 0 

    #Error when no record in table 
    result = Stage.query.filter_by(stage_id=f'{session["stage"][1]}').all()[0]
    stage = read_json(result.pathtofile)


    #scenario = games_scenarios[session["game_index"]] ["scenario"][session["stage"]]
    #stage = scenario[session["stage"][1]]

    stage_template = stage["template"]

    if stage_template == "game_answer":
        session["answer"] = stage["answer"]

    return render_template(f'{stage_template}.html', stage = stage, stage_index = session["stage"])
    #return render_template(f'game_standard.html', scenario = scenario)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/')


@app.route('/login', methods=["GET", "POST"])
def login():
    
        
    if request.method == "POST":

        if not request.form.get("login"):
            return render_template("login.html", msg= "You have to provide login!")

        result = User.query.filter_by(login=f'{request.form.get("login")}').all()
        if len(result) == 0:
            return render_template("login.html", msg= "User with this login does not exist!")
        
        if not request.form.get("password"):
            return render_template("login.html", msg= "You have to provide password!")
        

        if  not bcrypt.check_password_hash(result[0].password, request.form.get("password")) :
            return render_template("login.html", msg = "Wrong login or password")



        session["login"] = request.form.get("login")
        return redirect("/")
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":


        if not request.form.get("login"):
            return render_template("register.html", msg = "You have to provide login!")

        result = User.query.filter_by(login=f'{request.form.get("login")}').all()
        if len(result) >0:
            return render_template("register.html", msg= "User with such login exists!")
        
        if not request.form.get("password"):
            return render_template("register.html", msg= "You have to provide password!")

        if not request.form.get("confirm_password"):
            return render_template("register.html", msg= "You have to confirm password!")

        if request.form.get("confirm_password") != request.form.get("password"):
            return render_template("register.html", msg= "Passwords are not the same!")

        hashed_password = bcrypt.generate_password_hash(request.form.get("password")).decode('utf-8') 

        new_user = User(login=request.form.get("login"), password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session["login"] = request.form.get("login")
        return redirect("/")
    

    return render_template("register.html")



if __name__ == '__main__':
    #get_secrets()
    app.run(debug=True, host='0.0.0.0', port="5000")