#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Auto-create or update superuser
python manage.py shell << EOF
from django.contrib.auth.models import User

SUPERUSER_NAME = 'admin'
SUPERUSER_EMAIL = 'admin@example.com'
SUPERUSER_PASSWORD = 'admin123'

if User.objects.filter(username=SUPERUSER_NAME).exists():
    user = User.objects.get(username=SUPERUSER_NAME)
    user.set_password(SUPERUSER_PASSWORD)
    user.email = SUPERUSER_EMAIL
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f'✅ Superuser password updated: {SUPERUSER_NAME}')
else:
    User.objects.create_superuser(
        username=SUPERUSER_NAME,
        email=SUPERUSER_EMAIL,
        password=SUPERUSER_PASSWORD
    )
    print(f'✅ Superuser created: {SUPERUSER_NAME}')