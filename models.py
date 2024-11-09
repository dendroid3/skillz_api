from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from datetime import datetime
import pytz
from sqlalchemy_serializer import SerializerMixin

# Define East African Time timezone
EAT = pytz.timezone('Africa/Nairobi')

def get_eat_now():
    return datetime.now(EAT)

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)
db = SQLAlchemy(metadata=metadata)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100))  # To store the token for email verification
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sign_in = db.Column(db.DateTime)

    courses = db.relationship('Course', backref='user', lazy=True)
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)
    payments = db.relationship('Payment', backref='learner', lazy=True)

    def to_dict(self, include_courses=False):
        user_dict = {
            'id': self.id,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'verified': self.verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_sign_in': self.last_sign_in.isoformat() if self.last_sign_in else None,
        }

        if include_courses:
            user_dict['courses'] = [course.to_dict() for course in self.courses]

        return user_dict


class Course(db.Model, SerializerMixin):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    price = db.Column(db.DECIMAL(10, 2))
    image_url = db.Column(db.String(255)) 
    category = db.Column(db.String(100))
    created_at = db.Column(db.TIMESTAMP, default=get_eat_now)
    updated_at = db.Column(db.TIMESTAMP, default=get_eat_now, onupdate=get_eat_now)

    contents = db.relationship('CourseContent', backref='course', lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    reviews = db.relationship('Review', backref='course', lazy=True)
    payments = db.relationship('Payment', backref='course', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'instructor_id': self.instructor_id,
            'title': self.title,
            'description': self.description,
            'price': str(self.price) if self.price else None,
            'image_url': self.image_url,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'instructor': self.user.to_dict() if self.user else None,  
            'contents': [content.to_dict() for content in self.contents], 
            'reviews': [review.to_dict() for review in self.reviews]
        }



class CourseContent(db.Model, SerializerMixin):
    __tablename__ = 'coursecontent'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    content_type = db.Column(db.String(50))
    content_url = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, default=get_eat_now)
    updated_at = db.Column(db.TIMESTAMP, default=get_eat_now, onupdate=get_eat_now)

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'content_type': self.content_type,
            'content_url': self.content_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Payment(db.Model, SerializerMixin):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    learner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.DECIMAL(10, 2))
    payment_status = db.Column(db.String(50))
    payment_date = db.Column(db.TIMESTAMP, default=get_eat_now)

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'learner_id': self.learner_id,
            'amount': str(self.amount) if self.amount else None,
            'payment_status': self.payment_status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
        }

class Enrollment(db.Model, SerializerMixin):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    learner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50))
    enrolled_at = db.Column(db.TIMESTAMP, default=get_eat_now)
    completed_at = db.Column(db.TIMESTAMP)

    accolades = db.relationship('Accolade', backref='enrollment', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'learner_id': self.learner_id,
            'status': self.status,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }

class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    learner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=get_eat_now)
    updated_at = db.Column(db.TIMESTAMP, default=get_eat_now, onupdate=get_eat_now)

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'learner_id': self.learner_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Message(db.Model, SerializerMixin):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=get_eat_now)

    def __repr__(self):
        return f"<Message {self.id}: from {self.sender_id} to {self.receiver_id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
        }

class Accolade(db.Model, SerializerMixin):
    __tablename__ = 'accolades'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id'), nullable=False)
    title = db.Column(db.String(20))
    description = db.Column(db.String(100))
    awarded_at = db.Column(db.TIMESTAMP, default=get_eat_now)

    def to_dict(self):
        return {
            'id': self.id,
            'enrollment_id': self.enrollment_id,
            'title': self.title,
            'description': self.description,
            'awarded_at': self.awarded_at.isoformat() if self.awarded_at else None,
        }
