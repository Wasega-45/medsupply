#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Auto-create the superuser
python manage.py createsuperuser --noinput || true

# Auto-populate the 47 counties
python manage.py shell -c "
from core.models import County
counties = [
    ('Mombasa', '001'), ('Kwale', '002'), ('Kilifi', '003'), ('Tana River', '004'), ('Lamu', '005'),
    ('Taita-Taveta', '006'), ('Garissa', '007'), ('Wajir', '008'), ('Mandera', '009'), ('Marsabit', '010'),
    ('Isiolo', '011'), ('Meru', '012'), ('Tharaka-Nithi', '013'), ('Embu', '014'), ('Kitui', '015'),
    ('Machakos', '016'), ('Makueni', '017'), ('Nyandarua', '018'), ('Nyeri', '019'), ('Kirinyaga', '020'),
    ('Muranga', '021'), ('Kiambu', '022'), ('Turkana', '023'), ('West Pokot', '024'), ('Samburu', '025'),
    ('Trans Nzoia', '026'), ('Uasin Gishu', '027'), ('Elgeyo-Marakwet', '028'), ('Nandi', '029'), ('Baringo', '030'),
    ('Laikipia', '031'), ('Nakuru', '032'), ('Narok', '033'), ('Kajiado', '034'), ('Kericho', '035'),
    ('Bomet', '036'), ('Kakamega', '037'), ('Vihiga', '038'), ('Bungoma', '039'), ('Busia', '040'),
    ('Siaya', '041'), ('Kisumu', '042'), ('Homa Bay', '043'), ('Migori', '044'), ('Kisii', '045'),
    ('Nyamira', '046'), ('Nairobi', '047')
]
for name, code in counties:
    County.objects.get_or_create(code=code, defaults={'name': name})
"