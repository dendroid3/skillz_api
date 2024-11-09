from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from models import Course, Enrollment, db
import cloudinary
import cloudinary.uploader

course_ns = Namespace('courses', description='Course-related operations')

class CourseResource(Resource):
    def get(self, course_id=None):
        if course_id:
            course = Course.query.get_or_404(course_id)
            return course.to_dict(), 200
        else:
            instructor_id = request.args.get('instructor_id')
            learner_id = request.args.get('learner_id')
            if instructor_id:
                courses = Course.query.filter_by(instructor_id=instructor_id).all()
                return [course.to_dict() for course in courses], 200
            elif learner_id:
                enrollments = Enrollment.query.filter_by(learner_id=learner_id).all()
                course_ids = [enrollment.course_id for enrollment in enrollments]
                courses = Course.query.filter(Course.id.in_(course_ids)).all()
                return [course.to_dict() for course in courses], 200
            else:
                courses = Course.query.all()
                return [course.to_dict() for course in courses], 200

    def post(self):
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        instructor_id = request.form.get('instructor_id')
        category = request.form.get('category')
        image_file = request.files.get('file')

        # Validate input data
        if not all([title, description, price, instructor_id]):
            return {'message': 'Missing required fields'}, 400

        image_url = None
        if image_file:
            try:
                upload_result = cloudinary.uploader.upload(image_file)
                image_url = upload_result.get('secure_url')
                print(f'Image uploaded: {image_url}')
            except Exception as e:
                return {'message': f'Error uploading image: {str(e)}'}, 500

        new_course = Course(
            instructor_id=instructor_id,
            title=title,
            description=description,
            price=price,
            image_url=image_url,
            category=category
        )

        try:
            db.session.add(new_course)
            db.session.commit()
            print(f'Course saved with image_url: {image_url}')
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error saving course: {str(e)}'}, 500

        return new_course.to_dict(), 201

    def delete(self, course_id):
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        return {'message': 'Course deleted'}, 200

course_ns.add_resource(CourseResource, '', '/<int:course_id>')
