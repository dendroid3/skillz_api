import os
from datetime import timedelta
from dotenv import load_dotenv

from flask import Flask, make_response, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message as MailMessage
from flask_migrate import Migrate
from flask_restx import Api, Namespace

import pytz

import cloudinary
import cloudinary.uploader
import cloudinary.api

from models import db, User, Message

# Define East African Time timezone
EAT = pytz.timezone('Africa/Nairobi')

load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Configurations
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///yourdatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')


print("MAIL_USERNAME:", os.getenv("MAIL_USERNAME"))

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt_manager = JWTManager(app)
mail = Mail(app)
CORS(app)

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'dx0dgxzpk'),
    api_key=os.getenv('CLOUDINARY_API_KEY', '528686173472686'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET', 'vl_n-rurd_6IJQ-TM_oC8ruukyk')
)

# Handle CORS preflight requests
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response

from Resources import auth_ns, user_ns, users_ns, message_ns, enrollment_ns, course_ns, payment_ns, course_contents_ns

# Import resources
from Resources import (
    MessageResource,
    # SignInResource,
    SignUpResource,
    SignOutResource,
    UsersInConversationResource,
    AllUsersResource,
    EditUserResource,
    UserResource,
    CourseResource,
    CourseContentResource,
    ReviewResource,
    EnrollmentResource,
    AccoladeResource, 
    AccoladeListResource,
    Verify2FAResource,
    VerifyEmailResource,
    PaymentResource
)


api = Api(
    app,
    title='Skillz',
    version='1.0',
    description='Skillz API documentation with Swagger UI',
    doc='/docs'  
)

# Define namespaces

accolade_ns = Namespace('accolades', description='Accolade-related operations')
review_ns = Namespace('reviews', description='Review-related operations')

# auth_ns.add_resource(SignOutResource, '/sign-out')


accolade_ns.add_resource(AccoladeListResource, '')
accolade_ns.add_resource(AccoladeResource, '/<int:id>')

review_ns.add_resource(ReviewResource, '', '/reviews/<int:review_id>')

# Register namespaces with the main API, ensuring no extra routes are created
api.add_namespace(auth_ns)
api.add_namespace(user_ns)
api.add_namespace(users_ns)
api.add_namespace(message_ns)
api.add_namespace(course_ns)
api.add_namespace(course_contents_ns)
api.add_namespace(enrollment_ns)
api.add_namespace(payment_ns)
api.add_namespace(accolade_ns)
api.add_namespace(review_ns)

# Create tables and run the application
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)