from flask import request
# from flask_restful import Resource
from models import Enrollment, db
from flask_restx import Namespace, Resource, fields

enrollment_ns = Namespace('enrollments', description='Enrollment-related operations')

class EnrollmentResource(Resource):
    def get(self, enrollment_id=None):
        if enrollment_id:
            enrollment = Enrollment.query.get_or_404(enrollment_id)
            return enrollment.to_dict(), 200
        else:
            learner_id = request.args.get('learner_id')
            if not learner_id:
                return {'message': 'learner_id is required'}, 400
            enrollments = Enrollment.query.filter_by(learner_id=learner_id).all()
            return [enrollment.to_dict() for enrollment in enrollments], 200

    def post(self):
        data = request.get_json()
        new_enrollment = Enrollment(
            course_id=data.get('course_id'),
            learner_id=data.get('learner_id'),
            status=data.get('status')
        )
        db.session.add(new_enrollment)
        db.session.commit()
        return new_enrollment.to_dict(), 201

    def put(self, enrollment_id):
        enrollment = Enrollment.query.get_or_404(enrollment_id)
        data = request.get_json()
        enrollment.status = data.get('status', enrollment.status)
        enrollment.completed_at = data.get('completed_at', enrollment.completed_at)
        db.session.commit()
        return enrollment.to_dict(), 200

    def delete(self, enrollment_id):
        enrollment = Enrollment.query.get_or_404(enrollment_id)
        db.session.delete(enrollment)
        db.session.commit()
        return '', 204
    
enrollment_ns.add_resource(EnrollmentResource, '', '/<int:learner_id>')
