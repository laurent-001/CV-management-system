import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Profile, JobPosition, CompanyInfo

class Command(BaseCommand):
    help = 'Seeds the database with initial data.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Clean up existing data
        User.objects.exclude(is_superuser=True).delete()
        JobPosition.objects.all().delete()
        CompanyInfo.objects.all().delete()

        # Create Company Info
        company_info = CompanyInfo.objects.create(
            name="Innovate Inc.",
            description="A leading company in the tech industry, focused on innovation and creating cutting-edge solutions.",
            email="contact@innovateinc.com",
            phone="123-456-7890",
            address="123 Tech Avenue, Silicon Valley, CA",
            logo="company/logo.svg",
        )
        self.stdout.write(self.style.SUCCESS('Successfully created company info.'))

        # Create Job Poster user
        poster_user = User.objects.create_user(
            username='jobposter',
            password='password123',
            email='poster@innovateinc.com',
            first_name='John',
            last_name='Doe',
        )
        Profile.objects.create(user=poster_user, role='POSTER')
        self.stdout.write(self.style.SUCCESS('Successfully created a job poster user.'))

        # Create Job Applicant user
        applicant_user = User.objects.create_user(
            username='jobapplicant',
            password='password123',
            email='applicant@example.com',
            first_name='Jane',
            last_name='Smith',
        )
        Profile.objects.create(
            user=applicant_user,
            role='APPLICANT',
            profile_picture="profiles/placeholder.png",
            skills="Django, Python, HTML, CSS",
            work_experience="2 years as a junior developer.",
            education="B.S. in Computer Science",
        )
        self.stdout.write(self.style.SUCCESS('Successfully created a job applicant user.'))

        # Create Job Positions
        JobPosition.objects.create(
            title='Senior Python Developer',
            description='We are looking for an experienced Python developer to join our team.',
            required_skills='Python, Django, DRF, PostgreSQL',
            location='San Francisco, CA',
            job_type='Full-time',
            application_deadline=datetime.date.today() + datetime.timedelta(days=30),
            posted_by=poster_user,
        )

        JobPosition.objects.create(
            title='Frontend Developer (React)',
            description='Join our frontend team and build amazing user interfaces with React.',
            required_skills='HTML, CSS, JavaScript, React, Redux',
            location='New York, NY',
            job_type='Full-time',
            application_deadline=datetime.date.today() + datetime.timedelta(days=45),
            posted_by=poster_user,
        )

        JobPosition.objects.create(
            title='Data Science Intern',
            description='An exciting opportunity for a data science student to gain hands-on experience.',
            required_skills='Python, Pandas, NumPy, Scikit-learn',
            location='Remote',
            job_type='Internship',
            application_deadline=datetime.date.today() + datetime.timedelta(days=20),
            posted_by=poster_user,
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database.'))
