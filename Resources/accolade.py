from flask import request, jsonify
from flask_restful import Resource
from models import Accolade, db

class AccoladeResource(Resource):
    def get(self, id):
        accolade = Accolade.query.get(id)
        if accolade is None:
            return {'message': 'Accolade not found'}, 404
        return accolade.to_dict(), 200

    def put(self, id):
        accolade = Accolade.query.get(id)
        if accolade is None:
            return {'message': 'Accolade not found'}, 404
        
        data = request.get_json()
        if 'title' in data:
            accolade.title = data['title']
        if 'description' in data:
            accolade.description = data['description']
        if 'awarded_at' in data:
            accolade.awarded_at = data['awarded_at']
        
        db.session.commit()
        return accolade.to_dict(), 200

    def delete(self, id):
        accolade = Accolade.query.get(id)
        if accolade is None:
            return {'message': 'Accolade not found'}, 404
        
        db.session.delete(accolade)
        db.session.commit()
        return {'message': 'Accolade deleted'}, 200

class AccoladeListResource(Resource):
    def get(self):
        accolades = Accolade.query.all()
        return [accolade.to_dict() for accolade in accolades], 200

    def post(self):
        data = request.get_json()
        new_accolade = Accolade(
            enrollment_id=data['enrollment_id'],
            title=data.get('title'),
            description=data.get('description'),
            awarded_at=data.get('awarded_at')
        )
        db.session.add(new_accolade)
        db.session.commit()
        return new_accolade.to_dict(), 201
