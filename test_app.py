import app
from models import Admin, Candidate, Election, Race, Voter, Votes, Precincts, PollManager, database, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


# Test paths
def test_hello_route():
    response = app.app.test_client().get('/hello')

    assert response.status_code == 200


# Voter Registration Test
def test_new_voter():
    voter = Voter('John', 'test@gmail.com', '1234567890', '1 test st', 'Iowa City', 'Iowa', '52240', 20,
                  'Driving License', 0000)

    hashed_password = generate_password_hash('testingcreation123')
    # assert voter.name == 'John'
    assert voter.email == 'test@gmail.com'
    assert hashed_password != 'testingcreation123'
    assert voter.phone_number == '1234567890'
    assert voter.address == '1 test st'
    assert voter.city == 'Iowa City'
    assert voter.state == 'Iowa'
    assert voter.zipcode == '52240'
    assert voter.age == 20
    assert voter.identification == 'Driving License'


# Admin Registration Test
def test_new_admin():
    admin = Admin('Test Admin', 'testadmin@gmail.com')
    assert admin.name == 'Test Admin'
    assert admin.email == 'testadmin@gmail.com'


# Manager Creation Test
def test_new_manager():
    manager = PollManager('Test Manager', 'manager@gmail.com', 'P1')

    assert manager.name == 'Test Manager'
    assert manager.email == 'manager@gmail.com'
    assert manager.precinct == 'P1'


# Candidate Creation Test
def test_new_candidate():
    candidate = Candidate('Candidate Test', 'Republican Party', 'Senate', 0, 'Test statement')

    assert candidate.full_name == 'Candidate Test'
    assert candidate.party == 'Republican Party'
    assert candidate.position == 'Senate'
    assert candidate.votes == 0
    assert candidate.statement == 'Test statement'


# Race Creation Test
def test_new_race():
    race = Race('Senate Race', '2', 'P1', 1)

    assert race.name == 'Senate Race'
    assert race.term == '2'
    assert race.precinct == 'P1'
    assert race.election_id == 1


# Election Creation Test
def test_new_election():
    election = Election('General Election', 'Senate', '06/22/2022')

    assert election.name == 'General Election'
    assert election.electoral_constituency == 'Senate'
    assert election.election_date == '06/22/2022'


# Precinct Creation Test
def test_new_precinct():
    precinct = Precincts('P1', 52240, 0000, 4999, 'Iowa City', 'manager@gmail.com', 'iowa@gmail.com')

    assert precinct.precinct_name == 'P1'
    assert precinct.zipcode == 52240
    assert precinct.plus4start == 0000
    assert precinct.plus4end == 4999
    assert precinct.location == 'Iowa City'
    assert precinct.polling_manager_email == 'manager@gmail.com'
    assert precinct.state_office_email == 'iowa@gmail.com'


# Test login
def test_valid_login():
    response = app.app.test_client().post('/users/login',
                                          data=dict(email='testvoter@gmail.com', password='testvoter123'),
                                          follow_redirects=True)
    assert response.status_code == 200
    assert b"Login to Account" in response.data

    response = app.app.test_client().get('/users/logout', follow_redirects=True)
    assert response.status_code == 200


def test_register():
    response = app.app.test_client().post('/users/login',
                                          data=dict(email='testvoter@gmail.com', password='testvoter123'))
    res = app.app.test_client().get('/users/profile')
    assert res.status_code == 200


# Testing page access
def test_accesss():
    response = app.app.test_client().get('/users/profile')
    assert response.status_code == 302  # Should not access unless logged in


def test_search_user():
    admin = Admin('Test Admin', 'testadmin@gmail.com')

    findAdmin = Admin.query.filter_by(email=admin.email).first()
    assert findAdmin.email == admin.email
    assert findAdmin.name == admin.name


def test_approve_user():
    voter = Voter('Test', 'testvoter@gmail.com', '1234567890', '1 main st', 'Iowa City', 'Iowa', '52240', 40,
                  'Driving License', 0000)

    findVoter = Voter.query.filter_by(email=voter.email).first()
    findVoter.approved = True
    findVoter.denied = False
    database.session.merge(findVoter)
    database.session.flush()

    assert findVoter.approved == True

    findVoter.approved = False
    findVoter.denied = True
    database.session.merge(findVoter)
    database.session.flush()


# test adding votes
def test_new_vote():

    vote = Votes(1, 1, 1, 'E10AD0B0F3894C3D8D10BC5952F34608')

    assert vote.race_id == 1
    assert vote.election_id == 1
    assert vote.candidate_id == 1
    assert vote.voter_id != generate_password_hash('E10AD0B0F3894C3D8D10BC5952F34608')


# test adding ballots
def test_new_ballot():
    response = app.app.test_client().get('/users/elections/1/ballot')
    election = Election('General Election', 'Senate', '06/22/2022')
    first_candidate = Candidate('Candidate Test', 'Republican Party', 'Senate', 0, 'Test statement')
    second_candidate = Candidate('Mike', 'Democratic Party', 'Senate', 0, 'Test statement')
    race = Race('Senate Race', '2', 'P1', 1)

    assert election.name == 'General Election'
    assert election.electoral_constituency == 'Senate'
    assert election.election_date == '06/22/2022'

    assert race.name == 'Senate Race'
    assert race.term == '2'
    assert race.precinct == 'P1'
    assert race.election_id == 1

    assert first_candidate.full_name == 'Candidate Test'
    assert first_candidate.party == 'Republican Party'
    assert first_candidate.position == 'Senate'
    assert first_candidate.votes == 0
    assert first_candidate.statement == 'Test statement'

    assert second_candidate.full_name == 'Mike'
    assert second_candidate.party == 'Democratic Party'
    assert second_candidate.position == 'Senate'
    assert second_candidate.votes == 0
    assert second_candidate.statement == 'Test statement'

    assert response.status_code == 200

