from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateField, SelectField, widgets,SelectMultipleField
from wtforms import validators
from wtforms.validators import InputRequired, Email, Length, ValidationError
from models import *
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[InputRequired(), Email(message='Invalid email'), Length(min=4, max=60)])
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=4, max=15)])

class RegisterForm(FlaskForm):
    email = StringField('Email:', validators=[InputRequired(), Email(message='Invalid email'), Length(min=4,max=60)])
    name = StringField('Name:', validators=[InputRequired(), Length(min=4, max=30)])
    surname = StringField('Surname:', validators=[InputRequired(), Length(min=4, max=40)])
    phone = StringField('Phone:', validators=[InputRequired(), Length(min=4, max=20)])
    salary = IntegerField('Salary:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=4, max=15)])
    cname = SelectField('Country:')
    sex = SelectField('Gender:')
    def __init__(self):
        super(RegisterForm, self).__init__()
        self.cname.choices = [(c.cname) for c in db.session.query(Country).all()]
        self.sex.choices = ["","M", "F"]

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class FinishRegisterFormDoctor(FlaskForm):
    degree = StringField('Degree:', validators=[InputRequired(), Length(min=1, max=20)])
    specs = MultiCheckboxField('Specialization:', validators=[InputRequired()])
    def __init__(self):
        super(FinishRegisterFormDoctor, self).__init__()
        self.specs.choices = [(c.id, c.description) for c in db.session.query(DiseaseType).all()]

class FinishRegisterFormServant(FlaskForm):
    department = StringField('Department:', validators=[InputRequired(), Length(min=2, max=50)])
class RecordForm(FlaskForm):

    email = StringField('Email:', validators=[InputRequired(), Email(message='Invalid email'), Length(min=4, max=60)])
    disease_code = SelectField('Disease code:', validators=[validators.Optional()])
    total_deaths = IntegerField('Total deaths:', validators=[InputRequired()])
    total_patients = IntegerField('Total patients:', validators=[InputRequired()])
    cname = SelectField('Country:',validators=[validators.Optional()])
    def __init__(self):
        super(RecordForm, self).__init__()
        self.cname.choices = [(c.cname) for c in db.session.query(Country).all()]
        self.disease_code.choices = [(c.disease_code) for c in db.session.query(Disease).all()]

class DiscoveryForm(FlaskForm):
    disease_code = SelectField('Disease code:')
    first_enc_date = DateField('First discovered date:', format='%Y-%m-%d', render_kw={'placeholder': '2000-05-05 for May 5, 2000'}, validators=[InputRequired()])
    cname = SelectField('Country:')
    def __init__(self):
        super(DiscoveryForm, self).__init__()
        self.cname.choices = [(c.cname) for c in db.session.query(Country).all()]
        cur_spec = db.session.query(Specialize).filter_by(email=current_user.email).all()
        spec_id = []
        for i in cur_spec:
            spec_id.append(i.id)
        self.disease_code.choices = [(c.disease_code) for c in db.session.query(Disease).filter(Disease.id.in_(spec_id)).all()]




class DiseaseTypeForm(FlaskForm):
    id = IntegerField('id', validators=[InputRequired()])
    description = StringField('Description:', validators=[InputRequired(), Length(min=2, max=140)])

class CountryForm(FlaskForm):
    cname = StringField('Country Name: ', validators=[InputRequired()])
    population = IntegerField('Population:', validators=[InputRequired(), Length(min=2, max=140)])

class DiseaseForm(FlaskForm):
    disease_code = StringField('Disease code:', validators=[InputRequired(), Length(min=2, max=50)])
    pathogen = StringField('Pathogen:', validators=[InputRequired(), Length(min=2, max=20)])
    description = StringField('Description:', validators=[InputRequired(), Length(min=2, max=140)])
    id = SelectField('Disease type')
    def __init__(self):
        super(DiseaseForm, self).__init__()
        cur_spec = db.session.query(Specialize).filter_by(email=current_user.email).all()
        spec_id = []
        for i in cur_spec:
            spec_id.append(i.id)
        self.id.choices = [(c.id, c.description) for c in db.session.query(DiseaseType).filter(DiseaseType.id.in_(spec_id)).all()]