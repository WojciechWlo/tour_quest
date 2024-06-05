import os
import json
from flask import Flask,render_template,redirect, session,jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 

from flask_session import Session

from helpers import login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
bcrypt = Bcrypt(app) 

games = {
    "games" : [
        {
            "title" : "game 1",
            "description" : "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean eget ante at felis tempus viverra. Mauris accumsan est diam, vitae eleifend urna auctor eu. Praesent in lacus erat. Vivamus ac ante sit amet nulla laoreet elementum ac vel ex. Aliquam fringilla dolor vitae massa maximus, in congue lectus consectetur. Nulla facilisi. Cras dui ipsum, dapibus sed mollis a, vestibulum in nisl. Ut feugiat mollis leo, id laoreet risus aliquam et. Integer ut fringilla urna, sit amet aliquam augue. Curabitur et odio at elit facilisis aliquam vel in lorem. Nulla facilisi. Pellentesque rutrum sapien rhoncus nunc auctor ullamcorper. Mauris non efficitur eros. Vestibulum non laoreet nunc. Suspendisse molestie sapien in nulla porttitor, non gravida eros ultricies. Sed eleifend sodales odio."
        },
        {
            "title" : "game 2",
            "description" : "Donec iaculis porta risus quis cursus. Nulla non odio commodo, tempus neque ac, facilisis mi. Suspendisse in lacus justo. Sed ante nulla, bibendum a suscipit in, feugiat a enim. Sed ut maximus nibh. Sed neque nunc, cursus sed enim a, sollicitudin dapibus purus. Integer gravida mauris sem, ut pharetra neque tincidunt in. In sed dui non nibh porta venenatis."
        },
        {
            "title" : "game 3",
            "description" : "Donec iaculis porta risus quis cursus. Nulla non odio commodo, tempus neque ac, facilisis mi. Suspendisse in lacus justo. Sed ante nulla, bibendum a suscipit in, feugiat a enim. Sed ut maximus nibh. Sed neque nunc, cursus sed enim a, sollicitudin dapibus purus. Integer gravida mauris sem, ut pharetra neque tincidunt in. In sed dui non nibh porta venenatis. Donec iaculis porta risus quis cursus. Nulla non odio commodo, tempus neque ac, facilisis mi. Suspendisse in lacus justo. Sed ante nulla, bibendum a suscipit in, feugiat a enim. Sed ut maximus nibh. Sed neque nunc, cursus sed enim a, sollicitudin dapibus purus. Integer gravida mauris sem, ut pharetra neque tincidunt in. In sed dui non nibh porta venenatis. Donec iaculis porta risus quis cursus. Nulla non odio commodo, tempus neque ac, facilisis mi. Suspendisse in lacus justo. Sed ante nulla, bibendum a suscipit in, feugiat a enim. Sed ut maximus nibh. Sed neque nunc, cursus sed enim a, sollicitudin dapibus purus. Integer gravida mauris sem, ut pharetra neque tincidunt in. In sed dui non nibh porta venenatis."
        }
    ]

}

games_scenarios = {
    "scenarios" : [
        {
            "scenario" : [
                {
                    "template" : "game_standard",
                    "header" : "stage 0",
                    "label" : "label 0",
                    "description" : "Donec accumsan neque ac urna viverra, eget auctor quam sodales. Praesent cursus ligula ante, a imperdiet erat ultrices ac. Nulla sollicitudin arcu non magna dapibus, et congue velit aliquet. Sed gravida eros at turpis molestie auctor. Duis accumsan dui sed justo molestie, non lacinia justo sollicitudin. Sed in aliquam velit. Etiam efficitur congue commodo. In faucibus, lacus et tempus mattis, ipsum magna rhoncus magna, egestas egestas eros ligula id urna. "
                },
                {
                    "template" : "game_standard",
                    "header" : "stage 1",
                    "label" : "label 1",
                    "description" : "Praesent mauris nisl, luctus nec semper eget, pretium sit amet ex. Morbi mollis congue varius. Nunc id nibh bibendum magna tincidunt malesuada. Suspendisse vel dolor eleifend, pharetra sem at, venenatis orci. Maecenas convallis nec tellus eu ullamcorper. Sed nec dolor metus. Aliquam faucibus lectus ac metus euismod, euismod ultricies leo fermentum. Vestibulum dignissim nisi in sagittis vehicula. Sed tempor dui eros, vel dapibus purus vehicula quis. Sed varius nisl magna, eget tristique enim bibendum at. Morbi iaculis orci vel sagittis volutpat. Nunc in pulvinar nisl. Mauris tempor enim libero, eget lobortis dui tincidunt et. Cras vel nisi bibendum, aliquam diam quis, mollis quam. Donec mollis mauris in rutrum gravida."
               
                },                {
                    "template" : "game_map",
                    "header" : "Road",
                    "label" : "Where to go",
                    "description" : "Praesent mauris nisl, luctus nec semper eget, pretium sit amet ex. Morbi mollis congue varius. Nunc id nibh bibendum magna tincidunt malesuada. Suspendisse vel dolor eleifend, pharetra sem at, venenatis orci. Maecenas convallis nec tellus eu ullamcorper. Sed nec dolor metus. Aliquam faucibus lectus ac metus euismod, euismod ultricies leo fermentum. Vestibulum dignissim nisi in sagittis vehicula. Sed tempor dui eros, vel dapibus purus vehicula quis. Sed varius nisl magna, eget tristique enim bibendum at. Morbi iaculis orci vel sagittis volutpat. Nunc in pulvinar nisl. Mauris tempor enim libero, eget lobortis dui tincidunt et. Cras vel nisi bibendum, aliquam diam quis, mollis quam. Donec mollis mauris in rutrum gravida.",
                    "destination" : "https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d296.70717516412276!2d18.74922!3d53.492451!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4702cfed778e5619%3A0x66fbf04ca092a289!2s%C5%81aweczka%20Miko%C5%82aja%20Kopernika!5e0!3m2!1spl!2spl!4v1717509846757!5m2!1spl!2spl"
                },
                {
                    "template" : "game_answer",
                    "header" : "Question 1",
                    "description" : "Answer is one word and number. The word is the last word in the book's title. The number is quantity of visible coins from the moneybag.",
                    "answer" : "Monetae 7",
                    "image" : "static\\images\\answer1_image.jpg",
                    "hint_images" : [
                        {
                            "text":"The last of these three words.",
                            "image":"static\\images\\hint1_1_image.jpg"
                        }, 
                        {
                            "text":"Just count visible coins.",
                            "image":"static\\images\\hint1_2_image.jpg"
                        }
                        ]
                },
                {
                    "template" : "game_standard",
                    "header" : "Congratulations!",
                    "description" : "You have finished this game!"
                }
            ]
        },
        {

        }
    ]
}

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
    id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(db.String, unique=True, nullable=False)
    user_password = db.Column(db.String, unique=False, nullable=False)


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
    hints = games_scenarios["scenarios"][session["game_index"]]["scenario"][session["stage"]]["hint_images"]

    return jsonify(hints)


@app.route('/')
@login_required
def index():
    session["direction"] = None
    session["game_index"] = None
    return render_template("index.html", login = session["login"], games = games)

@app.route('/game_details', methods=["POST", "GET"])
@login_required
def game_details():
    '''
    game_data = request.form.get("game_list_element_details").replace( "'","\"")
    json_game_data = json.loads(game_data)
    return render_template("game_details.html", game_data = json_game_data)
    '''

    #print("afasdafaf: ",session["game_index"])
    if "stage" in session.keys():
        session["stage"] = 0

    if request.method =="POST":
        if session["game_index"]:
            return render_template("game_details.html", game_data = games["games"][session["game_index"]])
        else:
            game_index = int(request.form.get("game_list_element_index"))
            session["game_index"] = game_index
            game_data =games["games"][game_index]
            return render_template("game_details.html", game_data = game_data)


    if session["game_index"]!=None:
        return render_template("game_details.html", game_data = games["games"][session["game_index"]])
    
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

    scenario = games_scenarios["scenarios"][session["game_index"]]["scenario"]

    if not session["direction"] in [-1,1]:
        session["direction"] = 0


    if not "stage" in session.keys():# or session["stage"] == None:
        session["stage"] = 0
    else:
        session["stage"] +=session["direction"]
        if session["stage"] <0:
            session["stage"] =0
        elif session["stage"]>len(scenario)-1:
            session["stage"] = len(scenario)-1
        session["direction"] = 0 

    #scenario = games_scenarios[session["game_index"]] ["scenario"][session["stage"]]
    stage = scenario[session["stage"]]

    stage_template = stage["template"]

    if stage_template == "game_answer":
        session["answer"] = stage["answer"]

    return render_template(f'{stage_template}.html', stage = stage, stage_index = session["stage"], last_stage_index = len(scenario))
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

        result = User.query.filter_by(user_login=f'{request.form.get("login")}').all()
        if len(result) == 0:
            return render_template("login.html", msg= "User with this login does not exist!")
        
        if not request.form.get("password"):
            return render_template("login.html", msg= "You have to provide password!")
        

        if  not bcrypt.check_password_hash(result[0].user_password, request.form.get("password")) :
            return render_template("login.html", msg = "Wrong login or password")



        session["login"] = request.form.get("login")
        return redirect("/")
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":


        if not request.form.get("login"):
            return render_template("register.html", msg = "You have to provide login!")

        result = User.query.filter_by(user_login=f'{request.form.get("login")}').all()
        if len(result) >0:
            return render_template("register.html", msg= "User with such login exists!")
        
        if not request.form.get("password"):
            return render_template("register.html", msg= "You have to provide password!")

        if not request.form.get("confirm_password"):
            return render_template("register.html", msg= "You have to confirm password!")

        if request.form.get("confirm_password") != request.form.get("password"):
            return render_template("register.html", msg= "Passwords are not the same!")

        hashed_password = bcrypt.generate_password_hash(request.form.get("password")).decode('utf-8') 

        new_user = User(user_login=request.form.get("login"), user_password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session["login"] = request.form.get("login")
        return redirect("/")
    

    return render_template("register.html")



if __name__ == '__main__':
    #get_secrets()
    app.run(debug=True, host='0.0.0.0', port="5000")