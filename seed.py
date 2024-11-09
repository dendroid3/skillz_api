from app import app, db
from models import User, Course, CourseContent, Payment, Enrollment, Review, Message, Accolade
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash
from faker import Faker

# Define East African Time timezone
EAT = pytz.timezone('Africa/Nairobi')

# Define function to get current time in EAT
def get_eat_now():
    return datetime.now(EAT)

def seed_database():
    fake = Faker()  # Create a Faker instance

    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create real sample users
        users = [
            User(
                role='learner',
                first_name='Alice',
                last_name='Johnson',
                email='alice.johnson@example.com',
                password=generate_password_hash('password123'),
                profile_picture='https://example.com/images/alice.jpg',
                bio='Aspiring data scientist passionate about AI and machine learning.',
                verified=True,
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            User(
                role='instructor',
                first_name='Cyndi',
                last_name='Marren',
                email='marrencyndi101@gmail.com',
                password=generate_password_hash('password123'),
                profile_picture='data:image/jpeg;base64,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',
                bio='Seasoned software engineer with 10+ years of experience.',
                verified=True,
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            User(
                role='instructor',
                first_name='Carol',
                last_name='Williams',
                email='carol.williams@example.com',
                password=generate_password_hash('password123'),
                profile_picture='https://example.com/images/carol.jpg',
                bio='Expert chef and culinary instructor.',
                verified=True,
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            User(
                role='instructor',
                first_name='David',
                last_name='Brown',
                email='david.brown@example.com',
                password=generate_password_hash('password123'),
                profile_picture='https://example.com/images/david.jpg',
                bio='Professional artist specializing in digital art.',
                verified=True,
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            User(
                role='learner',
                first_name='Eve',
                last_name='Davis',
                email='eve.davis@example.com',
                password=generate_password_hash('password123'),
                profile_picture='https://example.com/images/eve.jpg',
                bio='Business analyst with a passion for entrepreneurship.',
                verified=True,
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            )
            # Add more real users if needed
        ]

        db.session.add_all(users)
        db.session.commit()

        # Create real sample courses
        courses = [
            Course(
                instructor_id=users[1].id,  # Bob
                title='Introduction to Python Programming',
                description='Learn the basics of Python, one of the most popular programming languages.',
                price=50,
                image_url='https://jonnychipz.com/wp-content/uploads/2020/11/introtopythonpython-hawaii-2017.png',
                category='Tech',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            Course(
                instructor_id=users[1].id,  # Bob
                title='AI for Beginners',
                description='Learn the basics of AI, and all AI tools.',
                price=100,
                image_url='https://example.com/images/ai-course.jpg',
                category='AI',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            Course(
                instructor_id=users[2].id,  # Carol
                title='Mastering Italian Cuisine',
                description='A comprehensive guide to cooking authentic Italian dishes.',
                price=75,
                image_url='https://static1.squarespace.com/static/56801b350e4c11744888ec37/t/5f5aea5a21cd480546a5d8b5/1599793774795/Lidia%27s+Mastering.JPG?format=1500w',
                category='Cooking',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            Course(
                instructor_id=users[2].id,  # Carol
                title='Baking for Beginners',
                description='Learn the basics of baking delicious bread and pastries.',
                price=60,
                image_url='https://media.istockphoto.com/id/1371938299/photo/african-american-family-at-home.jpg?s=2048x2048&w=is&k=20&c=BnbEgKYrv80DY8RdYhmODBzXcdt6znx81lFRJnEA5VY=',
                category='Cooking',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            Course(
                instructor_id=users[3].id,  # David
                title='Introduction to Digital Art',
                description='Learn to create stunning digital artworks using industry-standard tools.',
                price=120,
                image_url='https://www.google.com/url?sa=i&url=https%3A%2F%2Fhe.kendallhunt.com%2Fproduct%2Fdigital-art-and-design-introduction&psig=AOvVaw2j9CjjrHZ77slim3MHown3&ust=1723886240363000&source=images&cd=vfe&opi=89978449&ved=0CA8QjRxqFwoTCNjP-eqW-YcDFQAAAAAdAAAAABAI',
                category='Art',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            Course(
                instructor_id=users[3].id,  # David
                title='Advanced Photoshop Techniques',
                description='Master the art of photo editing with advanced techniques in Photoshop.',
                price=130,
                image_url='data:image/jpeg;base64,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',
                category='Art',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            Course(
                instructor_id=users[1].id,  # Bob
                title='Web Development Bootcamp',
                description='Become a full-stack web developer with this intensive bootcamp.',
                price=200,
                image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2Yd9KwuRnRTRnk_vh-J1rsWyaafavhRGZrw&s',
                category='Tech',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            Course(
                instructor_id=users[1].id,  # Bob
                title='Data Structures and Algorithms',
                description='An in-depth course on data structures and algorithms for software engineering.',
                price=150,
                image_url='data:image/png;base64,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',
                category='Tech',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            Course(
                instructor_id=users[1].id,  # Bob
                title='Healthy Cooking: Low-Carb Recipes',
                description='Learn how to cook delicious low-carb meals for a healthier lifestyle.',
                price=80,
                image_url='https://www.eatingwell.com/thmb/Druq51UV_zOxJ3x4Lny1BvNbXHc=/364x242/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/ten-minute-spinach-omelet-2000-ef8499a54f7447c297192772cac07c90.jpg',
                category='Cooking',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            Course(
                instructor_id=users[3].id,  # David
                title='Graphic Design Essentials',
                description='A beginner-friendly course on the fundamentals of graphic design.',
                price=90,
                image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT7r7-DzV5UbLtY8Ls1URAmGFRcBkRJ6mfv0Q&s',
                category='Art',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
        ]

        db.session.add_all(courses)
        db.session.commit()

        # Create real sample course content
        course_contents = [
            CourseContent(
                course_id=courses[7].id,
                content_type='Video',
                content_url='https://pin.it/Oe4FcOdo4',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            CourseContent(
                course_id=courses[1].id,
                content_type='Text',
                content_url='https://example.com/texts/ai-introduction.pdf',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            CourseContent(
                course_id=courses[2].id,
                content_type='Video',
                content_url='https://example.com/videos/italian-cuisine.mp4',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            CourseContent(
                course_id=courses[3].id,
                content_type='Text',
                content_url='https://example.com/texts/baking-basics.pdf',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            CourseContent(
                course_id=courses[4].id,
                content_type='Video',
                content_url='https://example.com/videos/digital-art.mp4',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            CourseContent(
                course_id=courses[5].id,
                content_type='Text',
                content_url='https://example.com/texts/photoshop-advanced.pdf',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            CourseContent(
                course_id=courses[6].id,
                content_type='Video',
                content_url='https://example.com/videos/web-development.mp4',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            CourseContent(
                course_id=courses[7].id,
                content_type='Text',
                content_url='https://example.com/texts/data-structures.pdf',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            CourseContent(
                course_id=courses[4].id,
                content_type='Video',
                content_url='https://example.com/videos/graphic-design.mp4',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
        ]

        db.session.add_all(course_contents)
        db.session.commit()

        # Create real sample payments
        payments = [
            Payment(
                learner_id=users[0].id,  # Alice
                course_id=courses[0].id,  # Python Programming
                amount=50,
                payment_date=get_eat_now()
            ),
            Payment(
                learner_id=users[0].id,  # Alice
                course_id=courses[1].id,  # AI for Beginners
                amount=100,
                payment_date=get_eat_now()
            ),
            Payment(
                learner_id=users[4].id,  # Eve
                course_id=courses[4].id,  # Digital Art
                amount=120,
                payment_date=get_eat_now()
            ),
            Payment(
                learner_id=users[4].id,  # Eve
                course_id=courses[5].id,  # Photoshop Techniques
                amount=130,
                payment_date=get_eat_now()
            ),
        ]

        db.session.add_all(payments)
        db.session.commit()

        # Create real sample enrollments
        enrollments = [
            Enrollment(
                learner_id=users[0].id,  # Alice
                course_id=courses[0].id,  # Python Programming
                enrolled_at=get_eat_now()
            ),
            Enrollment(
                learner_id=users[0].id,  # Alice
                course_id=courses[1].id,  # AI for Beginners
                enrolled_at=get_eat_now()
            ),
            Enrollment(
                learner_id=users[4].id,  # Eve
                course_id=courses[4].id,  # Digital Art
                enrolled_at=get_eat_now()
            ),
            Enrollment(
                learner_id=users[4].id,  # Eve
                course_id=courses[5].id,  # Photoshop Techniques
                enrolled_at=get_eat_now()
            ),
        ]

        db.session.add_all(enrollments)
        db.session.commit()

        # Create real sample reviews
        reviews = [
            Review(
                learner_id=users[0].id,  # Alice
                course_id=courses[0].id,  # Python Programming
                rating=5,
                comment='An excellent course for beginners in Python!',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            Review(
                learner_id=users[4].id,  # Eve
                course_id=courses[4].id,  # Digital Art
                rating=4,
                comment='Great introduction to digital art, but could use more advanced content.',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
            Review(
                learner_id=users[4].id,  # Eve
                course_id=courses[5].id,  # Photoshop Techniques
                rating=5,
                comment='Fantastic course! Learned a lot of new techniques.',
                created_at=get_eat_now(),
                updated_at=get_eat_now()
            ),
        ]

        db.session.add_all(reviews)
        db.session.commit()

        # Create real sample messages
        messages = [
            Message(
                sender_id=users[0].id,  # Alice
                receiver_id=users[1].id,  # Bob
                content='Hi Cyndi, I’m interested in your AI course. Can you tell me more about it?',
                sent_at=get_eat_now()
            ),
            Message(
                sender_id=users[1].id,  # Bob
                receiver_id=users[0].id,  # Alice
                content='Hello Alice! The AI course covers basic concepts and applications in AI. Let me know if you have any specific questions.',
                sent_at=get_eat_now()
            ),
            Message(
                sender_id=users[4].id,  # Eve
                receiver_id=users[3].id,  # David
                content='Hi David, I just started your Digital Art course. Could you provide some feedback on my first project?',
                sent_at=get_eat_now()
            ),
            Message(
                sender_id=users[3].id,  # David
                receiver_id=users[4].id,  # Eve
                content='Hi Eve, I’d be happy to review your project. Please send it over.',
                sent_at=get_eat_now()
            ),
        ]

        db.session.add_all(messages)
        db.session.commit()

        # Create real sample accolades
        accolades = [
            Accolade(
                enrollment_id=users[1].id,  # Cyndi 
                title='Top Instructor of the Month',
                description='Awarded for exceptional teaching in Python Programming.',
                awarded_at=get_eat_now()
            ),
            Accolade(
                enrollment_id=users[2].id,  # Carol
                title='Best Cooking Instructor',
                description='Recognized for outstanding performance in Cooking courses.',
                awarded_at=get_eat_now()
            ),
        ]

        db.session.add_all(accolades)
        db.session.commit()

if __name__ == '__main__':
    seed_database()
