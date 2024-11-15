from flask import request, jsonify
# from flask_restful import Resource
from models import Review, db
from flask_restx import Namespace, Resource


review_ns = Namespace('reviews', description='Review-related operations')


class ReviewResource(Resource):
    def get(self, review_id=None):
        if review_id:
            # Get a single review by ID
            review = Review.query.get_or_404(review_id)
            return review.to_dict(), 200
        else:
            # Get all reviews
            reviews = Review.query.all()
            return [review.to_dict() for review in reviews], 200

    def post(self):
        data = request.get_json()
        new_review = Review(
            course_id=data['course_id'],
            learner_id=data['learner_id'],
            rating=data['rating'],
            comment=data.get('comment')  
        )
        db.session.add(new_review)
        db.session.commit()
        return new_review.to_dict(), 201

    def delete(self, review_id):
        review = Review.query.get_or_404(review_id)
        db.session.delete(review)
        db.session.commit()
        return {'message': 'Review deleted'}, 200


review_ns.add_resource(ReviewResource, '', '/reviews/<int:review_id>')
