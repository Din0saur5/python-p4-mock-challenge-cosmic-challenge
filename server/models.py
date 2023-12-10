from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', back_populates='planet', cascade='all, delete-orphan')
    scientists = association_proxy('missions', 'scientist', creator = lambda s: Mission(scientist=s))
    # Add serialization rules
    serialize_rules = ('-missions.planet',)

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)

    # Add relationship
    missions = db.relationship('Mission', back_populates='scientist', cascade='all, delete-orphan')
    planets = association_proxy('missions', 'planet', creator = lambda p: Mission(planet=p))
    # Add serialization rules
    serialize_rules = ('-missions.scientist',)
    # Add validation
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError("scientist must have name")
        return name
    
    @validates('field_of_study')
    def validates(self, key, value):
        if not value:
            raise ValueError("scientist must have field of study")
        return value

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    # Add relationships
    planet = db.relationship('Planet', back_populates = 'missions')
    scientist = db.relationship('Scientist', back_populates = 'missions')
    # Add serialization rules
    serialize_rules=('-planet.missions', '-scientist.missions')
    # Add validation
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError("mission must have name")
        return name

    @validates('scientist_id')
    def validate_scientist_id(self, key, scientist_id):
        if not scientist_id:
            raise ValueError("mission must have scientist_id")
        return scientist_id
    
    @validates('planet_id')
    def validate_planet_id(self, key, planet_id):
        if not planet_id:
            raise ValueError("mission must have planet_id")
        return planet_id
# add any models you may need.
