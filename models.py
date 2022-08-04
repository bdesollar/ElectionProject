import datetime
import uuid
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from mysqldborm import DevORMConfig
from sqlalchemy_utils import EmailType
from flask_login import UserMixin, LoginManager, login_required, logout_user, current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(DevORMConfig)
app.config['SECRET_KEY'] = 'any secret key will work'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database = SQLAlchemy(app, session_options={'autocommit': True})

# Create SQLAlchemy object
# database = SQLAlchemy(app, session_options={'autocommit': True})

# Create LoginManager object
login_manager = LoginManager()
login_manager.login_view = 'home'
login_manager.init_app(app)


# FEEL FREE TO ADD MORE COLUMNS IF NECESSARY
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html

class PollManager(UserMixin, database.Model):
    __tablename__ = 'poll_manager'
    id = database.Column(database.Integer(), autoincrement=True, primary_key=True)
    precinct = database.Column(database.String(255))
    user_id = database.Column(database.String(255), unique=True, default=str(uuid.uuid4().hex).upper())
    password = database.Column(database.String(255))
    name = database.Column(database.String(255))
    email = database.Column(EmailType, index=True, unique=True)
    pin = database.Column(database.Integer())
    login_type = database.Column(database.String(60), default='poll manager')
    authorized = database.Column(database.Boolean(), default=False)

    # date_created = database.Column(database.DateTime, default=datetime.timezone.utc)

    def __init__(self, name, email, precinct):
        self.name = name
        self.email = email
        self.precinct = precinct

    def __repr__(self):
        return self.name + " " + self.email

    # Set hash password
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Election(UserMixin, database.Model):
    __tablename__ = 'election'
    election_id = database.Column(database.Integer(), autoincrement=True, primary_key=True)
    name = database.Column(database.String(60))
    electoral_constituency = database.Column(database.String(60))
    election_date = database.Column(database.String(60))
    active = database.Column(database.Boolean(), default=False)
    complete = database.Column(database.Boolean(), default=False)
    precincts = database.Column(database.String(255))

    def __init__(self, name, electoral_constituency, election_date):
        self.name = name
        self.electoral_constituency = electoral_constituency
        self.election_date = election_date


class Race(UserMixin, database.Model):
    __tablename__ = 'race'
    race_id = database.Column(database.Integer(), autoincrement=True, primary_key=True)
    election_id = database.Column(database.Integer())  # ForeignKey('election.election_id'))
    name = database.Column(database.String(60))
    term = database.Column(database.String(60))
    precinct = database.Column(database.String(60))

    def __init__(self, name, term, precinct, election_id):
        self.name = name
        self.term = term
        self.precinct = precinct
        self.election_id = election_id


class Candidate(UserMixin, database.Model):
    __tablename__ = 'candidate'
    candidate_id = database.Column(database.Integer(), autoincrement=True, primary_key=True)
    full_name = database.Column(database.String(60))
    race_id = database.Column(database.Integer())  # ForeignKey('race.race_id'))
    party = database.Column(database.String(60))
    position = database.Column(database.String(60))
    votes = database.Column(database.Integer())
    statement = database.Column(database.String(250))

    def __init__(self, full_name, party, position, race_id, statement):
        self.full_name = full_name
        self.party = party
        self.position = position
        self.race_id = race_id
        self.votes = 0
        self.statement = statement


class Precincts(UserMixin, database.Model):
    __tablename__ = 'precincts'
    precinct_id = database.Column(database.Integer(), autoincrement=True, primary_key=True)
    precinct_name = database.Column(database.String(60))
    zipcode = database.Column(database.Integer())
    plus4start = database.Column(database.Integer())
    plus4end = database.Column(database.Integer())
    location = database.Column(database.String(60))
    polling_manager_email = database.Column(database.String(60))
    state_office_email = database.Column(database.String(60))

    def __init__(self, precinct_name, zipcode, plus4start, plus4end, location, polling_manager_email,
                 state_office_email):
        self.precinct_name = precinct_name
        self.zipcode = zipcode
        self.plus4start = plus4start
        self.plus4end = plus4end
        self.location = location
        self.polling_manager_email = polling_manager_email
        self.state_office_email = state_office_email


class Admin(UserMixin, database.Model):
    """Model for the users/admin"""

    __tablename__ = 'admin'

    # Add columns
    id = database.Column(database.Integer(), autoincrement=True, primary_key=True)
    user_id = database.Column(database.String(255), unique=True, default=str(uuid.uuid4().hex).upper())
    password = database.Column(database.String(255))
    name = database.Column(database.String(255))
    email = database.Column(EmailType, index=True, unique=True)
    pin = database.Column(database.Integer())
    login_type = database.Column(database.String(60), default='admin')

    # date_created = database.Column(database.DateTime, default=datetime.timezone.utc)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return self.name + " " + self.email

    # Set hash password
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Votes(UserMixin, database.Model):
    """Model for the users/voters"""

    __tablename__ = 'votes'

    # Add columns
    id = database.Column(database.Integer(), autoincrement=True, primary_key=True)
    race_id = database.Column(database.Integer())
    election_id = database.Column(database.Integer())
    candidate_id = database.Column(database.Integer())
    voter_id = database.Column(database.String(255), unique=True, default=str(uuid.uuid4().hex).upper())

    def __init__(self, race_id, election_id, candidate_id, voter_id):
        self.race_id = race_id
        self.election_id = election_id
        self.candidate_id = candidate_id
        self.election_id = election_id
        self.hide_user(voter_id)

    def hide_user(self, voter_id):
        self.voter_id = generate_password_hash(voter_id)

    # Check password
    def check_user(self, voter_id):
        return check_password_hash(self.password_hash, voter_id)


class Voter(UserMixin, database.Model):
    """Model for the users/voters"""

    __tablename__ = 'voter'

    # Add columns
    id = database.Column(database.Integer(), autoincrement=True, primary_key=True)
    voter_id = database.Column(database.String(255), unique=True, default=str(uuid.uuid4().hex).upper())
    password = database.Column(database.String(255))
    name = database.Column(database.String(255))
    email = database.Column(EmailType, index=True, unique=True)
    phone_number = database.Column(database.String(15))
    address = database.Column(database.String(255))
    city = database.Column(database.String(255))
    state = database.Column(database.String(255))
    zipcode = database.Column(database.Integer())
    age = database.Column(database.Integer())
    identification = database.Column(database.String(255))
    approved = database.Column(database.Boolean(), default=False)
    denied = database.Column(database.Boolean(), default=False)
    pin = database.Column(database.Integer())
    login_type = database.Column(database.String(60), default='voter')
    zipcode_plus4 = database.Column(database.Integer())
    precinct = database.Column(database.String(15))
    elections_voted_in = database.Column(database.String(255))

    # date_created = database.Column(database.DateTime, default=datetime.timezone.utc)

    def __init__(self, name, email, phone_number, address, city, state, zipcode, age, identification, zipcode_plus4):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.age = age
        self.identification = identification
        self.zipcode_plus4 = zipcode_plus4
        self.elections_voted_in = ""

    def __repr__(self):
        return self.name + " " + self.email

    def set_plus4(self, digits):
        self.zipcode_plus4 = digits

    # Set hash password
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
