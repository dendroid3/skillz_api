from flask import request, jsonify
# from flask_restful import Resource
from models import CourseContent, db
from flask_restx import Namespace, Resource, fields

course_contents_ns = Namespace('coursecontents', description='Course-content-related operations')

class CourseContentResource(Resource):
    def get(self, content_id=None):
        course_id = request.args.get('course_id')

        if content_id:
            # Get a single content by ID
            content = CourseContent.query.get_or_404(content_id)
            return content.to_dict(), 200
        
        elif course_id:
            # Get all contents associated with a specific course_id
            contents = CourseContent.query.filter_by(course_id=course_id).all()
            return [content.to_dict() for content in contents], 200
        
        else:
            # Get all contents if no content_id or course_id is provided
            contents = CourseContent.query.all()
            return [content.to_dict() for content in contents], 200

        
    def post(self):
        data = request.get_json()
        new_content = CourseContent(
            course_id=data['course_id'],
            content_type=data['content_type'],
            content_url=data['content_url']
        )
        db.session.add(new_content)
        db.session.commit()
        return new_content.to_dict(), 201

    def delete(self, content_id):
        content = CourseContent.query.get_or_404(content_id)
        db.session.delete(content)
        db.session.commit()
        return {'message': 'Content deleted'}, 200
    
course_contents_ns.add_resource(CourseContentResource, '', '/<int:course_id>')
