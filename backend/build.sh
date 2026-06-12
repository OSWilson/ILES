
set -o errexit


pip install -r requirements.txt


python manage.py collectstatic --no-input


python manage.py migrate




python manage.py createsuperuser \
  --noinput \
  --username superadmin \
  --email superadmin@iles.ac.ug || true