from flask_wtf import FlaskForm
from models import User
from wtforms import StringField, FloatField
from wtforms.fields.simple import PasswordField
from wtforms.validators import InputRequired, Optional

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class LoginForm(FlaskForm): 
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])