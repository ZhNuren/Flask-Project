from flask_login import LoginManager, UserMixin
from flask_sqlalchemy  import SQLAlchemy
db=  SQLAlchemy()
class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(60), primary_key=True)
    name = db.Column(db.String(30))
    surname = db.Column(db.String(40))
    phone = db.Column(db.String(20))
    salary = db.Column(db.Integer)
    password = db.Column(db.String(15))
    cname = db.Column(db.String(50))
    sex = db.Column(db.String(1))

    def get_id(self):
        return (self.email)
class Country(db.Model):
    __tablename__ = 'country'
    cname = db.Column(db.VARCHAR(50), primary_key=True)
    population = db.Column(db.BIGINT)

    def __init__(self, cname, population):
        self.cname = cname
        self.population = population


class Record(db.Model):
    __tablename__ = 'record'
    email = db.Column(db.String(50),primary_key=True)
    cname = db.Column(db.VARCHAR(50),primary_key=True)
    disease_code = db.Column(db.VARCHAR(50),primary_key=True)
    total_deaths = db.Column(db.Integer)
    total_patients = db.Column(db.Integer)

class Doctor(db.Model):
    __tablename__ = 'doctor'
    email = db.Column(db.VARCHAR(60),primary_key=True)
    degree = db.Column(db.VARCHAR(20))
class PublicServant(db.Model):
    __tablename__ = 'public_servant'
    email = db.Column(db.VARCHAR(60),primary_key=True)
    department = db.Column(db.VARCHAR(50))
class Specialize(db.Model):
    __tablename__ = 'specialize'
    email = db.Column(db.VARCHAR(60),primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
class DiseaseType(db.Model):
    __tablename__ = 'disease_type'
    id = db.Column(db.Integer,primary_key=True)
    description = db.Column(db.VARCHAR(140))
class Disease(db.Model):
    __tablename__ = 'disease'
    disease_code = db.Column(db.VARCHAR(50),primary_key=True)
    pathogen = db.Column(db.VARCHAR(20))
    description = db.Column(db.VARCHAR(140))
    id = db.Column(db.Integer)
class Discovery(db.Model):
    __tablename__ = 'discover'
    cname = db.Column(db.VARCHAR(50), primary_key=True)
    disease_code = db.Column(db.VARCHAR(50),primary_key=True)
    first_enc_date=db.Column(db.DATE)