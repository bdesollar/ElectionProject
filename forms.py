import phonenumbers
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, widgets, IntegerField, \
    BooleanField, FormField, FieldList
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_table import Table, Col
from email_validator import validate_email, EmailNotValidError


class AdminRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email(message='Enter a valid email'), Length(min=6, max=40)])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=60,
                                                                             message='Enter a password with a minimum '
                                                                                     'of 8 characters')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password2', message='Passwords '
                                                                                                           'should '
                                                                                                           'match')])
    submit = SubmitField('Create')


class MultipleCheckBoxesField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class VoterRegistrationForm(FlaskForm):
    identifications = [('Driving License', 'Driving License'), ('Passport Number', 'Passport Number'),
                       ('Social Security Number', 'Social Security Number'), ]
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email(message='Enter a valid email'), Length(min=6, max=40)])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zipcode = StringField('Zip Code', validators=[DataRequired()])
    zipcode_plus4 = StringField('Plus 4 Code (0000-9999)', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    identification = MultipleCheckBoxesField('Please choose two identification documents:', choices=identifications)
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=60,
                                                                             message='Enter a password with a minimum '
                                                                                     'of 8 characters')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password2', message='Passwords '
                                                                                                           'should '
                                                                                                           'match')])
    submit = SubmitField('Create')

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')


class BallotForm(FlaskForm):
    key = StringField('key', validators=[DataRequired(), Length(max=255)])
    chose_race = SubmitField('Choose Race')
    vote_in_race = SubmitField('Vote in Race')
    submit_all_votes = SubmitField('Submit all Votes')


class CandidateInfoForm(FlaskForm):
    return_to_vote = SubmitField('Return to Vote')


class ElectionSummary(FlaskForm):
    return_to_elections = SubmitField('Return to Elections')


class DisplayElectionResultsForm(FlaskForm):
    return_to_elections = SubmitField('Return to Elections')


class PollManagerRegistration(FlaskForm):
    precinct = StringField('Precinct', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email(message='Enter a valid email'), Length(min=6, max=40)])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=60,
                                                                             message='Enter a password with a minimum '
                                                                                     'of 8 characters')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password2', message='Passwords '
                                                                                                           'should '
                                                                                                           'match')])
    submit = SubmitField('Create')


class UpdateVoterProfileForm(FlaskForm):
    name = StringField('First Name', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email(message='Enter a valid email'), Length(min=6, max=40)])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zipcode = StringField('Zip Code', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=60,
                                                                             message='Enter a password with a minimum '
                                                                                     'of 8 characters')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password2', message='Passwords '
                                                                                                           'should '
                                                                                                           'match')])
    submit = SubmitField('Update')


class LoginForm(FlaskForm):
    user_id = StringField('Voter or Admin Email', validators=[DataRequired(), Length(min=6, max=40)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class VoterLoginForm(FlaskForm):
    voter_id = StringField('Email', validators=[DataRequired(), Length(min=6, max=40)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ResetEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=40)])


class ResetRequestForm(FlaskForm):
    user_id = StringField('Email', validators=[DataRequired(), Length(min=6, max=40)])
    submit = SubmitField('Reset Password')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=60,
                                                                            message='Enter a password with a minimum '
                                                                                    'of 8 characters')])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords '
                                                                                             'should '
                                                                                             'match')])
    submit = SubmitField('Change Password', validators=[DataRequired()])


class ResetPasswordPinForm(FlaskForm):
    code = IntegerField('Code', validators=[DataRequired()])
    submit = SubmitField('Submit Code', validators=[DataRequired()])


class SearchVoterForm(FlaskForm):
    key = StringField('key', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Search', validators=[DataRequired()])


class ViewElectionForm(FlaskForm):
    submit = SubmitField('Search', validators=[DataRequired()])


class SearchElectionForm(FlaskForm):
    key = StringField('key', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Search', validators=[DataRequired()])


class SetupElection(FlaskForm):
    title = StringField('Title of Election', validators=[DataRequired()])
    electoral_constituency = StringField('Electoral Constituency', validators=[DataRequired()])
    date = StringField('Date of Election', validators=[DataRequired()])
    submit_data = SubmitField('Add Election Info')
    submit_election = SubmitField('Submit Full Election Data')


class AddPrecinct(FlaskForm):
    precinct = StringField('Precinct', validators=[DataRequired()])
    zipcode = code = IntegerField('Zip Code', validators=[DataRequired()])
    plus_four_start = IntegerField('+ 4 Start', validators=[DataRequired()])
    plus_four_end = IntegerField('+ 4 End', validators=[DataRequired()])
    location = StringField('Location of Election', validators=[DataRequired()])
    polling_manager_email = StringField('Polling Manager Email')
    state_office_email = StringField('State Office Email', validators=[DataRequired()])
    submit = SubmitField('Add Precinct')


class AddCandidate(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    party = StringField('Party', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    statement = StringField('Statement (Optional)', validators=[DataRequired()])
    submit = SubmitField('Add Candidate')


class AddRace(FlaskForm):
    name = StringField('Race Name', validators=[DataRequired()])
    term = StringField('Race Term', validators=[DataRequired()])
    precinct = StringField('Precincts Seperated by Commas (P1, P2...', validators=[DataRequired()])
    submit = SubmitField('Add Race')


class AddElection(FlaskForm):
    name = StringField('Election Name', validators=[DataRequired()])
    term = StringField('Race Term', validators=[DataRequired()])
    precinct = StringField('Precinct', validators=[DataRequired()])
    submit = SubmitField('Add Election')
