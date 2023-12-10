#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class AllScientists(Resource):
    
    def get(self):
        scientists = Scientist.query.all()
        rb= [s.to_dict(rules=('-missions',)) for s in scientists]
        return make_response(rb, 200)    
        
    def post(self):
        try:
            new_s = Scientist(
                name = request.json.get('name'),
                field_of_study = request.json.get('field_of_study')
            )
            db.session.add(new_s)
            db.session.commit()
            rb = new_s.to_dict(rules=('-missions',))
            return make_response(rb,201)
        except ValueError:
            rb = {
                "errors": ["validation errors"]
                }
            return make_response(rb, 400)
        
class ScientistByID(Resource):
    def get(self, id):
        s = Scientist.query.filter(Scientist.id == id ).first()
        
        if s:
            rb = s.to_dict()
            return make_response(rb, 200)
        else:
            rb = {
            "error": "Scientist not found"
            }
            return make_response(rb,404)
    def patch(self,id):
        s = Scientist.query.filter(Scientist.id == id ).first()
        if s:
            try:
                for attr in request.json:
                    setattr(s, attr, request.json.get(attr))
                    db.session.commit()
                    rb = s.to_dict(rules=("-missions",))
                return make_response(rb, 202)
            except ValueError:
                rb = {
                "errors": ["validation errors"]
                }
                return make_response(rb, 400)
        else:
            rb ={
            "error": "Scientist not found"
            }
            return make_response(rb, 404)
        
    def delete(self, id):
        s = Scientist.query.filter(Scientist.id == id ).first()
        if s:
            db.session.delete(s)
            db.session.commit()
            return make_response({},204)
        
        else:
            rb ={
            "error": "Scientist not found"
            }
            return make_response(rb, 404)

class AllPlanets(Resource):
    def get(self):
        planets = Planet.query.all()
        rb= [s.to_dict(rules=('-missions',)) for s in planets]
        return make_response(rb, 200) 

class AllMissions(Resource):
    
    def get(self):
        missions = Mission.query.all()
        rb= [s.to_dict(rules=('-missions',)) for s in missions]
        return make_response(rb, 200) 

    def post(self):
        try:
            # Ensure required fields are present in the request
            name = request.json.get('name')
            scientist_id = request.json.get('scientist_id')
            planet_id = request.json.get('planet_id')

            if not all([name, scientist_id, planet_id]):
                raise ValueError("Missing required fields")

            new_m = Mission(
                name=name,
                scientist_id=scientist_id,
                planet_id=planet_id,
            )
            db.session.add(new_m)
            db.session.commit()

            # Assuming to_dict() method is defined in your Mission model
            rb = new_m.to_dict()
            return make_response(rb, 201)

        except ValueError:
            rb = {
                "errors": ["validation errors"]
                }
            return make_response(rb, 400)

api.add_resource(AllMissions, '/missions')       
api.add_resource(AllPlanets, '/planets')        
api.add_resource(ScientistByID, '/scientists/<int:id>')
api.add_resource(AllScientists, '/scientists')





























@app.route('/')
def home():
    return ''


if __name__ == '__main__':
    app.run(port=5001, debug=True)
