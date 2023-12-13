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

class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict(rules=('-missions',)) for scientist in Scientist.query.all()]
        return make_response(scientists,200)
    def post(self):
        data = request.get_json()
        try:
            scientist = Scientist(**data)
            db.session.add(scientist)
            db.session.commit()
            return make_response(scientist.to_dict(),201)
        except Exception as e:
            return make_response({"errors":["validation errors"]},400)
    
api.add_resource(Scientists,'/scientists')

class ScientistById(Resource):
    def get(self,id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            return make_response(scientist.to_dict(),200)
        else:
            return make_response({"error":"Scientist not found"},404)
    def patch(self,id):
        scientist = Scientist.query.filter_by(id=id).first()
        data = request.get_json()
        if scientist:
            try:
                for attr in data:
                    setattr(scientist, attr, data[attr])
                return make_response(scientist.to_dict(),202)
            except Exception as e:
                return make_response({"errors":["validation errors"]},400)
        else:
            return make_response({"error":"Scientist not found"},404)
    def delete(self, id):
        if scientist := Scientist.query.filter_by(id=id).first():
            db.session.delete(scientist)
            db.session.commit()
            return make_response({},204)
        else:
            return make_response({"error":"Scientist not found"},404)
        
api.add_resource(ScientistById,'/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(rules = ('-missions',)) for planet in Planet.query.all()]
        return make_response(planets,200)
    
api.add_resource(Planets,'/planets')

class Missions(Resource):
    def post(self):
        data = request.get_json()
        try:
            mission = Mission(**data)
            db.session.add(mission)
            db.session.commit()
            return make_response(mission.to_dict(),201)
        except Exception as e:
            return make_response({"errors":["validation errors"]},400)
api.add_resource(Missions, '/missions')

@app.route('/')
def home():
    return ''


if __name__ == '__main__':
    app.run(port=5555, debug=True)
