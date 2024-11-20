from flask import request, jsonify
# from flask_restful import Resource
from models import CourseContent, db, Course, Enrollment, Grade, Answer
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload


course_contents_ns = Namespace('coursecontents', description='Course-content-related operations')

class CourseContentResource(Resource):
    @jwt_required()  # Ensure JWT is required for this endpoint
    def get(self, content_id=None):
        # Get the JWT user ID
        user_id = get_jwt_identity()

        course_id = request.args.get('course_id')

        if content_id:
            # Get a single content by ID
            content = CourseContent.query.get_or_404(content_id)
            
            # Check if the course user_id is the same as the JWT user
            course = content.course  # assuming CourseContent has a relationship with Course
            if course.user_id == user_id:
                return content.to_dict(), 200
            else:
                # Check if the user is enrolled
                enrollment = Enrollment.query.filter_by(learner_id=user_id, course_id=course_id).first()
                if not enrollment:
                    return jsonify({"msg": "You have not enrolled to the course"}), 404
                
                # User is enrolled, fetch grade for this content
                grade = Grade.query.filter_by(user_id=user_id, coursecontent_id=content.id).first()
                content_dict = content.to_dict()
                content_dict['grade'] = grade.grade if grade else None  # Add grade to the response
                
                # Fetch the user's answer to this content, if it exists
                answer = Answer.query.filter_by(user_id=grade.id, coursecontent_id=content.id).first() if grade else None
                content_dict['answer'] = answer.answer if answer else None  # Add answer to the content response

                return content_dict, 200
        
        elif course_id:
            # Get all contents associated with a specific course_id
            course = Course.query.get(course_id)
            if course.instructor_id == user_id:
                # Course belongs to the JWT user
                contents = CourseContent.query.filter_by(course_id=course_id).all()
                return [content.to_dict() for content in contents], 200
            else:
                # Check if the user is enrolled in the course
                enrollment = Enrollment.query.filter_by(learner_id=user_id, course_id=course_id).first()
                if not enrollment:
                    return jsonify({"msg": "You have not enrolled to the course"}), 404
                
                # User is enrolled, return contents with grades
                contents = CourseContent.query.filter_by(course_id=course_id).all()
                result = []
                for content in contents:
                    # Convert content to dictionary format
                    content_dict = content.to_dict()

                    # Fetch the user's grade for this content
                    grade = Grade.query.filter_by(user_id=user_id, coursecontent_id=content.id).first()
                    content_dict['grade'] = grade.grade if grade else None

                    # Fetch the user's answer for this content
                    answer = Answer.query.filter_by(coursecontent_id=content.id, user_id=user_id).first()
                    content_dict['answer'] = answer.answer if answer else None

                    # Append the updated content dictionary to the result
                    result.append(content_dict)

                
                return result, 200
        
        else:
            # Get all contents if no content_id or course_id is provided
            contents = CourseContent.query.all()
            return [content.to_dict() for content in contents], 200

    def post(self):
        data = request.get_json()
        new_content = CourseContent(
            course_id=data['course_id'],
            content_type=data['content_type'],
            content_url=data['content_url'],
            assignment=data['assignment'],
            max_grade=data['max_grade']
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

answers_ns = Namespace('answers', description='Answers-content-related operations')
class AnswerResource(Resource):
    @jwt_required()
    def post(self):
        # Get the JWT user ID
        user_id = get_jwt_identity()

        # Get the coursecontent_id and answer from the request data
        data = request.get_json()
        coursecontent_id = data.get('coursecontent_id')
        answer_text = data.get('answer')
        user_id = get_jwt_identity()
        
        if not coursecontent_id or not answer_text:
            return {"msg": "Missing coursecontent_id or answer"}, 400

        # Check if the course content exists
        content = CourseContent.query.get(coursecontent_id)
        if not content:
            return {"msg": "Course content not found"}, 404
        
        # Check if the user is enrolled in the course
        course_id = content.course_id
        enrollment = Enrollment.query.filter_by(learner_id=user_id, course_id=course_id).first()
        # if not enrollment:
        #     return {"msg": "You are not enrolled in this course"}, 403

        # Check if the user already has a grade for this content
        grade = Grade.query.filter_by(user_id=user_id, coursecontent_id=coursecontent_id).first()
        # if not grade:
        #     return {"msg": "No grade found for this content"}, 404
        
        # Create a new answer
        new_answer = Answer(coursecontent_id=coursecontent_id, answer=answer_text, user_id=user_id)
        
        # Add the answer to the database
        db.session.add(new_answer)
        db.session.commit()
        
        return {"msg": "Answer added successfully"}, 201

    def get(self, course_id):
        # Fetch all course content for the given course_id
        course_contents = CourseContent.query.filter_by(course_id=course_id).all()

        if not course_contents:
            return jsonify({"msg": "No course contents found for the given course ID"}), 404

        result = []

        for content in course_contents:
            content_dict = content.to_dict()  # Assuming `to_dict` is implemented in your model
            
            # Fetch all answers for this content
            answers = Answer.query.filter_by(coursecontent_id=content.id).options(
                joinedload(Answer.user)  # Load related user data
            ).all()
            
            # Separate answers into those with a grade and those without
            with_grade = []
            without_grade = []
            
            for answer in answers:
                answer_dict = {
                    "id": answer.id,
                    "answer": answer.answer,
                    "learner": answer.user.to_dict()  # Assuming `to_dict` is implemented in the User model
                }

                if answer.grade_id:
                    grade = Grade.query.get(answer.grade_id)
                    answer_dict["grade"] = grade.to_dict() if grade else None
                    with_grade.append(answer_dict)
                else:
                    without_grade.append(answer_dict)

            # Add organized answers to the content dict
            content_dict["answers_with_grade"] = with_grade
            content_dict["answers_without_grade"] = without_grade

            result.append(content_dict)

        return result, 200

    
answers_ns.add_resource(AnswerResource, '', '/<int:course_id>')

grade_ns = Namespace('grades', description='Grade-content-related operations')
class GradeResource(Resource):
    def post(self):
        # Get the answer_id and grade from the request
        data = request.get_json()
        answer_id = data.get('answer_id')
        grade_value = data.get('grade')

        # Check if the answer_id and grade are provided
        if not answer_id or not grade_value:
            return {"msg": "Missing answer_id or grade"}, 400

        # Fetch the answer record using the answer_id
        answer = Answer.query.get(answer_id)
        if not answer:
            return {"msg": "Answer not found"}, 404

        # Get the coursecontent_id and user_id from the answer record
        coursecontent_id = answer.coursecontent_id
        user_id = answer.user_id

        # Create a Grade record using the coursecontent_id, user_id, and the grade
        new_grade = Grade(coursecontent_id=coursecontent_id, user_id=user_id, grade=grade_value)

        # Add the Grade record to the session and commit it to the database
        db.session.add(new_grade)
        db.session.commit()

        # Update the answer record with the grade_id
        answer.grade_id = new_grade.id
        db.session.commit()

        return {"msg": "Grade added successfully", "grade_id": new_grade.id}, 201

grade_ns.add_resource(GradeResource, '', '/<int:course_id>')
