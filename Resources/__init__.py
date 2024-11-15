# resources/__init__.py

from .user import SignInResource
from .user import SignUpResource
from .user import SignOutResource
from .user import UsersInConversationResource
from .user import UserResource
from .user import EditUserResource, AllUsersResource
from .user import PublicUserResource
from .user import Verify2FAResource
from .user import VerifyEmailResource
from .course import CourseResource
from .course_content import CourseContentResource
from .payment import PaymentResource
from .enrollments_resource import EnrollmentResource
from .reviews import ReviewResource
from .message_resource import MessageResource
from .accolade import AccoladeListResource, AccoladeResource


from .user import auth_ns, user_ns, users_ns
from .message_resource import message_ns
from .enrollments_resource import enrollment_ns
from .course import course_ns
from .payment import payment_ns
from .course_content import course_contents_ns
from .reviews import review_ns


__all__ = [
    'SignUpResource',
    'SignInResource',
    'SignOutResource',
    'UsersInConversationResource',
    'UserResource',
    'EditUserResource',
    'AllUsersResource',
    'CourseResource',
    'CourseContentResource',
    'PaymentResource',
    'EnrollmentResource',
    'ReviewResource',
    'MessageResource',
    'AccoladeResource',
    'AccoladeListResource',
    'Verify2FAResource', 
    'VerifyEmailResource',
    'PublicUserResource',


    'auth_ns',
    'user_ns',
    'users_ns',

    'message_ns',

    'enrollment_ns',

    'course_ns',

    'payment_ns',

    'course_contents_ns',

    'review_ns'
]
