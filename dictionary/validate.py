# Run with: python -m dictionary.validate

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
from django.conf import settings  # NOQA: set up Django database

import random


def find_bad_entries():
    from .models import Chunk
    from .views import group_entries
    from .alutiiq import get_endings_map, is_valid

    entries = group_entries(Chunk.objects.all(), separate_roots=True)
    bad_forms = []
    for i, entry in enumerate(entries):
        if i % 100 == 0:
            print '{} / {}'.format(i, len(entries))
        for root in entry.roots:
            word = root.word.replace('(', '').replace(')', '')
            if not is_valid(word):
                bad_forms.append(('-', word, '-'))
            elif root.pos and root.pos != 'None':
                for tags, form in get_endings_map(root.root, root.pos).iteritems():
                    form = form.replace('(', '').replace(')', '')
                    if form != '-' and not is_valid(form):
                        bad_forms.append((form, root.word, tags))
        if len(bad_forms) > 200:
            break

    sample_size = min(100, len(bad_forms))
    for form, word, tags in random.sample(bad_forms, sample_size):
        print('{0: <51} {1}'.format('{0: <25} {1}'.format(form, word), tags).encode('utf-8'))


if __name__ == '__main__':
    find_bad_entries()
