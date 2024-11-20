from flask import request, jsonify, current_app, Response
# from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, Message, db
from datetime import datetime, timedelta
from flask_restx import Namespace, Resource, fields
import json
import cloudinary.uploader
import uuid

import smtplib

import random
import string

from flask_mail import Message as MailMessage

otp_store = {}

auth_ns = Namespace('auth', description='Authentication-related operations')
user_ns = Namespace('user', description='User-related operations')
users_ns = Namespace('users', description='Users-related operations')


# Utility functions
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_email(to_email, subject, content):

    # Create the email message
    msg = MailMessage(subject=subject, recipients=[to_email], body=content)
    try:
        print("The /test route was accessed!")
        print(f"2FA Email Body: {content}")
        mail = current_app.extensions['mail']
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
  
class SignUpResource(Resource):
    #    # Define the request payload schema for SignUp
    auth_sign_up_params_model = auth_ns.model('SignUpParams', {
        'firstName': fields.String(required=True, description='User\'s first name'),
        'lastName': fields.String(required=True, description='User\'s last name'),
        'role': fields.String(required=True, description='User\'s role'),
        'email': fields.String(required=True, description='User\'s email'),
        'password': fields.String(required=True, description='User\'s password'),
        'bio': fields.String(description='User\'s bio'),
    })

    # Define the response schema for successful signup (201)
    auth_sign_up_success_model = auth_ns.model('SignUpSuccess', {
        'message': fields.String(description='Message indicating registration success and email verification prompt')
    })

    # Define the response schema for email already registered (400)
    auth_sign_up_email_exists_model = auth_ns.model('SignUpEmailExists', {
        'message': fields.String(description='Message indicating email is already registered')
    })

    auth_sign_up_internal_error_model = auth_ns.model('SignUpInternalServerError', {
        'message': fields.String(description='Error message for internal server error'),
        'error': fields.String(description='Specific error description', enum=[
            'Profile Picture Upload Failed',
            'User Creation Failed',
            'Verification Email Failed'
        ])
    })

    @auth_ns.doc(
        params={
            'firstName': 'User\'s first name',
            'lastName': 'User\'s last name',
            'role': 'User\'s role',
            'email': 'User\'s email address',
            'password': 'User\'s password',
            'bio': 'User\'s bio',
        },
        responses={
            201: ('Registration Successful', auth_sign_up_success_model),
            400: ('Email Already Registered', auth_sign_up_email_exists_model),
            500: ('Internal Server Error: This may include "Profile Picture Upload Failed", "User Creation Failed", or "Verification Email Failed".', auth_sign_up_internal_error_model)
        }
    )

    @auth_ns.expect(auth_sign_up_params_model)

    def post(self):

        
        # verification_link = f"http://127.0.0.1:5000/auth/verify/123"
        # msg = MailMessage("Verify Your Email", sender="your-email@example.com", recipients=[email])
        # msg.body = f"Please click the following link to verify your email: {verification_link}"


        data = request.form
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        role = data.get('role')
        email = data.get('email')
        password = data.get('password')
        bio = data.get('bio')

        if User.query.filter_by(email=email).first():
            return {'message': 'Email is already registered'}, 400

        profile_picture = request.files.get('profilePicture')
        profile_picture_url = None
        if profile_picture:
            try:
                upload_result = cloudinary.uploader.upload(profile_picture)
                profile_picture_url = upload_result.get('secure_url')
            except Exception as e:
                return {
                        'message': f'Profile picture upload failed: {e}', 
                        'error': 'Profile Picture Upload Failed'
                        }, 500

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        verification_token = str(uuid.uuid4())

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            role=role,
            email=email,
            password=hashed_password,
            profile_picture=profile_picture_url,
            bio=bio,
            verification_token=verification_token
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            
            'User Creation Failed',
            'Verification Email Failed'
            return {
                    'message': f'Failed to create user: {e}',
                    'error': 'User Creation Failed'   
                }, 500
        
        # Send verification email
        verification_link = f"https://skillz-api-6411a8af904e.herokuapp.com/auth/verify/{verification_token}"
        msg_subject = "Verify Your Email"
        msg_body = f"Please click the following link to verify your email: {verification_link}"

        try:
            send_email(email, msg_subject, msg_body)

        except Exception as e:
            return {
                'message': f'Failed to send verification email: {e}',
                'error': 'Verification Email Failed'   
            }, 500

        return {'message': 'Registration successful. Please check your email to verify your account.'}, 201

class VerifyEmailResource(Resource):
    # Define the response model for a successful verification (200)
    auth_verify_email_success_model = auth_ns.model('VerifyEmailSuccess', {
        'message': fields.String(description='Message confirming email verification')
    })

    # Define the response model for an invalid or expired token (400)
    auth_verify_email_invalid_token_model = auth_ns.model('VerifyEmailInvalidToken', {
        'message': fields.String(description='Message indicating invalid or expired token')
    })

    # Define the response model for a generic internal server error (500)
    auth_verify_email_internal_error_model = auth_ns.model('VerifyEmailInternalError', {
        'message': fields.String(description='A server error occurred during email verification'),
        'details': fields.String(description='Specific error description', enum=[
            'Database Commit Failed', 
            'Token Processing Error'
        ])
    })

    @auth_ns.doc(
        responses={
            200: ('Email Verified Successfully', auth_verify_email_success_model),
            400: ('Invalid or Expired Token', auth_verify_email_invalid_token_model),
            500: ('Internal Server Error: This may include "Database Commit Failed" or "Token Processing Error".', auth_verify_email_internal_error_model)
        }
    )

    def get(self, token):
        user = User.query.filter_by(verification_token=token).first()
        if user:
            user.verified = True
            user.verification_token = None  # Clear the token after verification
            db.session.commit()
            return {'message': 'Email verified successfully'}, 200
        else:
            return {'message': 'Invalid or expired token'}, 400


class SignInResource(Resource):
    # Define the response schema for payload
    auth_sign_in_params_model = auth_ns.model('SignIn', {
        'email': fields.String(required=True, description='The email'),
        'password': fields.String(required=True, description='The password'),
    })
    # Define the response schema for successful login (200)
    auth_sign_in_success_model = auth_ns.model('SignInSuccess', {
        'message': fields.String(description='Message confirming successful login and OTP sent')
    })
    # Define the response schema for invalid credentials (401)
    auth_sign_in_invalid_credentials_model = auth_ns.model('SignInInvalidCredentials', {
        'message': fields.String(description='Message indicating invalid credentials')
    })
    # Define the response schema for user not verified (403)
    auth_sign_in_user_not_verified_model = auth_ns.model('SignInUserNotVerified', {
        'message': fields.String(description='Message prompting user to verify email before logging in')
    })
    # Define the response schema for failed OTP send (500)
    auth_sign_in_failed_send_otp_model = auth_ns.model('SignInFailedSendOTP', {
        'message': fields.String(description='Message indicating failure to send OTP')
    })

    @auth_ns.doc(
        params={'email': 'The email to sign in with', 'password': 'The password to sign in with'},
        responses={
            200: ('Success', auth_sign_in_success_model),
            401: ('Invalid credentials', auth_sign_in_user_not_verified_model),
            403: ('Account Not Verified', auth_sign_in_user_not_verified_model),
            500: ('Failed to send 2FA code', auth_sign_in_failed_send_otp_model),
        }
    )

    @auth_ns.expect(auth_sign_in_params_model)

    def post(self):
        # return {"message": "Signed in successfully!"}, 200
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            if not user.verified:
                return {'message': 'Please verify your email before logging in'}, 403

            # Generate 2FA code
            otp = generate_otp()
            otp_store[email] = {
                'otp': otp,
                'expiry': datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
            }

            # Send OTP to the user's email
            subject = "Verification Code"
            content = f"Your verification code is {otp}. It will expire in 5 minutes."
            if send_email(email, subject, content):  # Pass 'mail' here
                
                return {'message': 'Please verify your 2FA code sent to your email'}, 200

            return {'message': 'Failed to send 2FA code'}, 500
        
        return {'message': 'Invalid credentials'}, 401

class Verify2FAResource(Resource):
    # Model for successful 2FA verification (200)
    auth_verify_2fa_success_model = auth_ns.model('Verify2FASuccess', {
        'token': fields.String(description='JWT token returned after successful 2FA verification')
    })

    # Model for all 400 errors (combining OTP expired, Invalid OTP, and No OTP)
    auth_verify_2fa_error_model = auth_ns.model('Verify2FAError', {
        'message': fields.String(description='Message indicating the error')
    })

    @auth_ns.doc(
        params={'email': 'The email for 2FA verification', 'otp': 'The OTP sent to the user'},
        responses={
            200: ('2FA verified successfully, JWT token returned', auth_verify_2fa_success_model),
            400: ('Error in OTP verification', auth_verify_2fa_error_model),  # Combined 400 response
        }
    )

    def post(self):
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')

        if email in otp_store:
            stored_otp = otp_store[email]['otp']
            expiry = otp_store[email]['expiry']
            if datetime.now() > expiry:
                return {'message': 'OTP expired'}, 400
            if otp == stored_otp:
                del otp_store[email]  # Remove OTP after successful verification
                # Generate JWT token
                user = User.query.filter_by(email=email).first()
                access_token = create_access_token(identity=user.id)

                return {'token': access_token, 'user': user.to_dict()}, 200
            return {'message': 'Invalid OTP'}, 400

        return {'message': 'No OTP found for email'}, 400

class SignOutResource(Resource):
    @jwt_required()
    def post(self):
        # Invalidate the token on the client side
        return {'message': 'Successfully logged out'}, 200

class UsersInConversationResource(Resource):
    # User model: represents a single user structure
    user_model = users_ns.model('User', {
        'id': fields.Integer(description='User ID'),
        'first_name': fields.String(description='User first name'),
        'last_name': fields.String(description='User last name'),
        'email': fields.String(description='User email address'),
        'bio': fields.String(description='User bio'),
        'profile_picture': fields.String(description='Profile picture URL'),
    })

    # General error model for failure responses
    general_error_model = users_ns.model('GeneralError', {
        'message': fields.String(description='Error message'),
    })

    # List of users model (used in the 200 response for users in conversation)
    users_list_model = users_ns.model('UsersList', {
        'users': fields.List(fields.Nested(user_model))
    })

    @users_ns.doc(
        responses={
            200: ('List of users in conversation retrieved successfully', users_ns.model('UsersList', {
                'users': fields.List(fields.Nested(user_model))
            })),
            400: ('Invalid user ID format', general_error_model),  # 400 error for invalid user ID format
            500: ('Internal server error', general_error_model)  # General error model for failure
        }
    )
      
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        if not isinstance(current_user_id, int):
            return jsonify({"error": "Invalid user ID format"}), 400

        received_messages = Message.query.filter_by(receiver_id=current_user_id).all()
        sent_messages = Message.query.filter_by(sender_id=current_user_id).all()

        user_ids = set(
            [msg.sender_id for msg in received_messages] +
            [msg.receiver_id for msg in sent_messages]
        )
        user_ids.discard(current_user_id)

        users = User.query.filter(User.id.in_(user_ids)).all()
        users_list = [user.to_dict() for user in users]

        return jsonify(users_list)

class InstructorResource(Resource):
    def get(self):
        # Return the results as a JSON response
        instructors = User.query.filter_by(role='instructor').all()
        instructors_list = [user.to_dict() for user in instructors]

        return jsonify(instructors_list)
    
    def delete(email):
        email = request.args.get('email')  # Get the email from the query string
    
        if not email:
            return {"message": "Email parameter is required"}, 400

        # Query the user by email
        user = User.query.filter_by(email=email).first()

        if user:
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully"}, 200
        else:
            return {"message": "User not found"}, 404



class UserResource(Resource):
    # Model for successful user retrieval (200)
    auth_user_success_model = auth_ns.model('UserSuccess', {
        'id': fields.Integer(description='The unique ID of the user'),
        'first_name': fields.String(description='The first name of the user'),
        'last_name': fields.String(description='The last name of the user'),
        'email': fields.String(description='The email address of the user'),
        'role': fields.String(description='The role of the user (e.g., admin, user)'),
        'bio': fields.String(description='The bio of the user'),
        'profile_picture': fields.String(description='The URL to the user\'s profile picture'),
        'courses': fields.List(fields.String, description='A list of the user\'s courses (if included)', example=['Course 1', 'Course 2'])
    })

    # Model for 404 errors (User not found)
    auth_user_not_found_model = auth_ns.model('UserNotFoundError', {
        'message': fields.String(description='Message indicating the user was not found')
    })

    @jwt_required()

    @user_ns.doc(
        params={'user_id': 'The ID of the user to retrieve (optional)'},
        responses={
            200: ('User retrieved successfully', auth_user_success_model),  # Define your success model for user data
            404: ('User not found', auth_user_not_found_model),  # 404 error using the combined model
        }
    )

    def get(self, user_id=None):
        if user_id is None:
            current_user_id = get_jwt_identity()
            user = User.query.filter_by(id=current_user_id).first()
        else:
            user = User.query.filter_by(id=user_id).first()

        if not user:
            return {'message': 'User not found'}, 404

        # Fetch the user and include their courses
        return user.to_dict(include_courses=True), 200

class AllUsersResource(Resource):
    # Define the model for a single user
    user_model = user_ns.model('User', {
        'id': fields.Integer(description='User ID'),
        'first_name': fields.String(description='User first name'),
        'last_name': fields.String(description='User last name'),
        'email': fields.String(description='User email address'),
        'bio': fields.String(description='User bio'),
        'profile_picture': fields.String(description='Profile picture URL'),
    })
     # Model for general error (500)
    general_error_model = user_ns.model('GeneralError', {
        'message': fields.String(description='General error message for server-side issues')
    })

    @users_ns.doc(
        responses={
            200: ('List of users retrieved successfully', user_ns.model('UsersList', {
                'users': fields.List(fields.Nested(user_model))
            })),
            500: ('Internal server error', general_error_model)  # General error model for failure
        }
    )
    @jwt_required()
    def get(self):
        # No role check required; any logged-in user can access
        users = User.query.all()
        users_list = [user.to_dict() for user in users]

        return jsonify(users_list)

class EditUserResource(Resource):
    # Define the request parameters model for updating user details
    edit_user_params_model = user_ns.model('EditUserParams', {
        'first_name': fields.String(description='User first name', required=False),
        'last_name': fields.String(description='User last name', required=False),
        'email': fields.String(description='User email address', required=False),
        'bio': fields.String(description='User bio', required=False),
        'profile_picture': fields.String(description='Profile picture file (if uploading)', required=False),
    })
    # Model for successful user edit (200)
    edit_user_success_model = user_ns.model('EditUserSuccess', {
        'message': fields.String(description='Success message indicating user update was successful')
    })
    # Model for User Not Found (404)
    user_not_found_model = user_ns.model('UserNotFound', {
        'message': fields.String(description='Message indicating the user was not found')
    })
    # Model for general error (500)
    general_error_model = user_ns.model('GeneralError', {
        'message': fields.String(description='General error message for server-side issues')
    })

    @user_ns.doc(
        responses={
            200: ('User details updated successfully', edit_user_success_model),  # Using edit_user_success_model
            404: ('User not found', user_not_found_model),  # Using user_not_found_model
            500: ('Internal server error', general_error_model) # General error model
        }
    )

    @jwt_required()
    def put(self):
        current_user_id = get_jwt_identity()
        data = request.get_json()

        user = User.query.filter_by(id=current_user_id).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Optional: Validate input data here

        # Update user details
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'bio' in data:
            user.bio = data['bio']
        # Handle profile picture upload if included in data
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            try:
                upload_result = cloudinary.uploader.upload(profile_picture)
                user.profile_picture = upload_result.get('secure_url')
            except Exception as e:
                return {'message': f'Profile picture upload failed: {e}'}, 500

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to update user: {e}'}, 500

        return {'message': 'User details updated successfully'}, 200

class PublicUserResource(Resource):
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            return {'message': 'User not found'}, 404

        # Return user details without authentication
        return user.to_dict(include_courses=True), 200
    
# /auth/
auth_ns.add_resource(SignInResource, '/sign-in') 
auth_ns.add_resource(SignUpResource, '/sign-up') 
auth_ns.add_resource(VerifyEmailResource, '/verify/<string:token>') 
auth_ns.add_resource(Verify2FAResource, '/verify-2fa')

# /users/
user_ns.add_resource(UserResource, '', '/<int:user_id>')
user_ns.add_resource(EditUserResource, '/edit')

users_ns.add_resource(AllUsersResource, '/all')
users_ns.add_resource(UsersInConversationResource, '/conversations')
users_ns.add_resource(InstructorResource, '/instructor')
