# Run with: python -m dictionary.save_all
# This script is useful for refreshing the "search_word" and "search_text"
# fields when doing database migrations or restoring backups.

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
import django
django.setup()

from .models import Entry


def save_all():
    for i, entry in enumerate(Entry.objects.all()):
        if i % 1000 == 0:
            print(i)
        entry.save()


if __name__ == '__main__':
    save_all()
