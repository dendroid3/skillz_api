from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from models import db, Message, User
import logging
from flask_restx import Namespace, Resource, fields

logging.basicConfig(level=logging.DEBUG)

message_ns = Namespace('messages', description='Messaging-related operations')

class MessageResource(Resource):
    # Message model: represents a single message
    message_model = message_ns.model('Message', {
        'sender_id': fields.Integer(description='ID of the sender'),
        'receiver_id': fields.Integer(description='ID of the receiver'),
        'content': fields.String(description='Message content'),
        'sent_at': fields.DateTime(description='Time message was sent'),
    })

    # Error model for general errors like missing fields or internal issues
    general_error_model = message_ns.model('GeneralError', {
        'message': fields.String(description='Error message'),
    })

    # Success model for sending a message successfully
    message_sent_success_model = message_ns.model('MessageSentSuccess', {
        'message': fields.String(description='Success message'),
        'data': fields.Nested(message_model, description='Message data')  # Include message details
    })

    # Conversations list model for response when retrieving user conversations
    conversations_list_model = message_ns.model('ConversationsList', {
        'conversations': fields.List(fields.Nested(message_model))  # List of users involved in conversations
    })

    @message_ns.doc(
        responses={
            201: ('Message sent successfully', message_sent_success_model),  # Success response
            400: ('Bad request, missing required fields', general_error_model),  # Missing fields error
            500: ('Internal server error', general_error_model)  # General error response
        }
    )

    @jwt_required()
    def post(self):
        try:
            data = request.json
            logging.debug(f"Received data: {data}")

            sender_id = get_jwt_identity()
            receiver_id = data.get('receiver_id')
            content = data.get('content')

            if not receiver_id or not content:
                return {"error": "Receiver ID and content are required"}, 400

            message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
            db.session.add(message)
            db.session.commit()

            response_data = {"message": "Message sent successfully", "data": message.to_dict()}
            logging.debug(f"Sending response: {response_data}")

            return response_data, 201

        except Exception as e:
            logging.error(f"Error: {e}", exc_info=True)
            return {"error": "Internal Server Error"}, 500
        
    @message_ns.doc(
        responses={
            200: ('List of messages retrieved successfully', fields.List(fields.Nested(message_model))),  # 200 response with list of messages
            500: ('Internal server error', general_error_model)  # General error response
        }
    )
    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            user_id = request.args.get('user_id')

            if user_id:
                messages = Message.query.filter(
                    ((Message.sender_id == current_user_id) & (Message.receiver_id == user_id)) |
                    ((Message.sender_id == user_id) & (Message.receiver_id == current_user_id))
                ).order_by(Message.sent_at.asc()).all()

                message_list = [message.to_dict() for message in messages]
                logging.debug(f"Messages retrieved: {message_list}")
                return message_list, 200

            else:
                conversations = db.session.query(User).filter(
                    (User.id == Message.receiver_id) | (User.id == Message.sender_id)
                ).distinct().all()

                conversation_list = [user.to_dict() for user in conversations]
                logging.debug(f"Conversations retrieved: {conversation_list}")
                return conversation_list, 200

        except Exception as e:
            logging.error(f"Error: {e}", exc_info=True)
            return {"error": "Internal Server Error"}, 500

message_ns.add_resource(MessageResource, '', '/<int:user_id>')
