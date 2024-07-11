from flask_wtf import FlaskForm

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError
import re

def validate_contact(form, field):
        if not re.match(r'^[0-9]+$', field.data):
            raise ValidationError('Contact should contain only numbers.')


class RegisterForm(FlaskForm):

    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name")
    email = StringField("Email", validators=[DataRequired(), Email()])

    contact = StringField("Contact", validators=[DataRequired(),validate_contact])

    password = PasswordField("Password", validators=[
        
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp(r'^(?=.*[A-Z])', message='Password must contain at least one uppercase letter.'),
        Regexp(r'^(?=.*[a-z])', message='Password must contain at least one lowercase letter.'),
        Regexp(r'^(?=.*\d)', message='Password must contain at least one digit.'),
        Regexp(r'^(?=.*[!@#$%^&*(),.?":{}|<>])', message='Password must contain at least one special character.')

    ])


    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField("Submit")


class VerificationForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(), Email()])
    submit = SubmitField('Next')



class OTPForm(FlaskForm):
     otp = PasswordField("Enter OTP",validators=[DataRequired(),])
     submit = SubmitField('Submit')



class ForgetPass(FlaskForm):

        password = PasswordField("New Password", validators=[
        
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp(r'^(?=.*[A-Z])', message='Password must contain at least one uppercase letter.'),
        Regexp(r'^(?=.*[a-z])', message='Password must contain at least one lowercase letter.'),
        Regexp(r'^(?=.*\d)', message='Password must contain at least one digit.'),
        Regexp(r'^(?=.*[!@#$%^&*(),.?":{}|<>])', message='Password must contain at least one special character.')

    ])
        confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
        submit = SubmitField("Change Password")