from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class HousePredictionForm(FlaskForm):
    area = IntegerField('Area (sq ft)', validators=[DataRequired(), NumberRange(min=500, max=50000)])
    bedrooms = IntegerField('Bedrooms', validators=[DataRequired(), NumberRange(min=1, max=10)])
    bathrooms = IntegerField('Bathrooms', validators=[DataRequired(), NumberRange(min=1, max=10)])
    stories = IntegerField('Stories', validators=[DataRequired(), NumberRange(min=1, max=5)])
    parking = IntegerField('Parking Spaces', validators=[DataRequired(), NumberRange(min=0, max=10)])
    
    mainroad = SelectField('Main Road Access', 
                          choices=[('yes', 'Yes'), ('no', 'No')], 
                          validators=[DataRequired()])
    guestroom = SelectField('Guest Room', 
                           choices=[('yes', 'Yes'), ('no', 'No')], 
                           validators=[DataRequired()])
    basement = SelectField('Basement', 
                          choices=[('yes', 'Yes'), ('no', 'No')], 
                          validators=[DataRequired()])
    hotwaterheating = SelectField('Hot Water Heating', 
                                 choices=[('yes', 'Yes'), ('no', 'No')], 
                                 validators=[DataRequired()])
    airconditioning = SelectField('Air Conditioning', 
                                 choices=[('yes', 'Yes'), ('no', 'No')], 
                                 validators=[DataRequired()])
    prefarea = SelectField('Preferred Area', 
                          choices=[('yes', 'Yes'), ('no', 'No')], 
                          validators=[DataRequired()])
    furnishingstatus = SelectField('Furnishing Status', 
                                  choices=[
                                      ('furnished', 'Furnished'),
                                      ('semi-furnished', 'Semi-furnished'),
                                      ('unfurnished', 'Unfurnished')
                                  ], 
                                  validators=[DataRequired()])
    
    submit = SubmitField('Predict Price')
