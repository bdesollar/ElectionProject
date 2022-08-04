import time
from ast import Add
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sendEmail import sendEmails, SendApprovalEmails
from mysqldb import mysql
from mysqldb import app
from mysqldborm import DevORMConfig
import random
import string
from sqlalchemy import or_
from flask_msearch import Search
from forms import AddCandidate, AddElection, AddRace, AdminRegistrationForm, LoginForm, ResetEmailForm, \
    ResetPasswordForm, UpdateVoterProfileForm, SearchVoterForm, VoterRegistrationForm, ResetRequestForm, \
    ResetPasswordPinForm, AddPrecinct, SetupElection, PollManagerRegistration, ViewElectionForm, BallotForm, \
    CandidateInfoForm, ElectionSummary, DisplayElectionResultsForm
from models import Admin, Candidate, Election, Race, Voter, Precincts, PollManager, database, login_manager, app, Votes
from election_info import currentElection, currentVoter

# app = Flask(__name__)
# Configuration for using ORM
app.config.from_object(DevORMConfig)
app.config['SECRET_KEY'] = 'any secret key will work'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create SQLAlchemy object
# database = SQLAlchemy(app, session_options={'autocommit': True})

# Create LoginManager object
# login_manager = LoginManager()
login_manager.login_view = 'home'
login_manager.init_app(app)

currentElection = currentElection()
currentVoter = currentVoter()


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))


@app.route('/registration')
def registration():
    return render_template('registration.html', name=registration)


# Voter Login
@app.route('/users/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        voter = Voter.query.filter_by(email=form.user_id.data).first()
        admin = Admin.query.filter_by(email=form.user_id.data).first()
        poll_manager = PollManager.query.filter_by(email=form.user_id.data).first()

        if voter is not None:
            password = request.form.get('password')
            if check_password_hash(voter.password, password):
                session["login_type"] = "voter"
                login_user(voter)
                if voter.approved and voter.denied is False:
                    return redirect(url_for('profile'))
                else:
                    return redirect(url_for('pending_approval'))
            flash('Invalid id or password')
        elif admin is not None:
            password = request.form.get('password')
            if check_password_hash(admin.password, password):
                session["login_type"] = "admin"
                login_user(admin)
                return redirect(url_for('profile'))
            flash('Invalid id or password')
        elif poll_manager is not None:
            password = request.form.get('password')
            if check_password_hash(poll_manager.password, password):
                session["login_type"] = "poll manager"
                login_user(poll_manager)
                if poll_manager.authorized:
                    return redirect(url_for('profile'))
                else:
                    return redirect(url_for('waiting_authorization'))
            flash('Invalid id or password')
        else:
            return render_template('/users/login.html', form=form)
    return render_template('/users/login.html', form=form)


@app.route('/users/logout')
@login_required
def logout():
    session.pop("login_type", None)
    return redirect(url_for('home'))


'''
#using to test html
@app.route('/testhtml')
def testhtml():
    form = AddCandidate()
    return render_template('/users/admin_add_election.html', form=form)
'''


# Ading candidates, might follow the same for race and election
@app.route('/users/admin_add_candidate', methods=['GET', 'POST'])
# @login_required
def add_candidates():
    """Route for voter registration"""
    # Create a form
    form = AddCandidate()
    race_list = []
    races = Race.query.filter_by(election_id=currentElection.election_id).all()
    if not races:
        flash("No Races Exist for this candidate to be added to", 'warning')
    else:
        for race in races:
            race_list.append(race.name)
        if request.method == 'POST':
            race_id1 = None
            for race in races:
                if race.name == request.form.get('Races'):
                    race_id1 = race.race_id
            candidates = Candidate.query.filter_by(race_id=race_id1).all()
            candidates_already_exists = False
            if candidates:
                for candidate in candidates:
                    if candidate.full_name == form.name.data:
                        flash('Candidate with this name already exists', 'warning')
                        candidates_already_exists = True
                        break
            if not candidates_already_exists:
                # Create new candidate
                candidate = Candidate(full_name=request.form['name'], party=request.form['party'],
                                      position=request.form['position'],
                                      race_id=race_id1, statement=request.form['statement'])
                database.session.add(candidate)
                database.session.flush()
                currentElection.candidates.append(request.form['name'])
                currentElection.candidates_made = True
                flash('CANDIDATE CREATED')
                return redirect(url_for('setup_election'))
    return render_template('users/admin_add_candidate.html', form=form, Races=race_list)


# ADDING RACE
@app.route('/users/admin_add_race', methods=['GET', 'POST'])
# @login_required
def add_race():
    """Route to add Race"""
    # Create a form
    form = AddRace()
    if request.method == 'POST':
        races = Race.query.filter_by(election_id=currentElection.election_id).all()
        race_already_exists = False
        if races:
            for race in races:
                if race.name == form.name.data:
                    flash('Race with this name already exists', 'warning')
                    race_already_exists = True
                    break
        if not race_already_exists:
            precincts = []
            all_precincts_exist = True
            for precinct in form.precinct.data.split(", "):
                precincts.append(precinct)
                precinct_check = Precincts.query.filter_by(precinct_name=precinct).first()
                if not precinct_check:
                    all_precincts_exist = False
            if all_precincts_exist:
                race = Race(name=request.form['name'], term=request.form['term'],
                            precinct=request.form['precinct'], election_id=currentElection.election_id)
                flash('RACE CREATED')
                currentElection.race_id = race.race_id
                database.session.add(race)
                database.session.flush()
                elections = Election.query.filter_by(election_id=currentElection.election_id).first()
                elections_precinct_list = []
                election_string = ""
                if elections.precincts:
                    for election_precinct in elections.precincts.split(", "):
                        if election_precinct not in elections_precinct_list:
                            elections_precinct_list.append(election_precinct)
                            election_string += election_precinct + ", "
                    for precinct in precincts:
                        if precinct not in elections_precinct_list:
                            elections_precinct_list.append(precinct)
                            election_string += precinct + ", "
                    election_string = election_string[:-2]
                    elections.precincts = election_string
                else:
                    elections.precincts = form.precinct.data
                currentElection.race_set = True
                database.session.merge(elections)
                database.session.flush()
                flash('Race Created', 'success')
                return redirect(url_for('setup_election'))
            else:
                flash(f'Precinct ({precincts[-1]}) does not exist', 'warning')
    # return  template for registration
    return render_template('users/admin_add_race.html', form=form)


@app.route('/users/add_precinct', methods=['GET', 'POST'])
def add_precinct():
    """Route to add precinct"""
    form = AddPrecinct()
    if request.method == 'POST':
        polling_manager = PollManager.query.filter_by(email=form.polling_manager_email.data).first()
        if not polling_manager:
            flash('User with this email address does not exist.', 'warning')
        else:
            precinct_check = Precincts.query.filter_by(zipcode=request.form['zipcode']).all()
            if precinct_check:
                precinct_good = True
                for precincts in precinct_check:
                    if precincts.precinct_name == form.precinct.data:
                        flash('Precinct Name Already Exists in that Zipcode', 'warning')
                        precinct_good = False
                        break
                if precinct_good:
                    precinct = Precincts(precinct_name=request.form['precinct'], zipcode=request.form['zipcode'],
                                         plus4start=0000,
                                         location=request.form['location'],
                                         plus4end=9999,
                                         polling_manager_email=request.form['polling_manager_email'],
                                         state_office_email=request.form['state_office_email'])
                    database.session.add(precinct)
                    # database.session.commit()
                    database.session.flush()
                    precinct_check = Precincts.query.filter_by(zipcode=request.form['zipcode']).all()
                    count = len(precinct_check)
                    end4_curr = 0
                    increment = int(10000 / count) - 1
                    first = False
                    for precincts in precinct_check:
                        if not first:
                            first = True
                            precincts.plus4start = 0000
                            precincts.plus4end = increment
                            end4_curr = precincts.plus4end
                        else:
                            precincts.plus4start = end4_curr + 1
                            precincts.plus4end = end4_curr + increment + 1
                            end4_curr = precincts.plus4end
                        database.session.merge(precincts)
                        database.session.flush()
                    flash('Precinct Created', 'success')
                    return redirect(url_for('setup_election'))
            else:
                precinct = Precincts(precinct_name=request.form['precinct'], zipcode=request.form['zipcode'],
                                     plus4start=0000,
                                     location=request.form['location'],
                                     plus4end=9999,
                                     polling_manager_email=request.form['polling_manager_email'],
                                     state_office_email=request.form['state_office_email'])
                database.session.add(precinct)
                database.session.flush()
                flash('Precinct Created', 'success')
                return redirect(url_for('setup_election'))

    return render_template('/users/add_precinct.html', title='Create Precinct', form=form, legend="Enter Code")


# returns election object
def get_election():
    """Route to get election"""
    election = Election.query.filter_by(name=currentElection.election_name).first()
    while not election:
        election = Election.query.filter_by(name=currentElection.election_name).first()
        if election:
            currentElection.election_id = election.election_id
            currentElection.election_name = election.name
            currentElection.date = election.election_date
        time.sleep(1)
    return election


@app.route('/users/setup_election', methods=['GET', 'POST'])
def setup_election():
    """Route to set up election"""
    global currentElection
    form = SetupElection()
    if request.method == 'GET':
        form.title.data = currentElection.election_name
        form.electoral_constituency.data = currentElection.election_name
        form.date.data = currentElection.date
        return render_template('/users/setup_election.html', title='Enter Election Info', form=form,
                               race_set=currentElection.race_set, candidates_made=currentElection.candidates_made,
                               election_data_added=currentElection.election_data_added)
    if request.method == 'POST':
        if (currentElection.election_name == None) and (form.title.data != None):
            election = Election(name=request.form['title'],
                                electoral_constituency=request.form['electoral_constituency'],
                                election_date=request.form['date'])
            database.session.add(election)
            # database.session.commit()
            database.session.flush()
            currentElection.election_id = election.election_id
            currentElection.election_name = election.name
            currentElection.date = election.election_date
            currentElection.election_data_added = True
        if form.submit_election.data == True:
            currentElection = currentElection.reset()
            return redirect(url_for('home'))

    return render_template('/users/setup_election.html', title='Enter Election Info', form=form,
                           race_set=currentElection.race_set, candidates_made=currentElection.candidates_made,
                           election_data_added=currentElection.election_data_added)


@app.route('/users/register/voter', methods=['GET', 'POST'])
def voter_registration():
    """Route for voter registration"""
    # Create a form
    form = VoterRegistrationForm()
    if request.method == 'POST':
        admin = Admin.query.filter_by(email=form.email.data).first()
        voter = Voter.query.filter_by(email=form.email.data).first()
        poll_manager = PollManager.query.filter_by(email=form.email.data).first()
        if voter or admin or poll_manager:
            flash('User with this email address already exists.')
        else:
            # Create new voter
            voter = Voter(name=request.form['name'], email=request.form['email'],
                          phone_number=request.form['phone_number'], address=request.form['address'],
                          city=request.form['city'], state=request.form['state'], zipcode=request.form['zipcode'],
                          age=request.form['age'], identification=request.form['identification'],
                          zipcode_plus4=request.form['zipcode_plus4'])
            # Set password
            voter.set_password(form.password1.data)
            database.session.add(voter)
            database.session.flush()
            flash('You account has successfully been created, but it needs approval from the administrator.')
            session["login_type"] = "voter"
            login_user(voter)
            return redirect(url_for('pending_approval'))
    # return  template for registration
    return render_template('users/voter_register.html', name=admin_registration, form=form)


@app.route('/users/register/admin', methods=['GET', 'POST'])
def admin_registration():
    """Route for admin registration"""
    # Create a form
    form = AdminRegistrationForm()
    if request.method == 'POST':
        admin = Admin.query.filter_by(email=form.email.data).first()
        voter = Voter.query.filter_by(email=form.email.data).first()
        poll_manager = PollManager.query.filter_by(email=form.email.data).first()
        if voter or admin or poll_manager:
            flash('User with this email address already exists.')
        else:
            # Create new Admin
            admin = Admin(name=request.form['name'], email=request.form['email'])
            # Set password
            admin.set_password(form.password1.data)
            database.session.add(admin)
            database.session.flush()
            flash('You account has successfully been created.')
            session["login_type"] = "admin"
            login_user(admin)
            return redirect(url_for('profile'))
    # return  template for registration
    return render_template('users/admin_register.html', name=admin_registration, form=form)


@app.route('/users/manage/elections', methods=['GET', 'POST'])
def admin_manage_and_view_elections():
    """Route for viewing elections"""
    form = SearchVoterForm()
    elections_voted_for = []
    try:
        if session.get('login_type') == 'voter':
            voter = Voter.query.filter_by(id=currentVoter.current_voter_id).first()
            voter_zip = voter.zipcode
            voter_plus4 = voter.zipcode_plus4
            elections_voted_for = []
            elections_voted_in = voter.elections_voted_in
            if elections_voted_in:
                for elections_voted in elections_voted_in.split(", "):
                    if elections_voted != "":
                        elections_voted_for.append(int(elections_voted))
    except:
        flash("No voters exist yet")
    # try:
    elections = Election.query
    elections_filtered_list = None
    if session.get('login_type') == 'voter':
        # elections that have races in the voters precinct
        elections_filtered_list = []
        election_id_list = []
        for election in elections:
            races = Race.query.filter_by(election_id=election.election_id).all()
            for race in races:
                precincts_list = []
                for precinct_name in race.precinct.split(", "):
                    precincts_list.append(precinct_name)
                    precincts = Precincts.query.filter_by(precinct_name=precinct_name).all()
                    for precinct in precincts:
                        if precinct.zipcode == voter_zip and election.active:
                            if precinct.plus4start <= voter_plus4 <= precinct.plus4end:
                                if not voter.precinct:
                                    voter.precinct = precinct_name
                                    database.session.merge(voter)
                                    database.session.flush()
                                if election.election_id not in election_id_list:
                                    elections_filtered_list.append(election)
                                    election_id_list.append(election.election_id)
    if request.method == 'POST':
        key = request.form['key']
        key = "%{}%".format(key)
        elections = elections.filter(
            or_(Election.name.like(key)))
        if elections_filtered_list != None:
            return render_template('users/admin/display_elections.html', name=admin_manage_and_view_elections,
                                   elections=elections_filtered_list, form=form, current_user=current_user,
                                   voter=voter, elections_voted_for=elections_voted_for)
        else:
            flash('No Elections Exist Yet', 'warning')
            elections = elections
            return render_template('users/admin/display_elections.html', name=admin_manage_and_view_elections,
                                   elections=elections, form=form, current_user=current_user,
                                   elections_voted_for=elections_voted_for)
    if elections_filtered_list != None:
        return render_template('users/admin/display_elections.html', name=admin_manage_and_view_elections,
                               elections=elections_filtered_list, form=form, current_user=current_user,
                               voter=voter, elections_voted_for=elections_voted_for)
    else:
        flash('No Elections Exist Yet', 'warning')
        elections = elections
        return render_template('users/admin/display_elections.html', name=admin_manage_and_view_elections,
                               elections=elections, form=form, current_user=current_user,
                               elections_voted_for=elections_voted_for)
    # except:
    # flash('No Elections Exist Yet', 'warning')
    # return redirect(url_for('profile'))


@app.route('/users/manage/elections/<int:id>/view', methods=['GET', 'POST'])
def display_election(id):
    """Route for displaying election"""
    form = ViewElectionForm()
    race_list = []
    race_selected = False
    election = Election.query.filter_by(election_id=id).first()
    races = Race.query.filter_by(election_id=id).all()
    if not races:
        flash("No Races Exist for this candidate to be added to", 'warning')
    else:
        for race in races:
            race_list.append(race)
        if request.method == 'POST':
            for race in race_list:
                if race.name == request.form.get('Races'):
                    currentVoter.user_selected_race = request.form.get('Races')
                    currentVoter.current_race = race
            candidates = Candidate.query.filter_by(race_id=currentVoter.current_race.race_id).all()
            candidate_list = []
            for candidate in candidates:
                candidate_list.append(candidate)
            return render_template('users/admin/view_election.html', name=display_election, Races=race_list,
                                   election=election, form=form, race_selected=True, race=currentVoter.current_race,
                                   candidates=candidate_list)

    return render_template('users/admin/view_election.html', name=admin_registration, Races=race_list,
                           election=election, form=form, race_selected=False)


@app.route('/users/elections/<int:id>/ballot', methods=['GET', 'POST'])
def ballot(id):
    """Route for ballet"""
    global currentVoter, race1, currentElection
    currentElection.election_id = id
    form = BallotForm()
    race_list = []
    candidate_list = []
    races_not_voted_in = []
    all_races_voted_in = True
    election = Election.query.filter_by(election_id=id).first()
    races = Race.query.filter_by(election_id=id).all()
    if not races:
        flash("No Races Exist for this candidate to be added to", 'warning')
    else:
        for race in races:
            race_list.append(race)
        if request.method == 'POST':
            if form.submit_all_votes.data:
                all_races_voted_in = True
                races_not_voted_in = []
                for race in races:
                    if race.name not in currentVoter.races_voted_in:
                        all_races_voted_in = False
                        races_not_voted_in.append(race.name)
                if all_races_voted_in:
                    voter = Voter.query.filter_by(id=currentVoter.current_voter_id).first()
                    if not voter.elections_voted_in:
                        voter.elections_voted_in = str(election.election_id)
                    else:
                        elections_voted_in = voter.elections_voted_in
                        elections_voted_in += ", " + str(election.election_id)
                        voter.elections_voted_in = elections_voted_in
                    database.session.merge(voter)
                    database.session.flush()
                    return redirect(url_for('admin_manage_and_view_elections'))
                else:
                    race_names_string = ""
                    for races_names in races_not_voted_in:
                        race_names_string += races_names + ","
                    race_names_string = race_names_string[:-1]
                    flash(f'Did not vote in ({race_names_string}), please vote in these race(s)')
            if form.chose_race.data:
                currentVoter.first_race_choose = True
                for race in race_list:
                    if race.name == request.form.get('Races'):
                        currentVoter.user_selected_race = request.form.get('Races')
                        currentVoter.current_race = race
            candidates = Candidate.query.filter_by(race_id=currentVoter.current_race.race_id).all()
            for candidate in candidates:
                candidate_list.append(candidate)
            if form.vote_in_race.data:
                votes = Votes.query.filter_by(race_id=currentVoter.current_race.race_id).all()
                voter_voted = False
                for vote in votes:
                    # checks the voter_id with the current voter id for current race and sees if the
                    #       current voter voted
                    if check_password_hash(vote.voter_id, currentVoter.current_voter_id):
                        voter_voted = True
                if not voter_voted:
                    candidate_id = None
                    for candidate in candidates:
                        if candidate.full_name == request.form.get('candidates'):
                            candidate_id = candidate.candidate_id
                    if candidate_id:
                        votes = Votes(race_id=currentVoter.current_race.race_id,
                                      election_id=currentVoter.current_race.election_id,
                                      candidate_id=candidate_id,
                                      voter_id=currentVoter.current_voter_id)
                        database.session.add(votes)
                        database.session.flush()
                        if currentVoter.current_race.name not in currentVoter.races_voted_in:
                            currentVoter.races_voted_in.append(currentVoter.current_race.name)
                    else:
                        flash("Candidate not found", "warning")
                else:
                    flash("Voter already voted in this race", "warning")
            return render_template('users/ballot.html', name=display_election, Races=race_list,
                                   election=election, form=form, race_selected=True, race=race,
                                   candidates=candidate_list, first_race_choose=currentVoter.first_race_choose,
                                   selected_race=currentVoter.user_selected_race, all_races_voted_in=all_races_voted_in,
                                   races_not_voted_in=races_not_voted_in)
    return render_template('users/ballot.html', name=display_election, Races=race_list,
                           election=election, form=form, race_selected=False,
                           candidates=candidate_list)


@app.route('/users/manage/elections/<int:id>/view_result', methods=['GET', 'POST'])
def display_election_result(id):
    """Route for displaying election"""
    form = DisplayElectionResultsForm()
    if request.method == 'POST':
        return redirect(url_for('admin_manage_and_view_elections'))
    race_winners = {}
    election = Election.query.filter_by(election_id=id).first()
    races = Race.query.filter_by(election_id=id).all()
    for race in races:
        candidates_votes = {}
        votes = Votes.query.filter_by(race_id=race.race_id).all()
        for vote in votes:
            if vote.candidate_id not in candidates_votes:
                candidates_votes[vote.candidate_id] = 1
            else:
                candidates_votes[vote.candidate_id] += 1
        max_keys = [key for key, value in candidates_votes.items() if value == max(candidates_votes.values())]
        if len(max_keys) > 1:
            candidates_string = ""
            for candidate_id in max_keys:
                candidate = Candidate.query.filter_by(candidate_id=candidate_id).first()
                candidates_string += candidate.full_name + ", "
            candidates_string = candidates_string[:-2]
            race_winners[race] = candidates_string
        else:
            candidate = Candidate.query.filter_by(candidate_id=max_keys[0]).first()
            race_winners[race] = candidate.full_name

    return render_template('users/election_results.html', name=display_election, race_winners=race_winners,
                           election=election, form=form)


@app.route('/users/elections/<int:id>/view_candidate', methods=['GET', 'POST'])
def display_candidate(id):
    """Route for ballet"""
    global currentVoter
    form = CandidateInfoForm()
    candidate = Candidate.query.filter_by(candidate_id=id).first()
    if request.method == 'POST':
        return redirect(url_for('ballot', id=currentElection.election_id))
    return render_template('users/candidate_info.html', form=form, name=display_candidate, candidate=candidate)


@app.route('/users/elections/<int:id>/election_summary', methods=['GET', 'POST'])
def display_election_summary(id):
    global currentVoter
    form = ElectionSummary()
    election = Election.query.filter_by(election_id=id).first()
    races = Race.query.filter_by(election_id=election.election_id).all()
    votes = Votes.query.filter_by(election_id=election.election_id).all()
    candidates_voted_for = []
    candidate_ids = []
    for vote in votes:
        # checks the voter_id with the current voter id for current race and sees if the
        #       current voter voted
        if check_password_hash(vote.voter_id, currentVoter.current_voter_id):
            candidate = Candidate.query.filter_by(candidate_id=vote.candidate_id).first()
            if candidate:
                if candidate.candidate_id not in candidate_ids:
                    candidates_voted_for.append(candidate)
                    candidate_ids.append(candidate.candidate_id)
    if request.method == 'POST':
        return redirect(url_for('admin_manage_and_view_elections'))
    return render_template('users/display_voter_results.html', form=form, name=display_election_summary,
                           candidates_voted_for=candidates_voted_for, races=races, election=election)


@app.route('/users/manage/voters', methods=['GET', 'POST'])
def admin_manage_and_search_voters():
    """Route for managing voters"""
    form = SearchVoterForm()
    try:
        voters = Voter.query
        if request.method == 'POST':
            key = request.form['key']
            key = "%{}%".format(key)
            voters = voters.filter(
                or_(Voter.name.like(key), Voter.city.like(key), Voter.zipcode.like(key), Voter.state.like(key)))
            return render_template('users/admin/manage.html', name=admin_manage_and_search_voters, voters=voters,
                                   form=form)
        voters = voters
        return render_template('users/admin/manage.html', name=admin_manage_and_search_voters, voters=voters, form=form)
    except:
        flash('No Voters Exist Yet', 'warning')
        return redirect(url_for('profile'))


@app.route('/users/manage/poll_managers', methods=['GET', 'POST'])
def manage_poll_managers():
    """Route for managing poll station managers"""
    form = SearchVoterForm()
    try:
        poll_managers = PollManager.query
        precincts = Precincts.query
        if request.method == 'POST':
            key = request.form['key']
            key = "%{}%".format(key)
            poll_managers = poll_managers.filter(
                or_(PollManager.name.like(key), PollManager.precinct.like(key)))
            return render_template('users/admin/managers.html', name=manage_poll_managers,
                                   poll_managers=poll_managers, precincts=precincts, form=form)
        poll_managers = poll_managers
        return render_template('users/admin/managers.html', name=manage_poll_managers, precincts=precincts,
                               poll_managers=poll_managers, form=form)
    except:
        flash('No poll station managers Exist Yet', 'warning')
        return redirect(url_for('profile'))


@app.route('/users/manage/poll_managers/<int:id>/assign', methods=['GET', 'POST'])
def assign_managers(id):
    """Route for assigning managers to poll stations"""

    manager = PollManager.query.get(id)
    manager.authorized = True
    database.session.merge(manager)
    database.session.flush()
    send = SendApprovalEmails()
    send.send_authorization_mail(manager.email)
    return redirect(url_for('manage_poll_managers'))


@app.route('/users/manage/poll_managers/<int:id>/unassign', methods=['GET', 'POST'])
def unassign_managers(id):
    """Route for assigning managers to poll stations"""

    manager = PollManager.query.get(id)
    manager.authorized = False
    database.session.merge(manager)
    database.session.flush()
    send = SendApprovalEmails()
    send.send_authorization_mail(manager.email)
    return redirect(url_for('manage_poll_managers'))


@app.route('/users/manage/poll_managers/<int:id>/ballot/activate', methods=['GET', 'POST'])
def managers_activate_ballot(id):
    """Route for activating ballots"""

    manager = PollManager.query.get(current_user.id)
    election = Election.query.filter_by(election_id=id).first()
    election.active = True
    database.session.merge(election)
    database.session.flush()
    return redirect(url_for('display_polling_station_elections'))


@app.route('/users/manage/poll_managers/<int:id>/end_election', methods=['GET', 'POST'])
def managers_end_election(id):
    """Route for activating ballots"""
    election = Election.query.filter_by(election_id=id).first()
    election.complete = True
    database.session.merge(election)
    database.session.flush()
    return redirect(url_for('display_polling_station_elections'))


@app.route('/users/manage/polling_station/elections', methods=['GET', 'POST'])
def display_polling_station_elections():
    """Route for displaying polling stations"""
    manager = PollManager.query.filter_by(id=current_user.id).first()
    elections = Election.query
    elections_list = []
    for election in elections:
        if manager.precinct in election.precincts:
            elections_list.append(election)
    return render_template('users/managers/precincts.html', name=display_polling_station_elections, elections=elections_list)


@app.route('/users/manage/poll_managers/<int:id>/ballot/deactivate', methods=['GET', 'POST'])
def managers_deactivate_ballot(id):
    """Route for activating ballots"""

    manager = PollManager.query.get(current_user.id)
    election = Election.query.filter_by(election_id=id).first()
    election.active = False
    database.session.merge(election)
    database.session.flush()
    return redirect(url_for('display_polling_station_elections'))


@app.route('/users/manage/voters/<int:id>/approve', methods=['GET', 'POST'])
def approve_voter(id):
    """Route for approving voters"""
    try:
        voter = Voter.query.get(id)
        voter.approved = True
        voter.denied = False
        database.session.merge(voter)
        database.session.flush()
        send = SendApprovalEmails()
        send.send_approval_mail(voter.email)
        return redirect(url_for('admin_manage_and_search_voters'))
    except:
        flash('No Voters Exist Yet', 'warning')
        return redirect(url_for('profile'))


@app.route('/users/manage/voters/<int:id>/deny', methods=['GET', 'POST'])
def deny_voter(id):
    """Route for denying voters"""
    voter = Voter.query.get(id)
    voter.denied = True
    voter.approved = False
    database.session.merge(voter)
    database.session.flush()
    send = SendApprovalEmails()
    send.send_denial_mail(voter.email)
    return redirect(url_for('admin_manage_and_search_voters'))


@app.route('/users/register/poll_manager', methods=['GET', 'POST'])
def poll_manager_registration():
    """Route for polling manager registration"""
    # Create a form
    form = PollManagerRegistration()
    if request.method == 'POST':
        poll_manager_email = PollManager.query.filter_by(email=form.email.data).first()
        if poll_manager_email:
            flash('User with this email address already exists.')
        else:
            # Create new voter
            poll_manager = PollManager(name=request.form['name'], email=request.form['email'],
                                       precinct=request.form['precinct'])
            # Set password
            poll_manager.set_password(form.password1.data)
            database.session.add(poll_manager)
            # database.session.commit()
            database.session.flush()
            flash('You account has successfully been created', 'success')
            # redirect voter to pending page
            return redirect(url_for('add_precinct'))

    # return  template for registration
    return render_template('users/poll_manager_register.html', name=poll_manager_registration, form=form)


@app.route('/users/pending_approval', methods=['GET'])
@login_required
def pending_approval():
    return render_template('users/pending.html', name=pending_approval)


@app.route('/users/waiting_authorization', methods=['GET'])
@login_required
def waiting_authorization():
    return render_template('users/waiting_for_access.html', name=waiting_authorization)


@login_manager.user_loader
def load_user(user_id):
    global currentVoter
    # Query user based on primary key id
    if session.get('login_type') == 'admin':
        return Admin.query.get(int(user_id))
    elif session.get('login_type') == 'voter':
        currentVoter.current_voter_id = user_id
        return Voter.query.get(int(user_id))
    elif session.get('login_type') == 'poll manager':
        return PollManager.query.get(int(user_id))
    else:
        return None


@app.route('/users/profile', methods=['GET'])
@login_required
def profile():
    if session.get('login_type') == 'admin':
        return render_template('users/profile.html', name=profile)
    elif session.get('login_type') == 'voter' and current_user.approved and current_user.denied == False:
        return render_template('users/voter_profile.html', name=profile)
    elif session.get('login_type') == 'poll manager':
        return render_template('users/profile.html', name=profile)
    else:
        return redirect(url_for('pending_approval'))


@app.route('/users/update/', methods=['GET', 'POST'])
@login_required
def edit_voter_profile():
    # Will fix it later, doesn't work correctly
    form = UpdateVoterProfileForm()

    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.phone_number.data = current_user.phone_number
        form.address.data = current_user.address
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.zipcode.data = current_user.zipcode
        form.age.data = current_user.age

    if request.method == 'POST':
        if form.validate_on_submit():
            current_user.name = form.name.data
            current_user.email = form.email.data
            current_user.phone_number = form.phone_number.data
            current_user.address = form.address.data
            current_user.city = form.city.data
            current_user.state = form.state.data
            current_user.zipcode = form.zipcode.data
            current_user.age = form.age.data
            current_user.password1 = form.password1.data
            current_user.password2 = form.password2.data
            # database.session.commit()
            database.session.flush()
            flash('You updated your profile successfully')
            return redirect('profile')
        else:
            flash("The form has a few errors.")
            return render_template('users/edit_profile.html', name=edit_voter_profile, form=form)
    return render_template('users/edit_profile.html', name=edit_voter_profile, form=form)


@app.route('/users/delete/', methods=['GET', 'POST'])
@login_required
def delete_profile():
    user = Voter.query.get_or_404(current_user.id)
    # Doesn't work correctly, will fix it later
    if user is not None:
        database.session.delete(user)
        # database.commit()
        database.session.flush()
        return redirect('home')
        flash('Your account has successfully been deleted')

    else:
        return redirect('home')


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


@app.route('/hello')
def hello_world():
    return 'Hello World!'


# will create a class for user later, global variable is temporary
user_for_reset_password = {'user_id': 'GGEHSJ000', 'type': 'admin', 'code': 0000}


@app.route('/users/reset_password', methods=['GET', 'POST'])
def reset_request():
    form = ResetRequestForm()
    admin = None
    voter = None
    global user_for_reset_password
    if form.data['submit']:
        try:
            voter = Voter.query.filter_by(email=form.user_id.data).one()
        except:
            pass
        # user = cursor.execute("SELECT * FROM voter WHERE email LIKE %s;", (form.user_id.data,))
        if voter:
            user_for_reset_password['user_id'] = form.user_id.data
            user_for_reset_password['type'] = 'voter'
            send_mail = sendEmails()
            code = generate_code()
            user_for_reset_password['code'] = code
            send_mail.send_mail(form.user_id.data, code)
            flash('Reset request sent. Check your email.', 'success')
            return redirect(url_for('check_pin'))
        else:
            try:
                admin = Admin.query.filter_by(email=form.user_id.data).one()
            except:
                pass
            if admin:
                user_for_reset_password['user_id'] = form.user_id.data
                user_for_reset_password['type'] = 'admin'
                send_mail = sendEmails()
                code = generate_code()
                user_for_reset_password['code'] = code
                send_mail.send_mail(form.user_id.data, code)
                flash('Reset request sent. Check your email.', 'success')
                return redirect(url_for('check_pin'))
    return render_template('/users/reset_password.html', title='Reset Request', form=form, legend="Reset Password")


def generate_code():
    return random.randint(1000, 9999)


@app.route('/users/reset_password_check', methods=['GET', 'POST'])
def check_pin():
    form = ResetPasswordPinForm()
    global user_for_reset_password
    if form.data['submit'] == True:
        if form.code.data == user_for_reset_password['code']:
            flash('Code Correct', 'success')
            return redirect(url_for('reset_token'))
        else:
            flash('Code incorrect', 'warning')
    return render_template('/users/confirm_pin.html', title='Enter Code', form=form, legend="Enter Code")


@app.route('/users/reset_password1', methods=['Get', 'POST'])
def reset_token():
    form = ResetPasswordForm()
    admin = False
    user = None
    if user_for_reset_password['type'] == 'voter':
        voter = Voter.query.filter_by(email=user_for_reset_password['user_id']).one()
    elif user_for_reset_password['type'] == 'admin':
        admin = True
        admins = Admin.query.filter_by(email=user_for_reset_password['user_id']).one()
    elif user and admin is None:
        flash("That is invalid token, please try again.", "warning")
        return redirect(url_for('reset_request'))
    if form.data['submit'] == True:
        if admin:
            # Admin.query.filter_by(email=user_for_reset_password['user_id']).one().
            admins.set_password(form.password.data)
            # database.session.commit()
            database.session.flush()
            return redirect(url_for('login'))
            # cursor.execute(
            # f"""UPDATE voter SET password = '{generate_password_hash(form.password.data)}' WHERE email = '{user_for_reset_password['user_id']}'""")
        else:
            voter.set_password(form.password.data)
            # database.session.commit()
            database.session.flush()
            # cursor.execute(
            #  f"""UPDATE admin SET password = '{generate_password_hash(form.password.data)}' WHERE email = '{user_for_reset_password['user_id']}'""")
            return redirect(url_for('login'))

    return render_template('/users/change_password.html', title="Change Password", form=form, legend="Change Passwprd")


if __name__ == '__main__':
    app.run(debug=True)
