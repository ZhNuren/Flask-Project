
from sqlalchemy import desc, asc
from flask import Flask, render_template, redirect, url_for, request, flash, send_file
import pandas as pd
from flask_bootstrap import Bootstrap
from sqlalchemy import func
from flask_sqlalchemy  import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import *
from forms import *
from flask import Response


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_POOL_SIZE'] = 20
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 0
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nuren:nuren0525@localhost:5432/homework'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:8000/homework'
#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://Nuren:nuren0525!@Nuren.mysql.pythonanywhere-services.com/Nuren$homework"
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)



@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    else:
        return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(Users).filter_by(email=form.email.data).first()
        if user:
            if user.password==form.password.data:
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash(u'Invalid password or login!',"warning")
                return render_template('login.html', form=form)
        else:
            flash(u'No such User!',"warning")
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        user = db.session.query(Users).filter_by(email=form.email.data).first()
        if(user):
            flash(u'Such email already exists!',"warning")
            return render_template('register.html', formiscomplete=False, form=form)
        new_user = Users(email=form.email.data, name=form.name.data,sex = form.sex.data, surname=form.surname.data, password=form.password.data, phone=form.phone.data, salary=form.salary.data, cname=form.cname.data)
        db.session.add(new_user)
        db.session.commit()
        usr = db.session.query(Users).filter_by(email=form.email.data).first()
        login_user(usr)
        form1 = FinishRegisterFormDoctor()
        form2 = FinishRegisterFormServant()
        return render_template('register.html', formiscomplete=True, form1=form1, form2=form2)


    return render_template('register.html', formiscomplete=False, form=form, data=Country.query.all())

@app.route('/finishregisterdoctor',methods=['GET', 'POST'])
@login_required
def finishregisterdoctor():

    form = FinishRegisterFormDoctor()
    degree=form.degree.data
    specs = form.specs.data
    new_user = Doctor(email=current_user.email, degree=degree)
    db.session.add(new_user)
    db.session.commit()
    for s in specs:
        new_spec = Specialize(email=current_user.email, id=s)
        db.session.add(new_spec)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/finishregisterservant',methods=['GET', 'POST'])
@login_required
def finishregisterservant():
    form = FinishRegisterFormServant()

    department=form.department.data
    new_user = PublicServant(email=current_user.email, department=department)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/doctors',methods=['GET', 'POST'])
@login_required
def doctors():
    doc = False
    ser = False
    doctor = db.session.query(Doctor).filter_by(email=current_user.email).first()
    servant = db.session.query(PublicServant).filter_by(email=current_user.email).first()
    if doctor is not None:
        doc = True
        ser = False
        cur_spec = db.session.query(Specialize).filter_by(email=current_user.email).all()
        spec_id = []
        for i in cur_spec:
            spec_id.append(i.id)
        spec_name = []
        for i in spec_id:
             spec_name.append(db.session.query(DiseaseType).filter_by(id=i).first().description)
        specs = db.session.query(Specialize).filter(Specialize.id.in_(spec_id),Specialize.email!=current_user.email).all()
        same_specs = set()
        for i in specs:
            same_specs.add(i.email)
        query = db.session.query(Doctor).filter(Doctor.email!=current_user.email).all()
        cur_deg = db.session.query(Doctor).filter_by(email = current_user.email).first().degree
        same_deg = db.session.query(Doctor).filter(Doctor.email!=current_user.email, Doctor.degree==cur_deg).all()
        return render_template('all_doctors.html',spec_name = spec_name, servantcheck = ser, doctorcheck=doc, same_deg = same_deg, doc = Doctor, same_specs = same_specs, name=current_user.name, query=query, doctor = Users, specs = Specialize, disid = DiseaseType)
    if servant is not None:
        cur_dept = db.session.query(PublicServant).filter_by(email=current_user.email).first().department
        doc=False
        ser = True
        return render_template('all_doctors.html',cur_dept = cur_dept, name=current_user.name,servantcheck = ser, doctorcheck=doc, query =  db.session.query(Doctor).all(),doctor = Users)
    return render_template('all_doctors.html', name=current_user.name,servantcheck = ser, doctorcheck=doc, query = db.session.query(Doctor).all(),doctor = Users)


@app.route('/servants',methods=['GET', 'POST'])
@login_required
def servants():
    doc = False
    ser = False
    doctor = db.session.query(Doctor).filter_by(email=current_user.email).first()
    servant = db.session.query(PublicServant).filter_by(email=current_user.email).first()
    allservants = db.session.query(Users,PublicServant).filter(PublicServant.email==Users.email).all()
    if doctor is not None:
        doc = True
        ser = False
        cur_spec = db.session.query(Specialize).filter_by(email=current_user.email).all()
        spec_id = []
        for i in cur_spec:
            spec_id.append(i.id)
        spec_name = []
        for i in spec_id:
             spec_name.append(db.session.query(DiseaseType).filter_by(id=i).first().description)
        return render_template('all_servants.html', allservants = allservants, spec_name = spec_name, servantcheck = ser, doctorcheck=doc, doc = Doctor, name=current_user.name, doctor = Users, specs = Specialize, disid = DiseaseType)
    if servant is not None:
        cur_dept = db.session.query(PublicServant).filter_by(email=current_user.email).first().department
        doc=False
        ser = True
        allservants = db.session.query(Users,PublicServant).filter(PublicServant.email==Users.email, Users.email!=current_user.email).all()
        samedept = db.session.query(Users,PublicServant).filter(PublicServant.email==Users.email, PublicServant.department==cur_dept, Users.email!=current_user.email).all()
        return render_template('all_servants.html',allservants = allservants, samedept = samedept, cur_dept = cur_dept, name=current_user.name,servantcheck = ser, doctorcheck=doc, query = Doctor.query.all(),doctor = Users)
    return render_template('all_servants.html',allservants = allservants, name=current_user.name,servantcheck = ser, doctorcheck=doc, query = Doctor.query.all(),doctor = Users)


@app.route('/records',methods=['GET', 'POST'])
@login_required
def records():
    doc = False
    ser = False
    doctor = db.session.query(Doctor).filter_by(email=current_user.email).first()
    servant = db.session.query(PublicServant).filter_by(email=current_user.email).first()
    allrecords = db.session.query(Record).all()
    groupdiscode = db.session.query(Record.disease_code,func.sum(Record.total_patients).label('totalpat'),func.sum(Record.total_deaths).label('totaldes')).group_by(Record.disease_code).all()
    groupcname = db.session.query(Record.cname,func.sum(Record.total_patients).label('totalpat'),func.sum(Record.total_deaths).label('totaldes')).group_by(Record.cname).all()
    if doctor is not None:
        doc = True
        ser = False
        cur_spec = db.session.query(Specialize).filter_by(email=current_user.email).all()
        spec_id = []
        for i in cur_spec:
            spec_id.append(i.id)
        spec_name = []
        for i in spec_id:
             spec_name.append(db.session.query(DiseaseType).filter_by(id=i).first().description)
        return render_template('all_records.html',groupdiscode=groupdiscode, groupcname = groupcname, editmode = False, allrecords=allrecords, spec_name = spec_name, servantcheck = ser, doctorcheck=doc, doc = Doctor, name=current_user.name)
    if servant is not None:
        cur_dept = db.session.query(PublicServant).filter_by(email=current_user.email).first().department
        doc=False
        ser = True
        form = RecordForm()
        form.email.data = current_user.email
        myrecords = db.session.query(Record).filter_by(email=current_user.email).all()
        return render_template('all_records.html',groupdiscode=groupdiscode,groupcname = groupcname, editmode = False, form=form, myrecords=myrecords, allrecords=allrecords, cur_dept = cur_dept, name=current_user.name,servantcheck = ser, doctorcheck=doc,)
    return render_template('all_records.html',groupdiscode=groupdiscode,groupcname = groupcname, editmode = False, allrecords=allrecords, name=current_user.name,servantcheck = ser, doctorcheck=doc)


@app.route('/diseases',methods=['GET', 'POST'])
@login_required
def diseases():
    doc = False
    ser = False
    doctor = db.session.query(Doctor).filter_by(email=current_user.email).first()
    servant = db.session.query(PublicServant).filter_by(email=current_user.email).first()
    diseasesquery = db.session.query(Disease.disease_code, Disease.pathogen, Disease.description, DiseaseType.description.label('dtype')).join(DiseaseType, Disease.id == DiseaseType.id).subquery()
    diseases = db.session.query(diseasesquery).all()
    discovery = db.session.query(Discovery).order_by(desc(Discovery.first_enc_date)).all()
    if doctor is not None:
        doc = True
        ser = False
        form = DiseaseForm()
        form1 = DiscoveryForm()
        cur_spec = db.session.query(Specialize).filter_by(email=current_user.email).all()
        spec_id = []
        for i in cur_spec:
            spec_id.append(i.id)
        spec_name = []
        for i in spec_id:
             spec_name.append(db.session.query(DiseaseType).filter_by(id=i).first().description)
        specialized = []
        for n in spec_name:
             for q in db.session.query(diseasesquery).filter_by(dtype = n).all():
                 specialized.append(q)

        return render_template('all_diseases.html',discovery = discovery, editmode = False, form1 = form1, form=form, specialized = specialized, diseases = diseases,spec_name = spec_name, servantcheck = ser, doctorcheck=doc, doc = Doctor, name=current_user.name, doctor = Users, specs = Specialize, disid = DiseaseType)
    if servant is not None:
        cur_dept = db.session.query(PublicServant).filter_by(email=current_user.email).first().department
        doc=False
        ser = True
        return render_template('all_diseases.html',discovery = discovery,editmode = False, cur_dept = cur_dept, diseases = diseases, name=current_user.name,servantcheck = ser, doctorcheck=doc, query = Doctor.query.all(),doctor = Users)

    return render_template('all_diseases.html', discovery = discovery, editmode = False, diseases = diseases, name=current_user.name,servantcheck = ser, doctorcheck=doc, query = Doctor.query.all(),doctor = Users)


@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if(current_user.email != 'moderator@gmail.com'):
         flash(u'You are not Moderator', "warning")
         return redirect(url_for('dashboard'))
    users = db.session.query(Users).filter(Users.email != current_user.email).order_by(asc(Users.email)).all()
    return render_template('all_users.html', moderator = True, name = current_user.name, users = users)

@app.route('/users/delete/<email>', methods=['GET', 'POST'])
@login_required
def deleteuser(email):
    if(current_user.email != 'moderator@gmail.com'):
         flash(u'You are not Moderator', "warning")
         return redirect(url_for('dashboard'))
    user = db.session.query(Users).filter_by(email=email).first()
    db.session.delete(user)
    db.session.commit()
    flash(u'The user successfully deleted', "success")
    return redirect(url_for('users'))

@app.route('/diseases/delete/<disease_code>', methods=['GET', 'POST'])
@login_required
def deletedisease(disease_code):
    if(current_user.email != 'moderator@gmail.com'):
         flash(u'You are not Moderator', "warning")
         return redirect(url_for('dashboard'))
    dist = db.session.query(Disease).filter_by(disease_code=disease_code).first()
    db.session.delete(dist)
    db.session.commit()
    flash(u'The disease successfully deleted', "success")
    return redirect(url_for('disease_type'))

@app.route('/diseasetype/delete/<id>', methods=['GET', 'POST'])
@login_required
def deletediseasetype(id):
    if(current_user.email != 'moderator@gmail.com'):
         flash(u'You are not Moderator', "warning")
         return redirect(url_for('dashboard'))
    dist = db.session.query(DiseaseType).filter_by(id=id).first()
    db.session.delete(dist)
    db.session.commit()
    flash(u'The disease type successfully deleted', "success")
    return redirect(url_for('disease_type'))

@app.route('/diseasetype/edit/<id>', methods=['GET', 'POST'])
@login_required
def editdiseasetype(id):
    if(current_user.email != 'moderator@gmail.com'):
         flash(u'You are not Moderator', "warning")
         return redirect(url_for('dashboard'))
    dist = db.session.query(DiseaseType).filter_by(id=id).first()
    editform = DiseaseTypeForm()
    editform.id.data = dist.id
    editform.description.data = dist.description
    diseasesquery = db.session.query(Disease.disease_code, Disease.pathogen, Disease.description, DiseaseType.description.label('dtype')).join(DiseaseType, Disease.id == DiseaseType.id).subquery()
    diseases = db.session.query(diseasesquery).all()
    diseasetypes = db.session.query(DiseaseType).all()
    form = DiseaseTypeForm()
    return render_template('moderator_disease.html',editmode = True, editform = editform, diseases = diseases, form = form, moderator = True,name = current_user.name, diseasetype = diseasetypes)


@app.route('/updatediseasetype', methods=['GET', 'POST'])
@login_required
def updatediseasetype():
    form = DiseaseTypeForm()
    exist = db.session.query(DiseaseType).all()
    for a in exist:
        if (a.description == form.description.data):
            flash(u'Such disease type already exists', "warning")
            return redirect(url_for('disease_type'))
    dist = db.session.query(DiseaseType).filter_by(id=form.id.data).first()
    dist.id = form.id.data
    dist.description = form.description.data
    db.session.commit()
    flash(u'Disease type was sucessfully updated', "success")
    return redirect(url_for('disease_type'))

@app.route('/countries/delete/<cname>', methods=['GET', 'POST'])
@login_required
def deletecountry(cname):
    if(current_user.email != 'moderator@gmail.com'):
         flash(u'You are not Moderator', "warning")
         return redirect(url_for('dashboard'))
    country = db.session.query(Country).filter_by(cname=cname).first()
    db.session.delete(country)
    db.session.commit()
    flash(u'The country successfully deleted', "success")
    return redirect(url_for('countries'))

@app.route('/countries/edit/<cname>', methods=['GET', 'POST'])
@login_required
def editcountry(cname):
    if(current_user.email != 'moderator@gmail.com'):
         flash(u'You are not Moderator', "warning")
         return redirect(url_for('dashboard'))
    ctr = db.session.query(Country).filter_by(cname=cname).first()
    editform = CountryForm()
    editform.cname.data = ctr.cname
    editform.population.data = ctr.population
    countries = db.session.query(Country).order_by(desc(Country.population)).all()
    form = CountryForm()
    return render_template('all_countries.html',editmode = True, moderator = True, editform = editform, form=form, name=current_user.name, country = countries)

@app.route('/countries', methods=['GET', 'POST'])
@login_required
def countries():
    if(current_user.email != 'moderator@gmail.com'):
         flash(u'You are not Moderator', "warning")
         return redirect(url_for('dashboard'))
    countries = db.session.query(Country).order_by(desc(Country.population)).all()
    form = CountryForm()
    return render_template('all_countries.html',editmode = False, form = form, moderator = True,name = current_user.name, country = countries)

@app.route('/updatecountry', methods=['GET', 'POST'])
@login_required
def updatecountry():
    form = CountryForm()
    country = db.session.query(Country).filter_by(cname=form.cname.data).first()
    country.cname = form.cname.data
    country.population = form.population.data
    db.session.commit()
    flash(u'Country was sucessfully updated', "success")
    return redirect(url_for('countries'))


@app.route('/add_country', methods=['GET', 'POST'])
@login_required
def add_country():
    if(current_user.email != 'moderator@gmail.com'):
         flash(u'You are not Moderator', "warning")
         return redirect(url_for('dashboard'))
    form = CountryForm()
    existcountry = db.session.query(Country).filter_by(cname=form.cname.data).first()
    if existcountry:
        flash(u'Such country already exists!',"warning")
        return redirect(url_for('countries'))
    country = Country(cname=form.cname.data, population=form.population.data)
    db.session.add(country)
    db.session.commit()
    flash(u'New country sucessfully added', "success")

    return redirect(url_for('countries'))

@app.route('/add_diseasetype', methods=['GET', 'POST'])
@login_required
def add_dist():
    if(current_user.email != 'moderator@gmail.com'):
         flash(u'You are not Moderator', "warning")
         return redirect(url_for('dashboard'))
    form = DiseaseTypeForm()
    existdist = db.session.query(DiseaseType).filter_by(description=form.description.data).first()
    if existdist:
        flash(u'Such disease type already exists!',"warning")
        return redirect(url_for('disease_type'))
    dist = DiseaseType(description=form.description.data)
    db.session.add(dist)
    db.session.commit()
    flash(u'New disease type sucessfully added', "success")

    return redirect(url_for('disease_type'))



@app.route('/disease_type', methods=['GET', 'POST'])
@login_required
def disease_type():
    if(current_user.email != 'moderator@gmail.com'):
         flash(u'You are not Moderator', "warning")
         return redirect(url_for('dashboard'))
    diseasesquery = db.session.query(Disease.disease_code, Disease.pathogen, Disease.description, DiseaseType.description.label('dtype')).join(DiseaseType, Disease.id == DiseaseType.id).subquery()
    diseases = db.session.query(diseasesquery).all()
    diseasetypes = db.session.query(DiseaseType).all()
    form = DiseaseTypeForm()
    return render_template('moderator_disease.html',diseases = diseases, form = form, moderator = True,name = current_user.name, diseasetype = diseasetypes)


@app.route('/dashboard')
@login_required
def dashboard():
    if(current_user.email == 'moderator@gmail.com'):
        return render_template('template.html', moderator = True, name=current_user.name)

    updateProfile=RegisterForm()
    updateProfile.email.data=current_user.email
    updateProfile.cname.data=current_user.cname
    updateProfile.phone.data=current_user.phone
    updateProfile.salary.data=current_user.salary
    updateProfile.password.data=current_user.password
    updateProfile.name.data=current_user.name
    updateProfile.surname.data=current_user.surname
    updateProfile.sex.data=current_user.sex
    doc = False
    ser = False
    doctor = db.session.query(Doctor).filter_by(email=current_user.email).first()
    servant = db.session.query(PublicServant).filter_by(email=current_user.email).first()
    if doctor is not None:
        doc = True
        ser = False
        cur_spec = db.session.query(Specialize).filter_by(email=current_user.email).all()
        degree = db.session.query(Doctor).filter_by(email=current_user.email).first().degree
        spec_id = []
        for i in cur_spec:
            spec_id.append(i.id)
        spec_name = []
        for i in spec_id:
             spec_name.append(db.session.query(DiseaseType).filter_by(id=i).first().description)
        return render_template('template.html',moderator = False, degree = degree,servantcheck = ser, form = updateProfile, spec_name = spec_name, doctorcheck=doc, name=current_user.name)
    if servant is not None:
        cur_dept = db.session.query(PublicServant).filter_by(email=current_user.email).first().department
        doc = False
        ser = True
        return render_template('template.html',moderator = False, cur_dept =cur_dept, form=updateProfile, servantcheck =ser, doctorcheck=doc, name=current_user.name)
    return render_template('template.html', moderator = False, form=updateProfile, servantcheck =ser, doctorcheck=doc, name=current_user.name)



@app.route('/add_disease',methods=['GET', 'POST'])
@login_required
def add_disease():
    form = DiseaseForm()
    existdisease = db.session.query(Disease).filter_by(disease_code=form.disease_code.data).first()
    if existdisease:
        flash(u'Such disease already exists!',"warning")
        return redirect(url_for('diseases'))
    dis = Disease(disease_code=form.disease_code.data, pathogen=form.pathogen.data, description=form.description.data, id=form.id.data)
    db.session.add(dis)
    db.session.commit()
    flash(u'New disease sucessfully added', "success")

    return redirect(url_for('diseases'))

@app.route('/diseases/edit/<disease_code>',methods=['GET', 'POST'])
@login_required
def editdisease(disease_code):
    disease = db.session.query(Disease).filter_by(disease_code=disease_code).first()
    editform = DiseaseForm()
    editform.disease_code.data = disease.disease_code
    editform.pathogen.data = disease.pathogen
    editform.description.data = disease.description
    editform.id.data = disease.id
    doc = True
    ser = False
    diseasesquery = db.session.query(Disease.disease_code, Disease.pathogen, Disease.description, DiseaseType.description.label('dtype')).join(DiseaseType, Disease.id == DiseaseType.id).subquery()
    diseases = db.session.query(diseasesquery).all()
    form = DiseaseForm()
    form1 = DiscoveryForm()
    cur_spec = db.session.query(Specialize).filter_by(email=current_user.email).all()
    spec_id = []
    for i in cur_spec:
        spec_id.append(i.id)
    spec_name = []
    for i in spec_id:
        spec_name.append(db.session.query(DiseaseType).filter_by(id=i).first().description)
    specialized = []
    for n in spec_name:
        for q in db.session.query(diseasesquery).filter_by(dtype = n).all():
            specialized.append(q)
    return render_template('all_diseases.html',editmode = True, editform = editform, form1 = form1, form=form, specialized = specialized, diseases = diseases,spec_name = spec_name, servantcheck = ser, doctorcheck=doc, doc = Doctor, name=current_user.name, doctor = Users, specs = Specialize, disid = DiseaseType)

@app.route('/records/edit/<cname>/<disease_code>',methods=['GET', 'POST'])
@login_required
def editrecord(cname, disease_code):
    record = db.session.query(Record).filter_by(email = current_user.email, cname=cname, disease_code=disease_code).first()
    editform = RecordForm()
    editform.email.data = record.email
    editform.cname.data = record.cname
    editform.disease_code.data = record.disease_code
    editform.total_deaths.data = record.total_deaths
    editform.total_patients.data = record.total_patients
    doc = False
    ser = True
    records = db.session.query(Record).all()
    myrecords = db.session.query(Record).filter_by(email=current_user.email).all()
    cur_dept = db.session.query(PublicServant).filter_by(email=current_user.email).first().department

    form = RecordForm()
    return render_template('all_records.html',editform=editform, editmode = True, form=form, myrecords=myrecords, allrecords=records, cur_dept = cur_dept, name=current_user.name,servantcheck = ser, doctorcheck=doc)


@app.route('/updatedisease', methods=['GET', 'POST'])
@login_required
def updatedisease():
    form = DiseaseForm()
    dis = db.session.query(Disease).filter_by(disease_code=form.disease_code.data).first()
    dis.pathogen = form.pathogen.data
    dis.description = form.description.data
    dis.id = form.id.data
    db.session.commit()
    flash(u'Disease was sucessfully updated', "success")
    return redirect(url_for('diseases'))

@app.route('/updaterecord', methods=['GET', 'POST'])
@login_required
def updaterecord():
    form = RecordForm()
    if(form.total_deaths.data>form.total_patients.data):
        flash(u'Number of Deaths cannot be greater than Number of Patients', "warning")
        return redirect(url_for('records'))
    record = db.session.query(Record).filter_by(email=form.email.data,cname=form.cname.data, disease_code=form.disease_code.data).first()
    record.total_deaths = form.total_deaths.data
    record.total_patients = form.total_patients.data
    db.session.commit()
    flash(u'Record was sucessfully updated', "success")
    return redirect(url_for('records'))

def to_dict(row):
    if row is None:
        return None

    rtn_dict = dict()
    keys = row.__table__.columns.keys()
    for key in keys:
        rtn_dict[key] = getattr(row, key)
    return rtn_dict


@app.route('/excel', methods=['GET', 'POST'])
def exportexcel():
    data = db.session.query(Record).all()
    data_list = [to_dict(item) for item in data]
    df = pd.DataFrame(data_list)
    filename = "report.xlsx"
    writer = pd.ExcelWriter(filename)
    df.to_excel(writer, sheet_name='Records')
    writer.save()
    with open("/home/Nuren/" + "report.xlsx", "rb") as excel:
        data = excel.read()
    headers = {
        'Content-Disposition': 'attachment; filename="{}"'.format(filename)
    }
    response = Response(data,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        direct_passthrough=True,
                        headers=headers)
    return response

@app.route('/add_discovery',methods=['GET', 'POST'])
@login_required
def add_discovery():
    form = DiscoveryForm()
    discoverexist = db.session.query(Discovery).filter_by(cname=form.cname.data, disease_code=form.disease_code.data).first()
    if discoverexist:
        flash(u'Such discovery already exists!',"warning")
        return redirect(url_for('diseases'))
    discovery = Discovery(disease_code=form.disease_code.data, cname=form.cname.data, first_enc_date=form.first_enc_date.data)
    db.session.add(discovery)
    db.session.commit()
    flash(u'New discovery sucessfully added', "success")

    return redirect(url_for('diseases'))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'Successfully Logged Out!', 'success')
    return render_template('main.html')




@app.route('/updateprofile', methods=['GET', 'POST'])
@login_required
def updateprofile():
    form=RegisterForm()
    t=db.session.query(Users).filter_by(email=current_user.email).first()
    t.cname=form.cname.data
    t.surname = form.surname.data
    t.name = form.name.data
    t.phone = form.phone.data
    t.sex = form.sex.data
    db.session.commit()
    flash(u'Your profile sucessfully saved', "success")
    return redirect(url_for('dashboard'))

@app.route('/records/delete/<cname>/<disease_code>', methods=['GET', 'POST'])
@login_required
def deleterecord(cname, disease_code):
    record = db.session.query(Record).filter_by(email=current_user.email, cname=cname,
                                           disease_code=disease_code).first()
    db.session.delete(record)
    db.session.commit()
    flash(u'The record successfully deleted', "success")
    return redirect(url_for('records'))

@app.route('/discovery/delete/<disease_code>/<cname>', methods=['GET', 'POST'])
@login_required
def deletediscovery(cname, disease_code):
    discovery = db.session.query(Discovery).filter_by(cname=cname,
                                           disease_code=disease_code).first()
    db.session.delete(discovery)
    db.session.commit()
    flash(u'The discovery successfully deleted', "success")
    return redirect(url_for('diseases'))

@app.route('/deleteaccount/<email>', methods=['GET', 'POST'])
@login_required
def deleteaccount(email):
    logout_user()
    delete = db.session.query(Users).filter_by(email=email).first()
    db.session.delete(delete)
    db.session.commit()
    flash(u'Your account successfully deleted', "success")
    return render_template('main.html')


@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    form=RecordForm()
    existrecord = db.session.query(Record).filter_by(email=form.email.data,cname=form.cname.data,disease_code=form.disease_code.data).first()
    if existrecord:
        flash(u'Such record already exists', "warning")
        return redirect(url_for('records'))
    if(form.total_deaths.data>form.total_patients.data):
        flash(u'Number of Deaths cannot be greater than Number of Patients', "warning")
        return redirect(url_for('records'))

    record=Record(email=form.email.data,total_deaths=form.total_deaths.data,total_patients=form.total_patients.data,cname=form.cname.data,disease_code=form.disease_code.data)
    db.session.add(record)
    db.session.commit()
    flash(u'The record successfully added', "success")
    return redirect(url_for('records'))





if __name__ == '__main__':
    app.run(debug=True)