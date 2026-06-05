import csv
import secrets
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = (
        "Generate new random passwords for all users and optionally apply them. "
        "By default this command only writes a CSV with new passwords. Use --apply to set them in the database."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply the generated passwords to user accounts in the database.',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='accounts_export.csv',
            help='Output CSV path (relative to project root).',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        rows = [('username', 'email', 'role', 'new_password')]

        for u in User.objects.all():
            pwd = secrets.token_urlsafe(10)
            rows.append((u.username, u.email or '', getattr(u, 'role', '') or '', pwd))
            if options['apply']:
                u.set_password(pwd)
                u.save()

        out = options['output']
        out_path = os.path.abspath(out)
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        self.stdout.write(self.style.SUCCESS(f'Wrote {out_path}'))
        if not options['apply']:
            self.stdout.write('Passwords were NOT applied. Re-run with --apply to set them in the database.')
        else:
            self.stdout.write(self.style.WARNING('Passwords applied to the database. Ensure you distribute the CSV securely.'))
