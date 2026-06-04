from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create initial staff and superuser accounts.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update existing users with the default credentials and roles.',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        force = options['force']

        default_users = [
            {
                'username': 'admin',
                'email': 'admin@evsu.local',
                'password': 'AdminPass123!',
                'role': 'MANAGER',
                'is_superuser': True,
                'is_staff': True,
                'first_name': 'Admin',
                'last_name': 'User',
            },
            {
                'username': 'manager',
                'email': 'manager@evsu.local',
                'password': 'ManagerPass123!',
                'role': 'MANAGER',
                'is_superuser': False,
                'is_staff': True,
                'first_name': 'Manager',
                'last_name': 'Staff',
            },
            {
                'username': 'staff',
                'email': 'staff@evsu.local',
                'password': 'StaffPass123!',
                'role': 'STAFF',
                'is_superuser': False,
                'is_staff': True,
                'first_name': 'Staff',
                'last_name': 'Member',
            },
            {
                'username': 'driver',
                'email': 'driver@evsu.local',
                'password': 'DriverPass123!',
                'role': 'DRIVER',
                'is_superuser': False,
                'is_staff': True,
                'first_name': 'Driver',
                'last_name': 'Staff',
            },
            {
                'username': 'auditor',
                'email': 'auditor@evsu.local',
                'password': 'AuditorPass123!',
                'role': 'AUDITOR',
                'is_superuser': False,
                'is_staff': True,
                'first_name': 'Auditor',
                'last_name': 'Staff',
            },
        ]

        for user_data in default_users:
            username = user_data['username']
            password = user_data.pop('password')
            user, created = User.objects.get_or_create(
                username=username,
                defaults=user_data,
            )

            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            else:
                if force:
                    for field, value in user_data.items():
                        setattr(user, field, value)
                    user.set_password(password)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated user: {username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'User already exists: {username}'))

        self.stdout.write(self.style.SUCCESS('Initial user setup completed.'))
