from wtforms import Form, StringField, IntegerField
from wtforms.validators import DataRequired, Email


class AddUserForm(Form):
    userid = StringField('UserID', validators=[DataRequired()])
    username = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])


class RemoveUserForm(Form):
    userid = StringField('UserID', validators=[DataRequired()])


class AddOrRemoveTrainingForm(Form):
    userid = StringField('UserID', validators=[DataRequired()])
    machineid = IntegerField('MachineID', validators=[DataRequired()])


class LookupUserForm(Form):
    username = StringField('UserName')
    email = StringField('Email')


class AddMachineForm(Form):
    machineid = IntegerField('MachineID', validators=[DataRequired()])
    machinename = StringField('Name', validators=[DataRequired()])


class RemoveMachineForm(Form):
    machineid = IntegerField('MachineID', validators=[DataRequired()])


class SimulateCheckoutForm(Form):
    userid = StringField('UserID', validators=[DataRequired()])
    machineid = IntegerField('MachineID', validators=[DataRequired()])


class SimulateCheckinForm(Form):
    machineid = IntegerField('MachineID', validators=[DataRequired()])
