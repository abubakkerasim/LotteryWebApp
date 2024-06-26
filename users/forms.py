from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired,Email,Length,ValidationError,EqualTo
from flask_wtf import RecaptchaField
import re

#created the method to validate characters when asked for both first and last names during the registration process
def validate_characters(form, field):
    #declaring the characters that are invalid
    excluded_chars = "*?!'^+%&/()=}][{$#@<>"
    for char in field.data:
        #checking if the excluded character is in the excluded characters
        if char in excluded_chars:
            raise ValidationError("Must not contain the characters:  * ? ! ' ^ + % & / ( ) = } ] [ { $ # @ < >")

def validate_number(form, field):
   #setting the format for the specification of the number
   p = re.compile("^(1-)?\d{4}-\d{3}-\d{4}$")
   if not p.match(field.data):
       #checking if the format of the number is correct
       raise ValidationError("Must be digits of the form: XXXX-XXX-XXXX (including the dashes)")


#created the method to validate characters when asked for the password
def validate_passwordRequirments(form, field):
   p = re.compile(r"^(?=.*\W)(?=.*[a-z])(?=.*[A-Z])(?=.*\d)*")
   # checking if the excluded character is in the excluded characters
   if not p.match(field.data):
       raise ValidationError("Must contain at least 1 digit, 1 lowercase letter, 1 uppercase letter and a special character")

#class RegisterForm implements the fields in the register window
class RegisterForm(FlaskForm):
    #vailidators dont allow fields to not be empty
    email = StringField(validators=[DataRequired(), Email()])
    firstname = StringField(validators=[DataRequired(), validate_characters])
    lastname = StringField(validators=[DataRequired(), validate_characters])
    phone = StringField(validators=[DataRequired(), validate_number])
    password = PasswordField(validators=[DataRequired(), Length(min=6, max=12), validate_passwordRequirments])
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password', message="Both password fields must be equal!")])
    submit = SubmitField()

#class LoginForm implements the fields in the login window
class LoginForm(FlaskForm):
    #vailidators dont allow fields to not be empty
    username = StringField(validators= [DataRequired(), Email()])
    password = PasswordField(validators= [DataRequired()])
    recaptcha = RecaptchaField()
    pin = StringField(validators=[DataRequired()])
    submit = SubmitField()