Overview
========

Word Wiinaq is an [Kodiak Alutiiq](http://www.alutiiqlanguage.org/) dictionary
web application with automatically generated ending tables and souped-up search
capabilities.

It is written in Python using Django.

Installation
============

Downloading and running locally
-------------------------------

If you haven't already, you'll want to start by installing [Python
2.7](https://www.python.org/downloads/) and
[pip](https://pypi.python.org/pypi/pip).  Then install Django:

    pip install django django-nose

Find a nice spot for the repo and clone it:

    git clone https://github.com/futurulus/wiinaq.git
    cd wiinaq

Set up the database:

    ./manage.py migrate
    ./manage.py loaddata sources
    ./manage.py loaddata words_free

Finally, start the server:

    ./server

Once you do this, your browser should be able to load the site locally at
http://localhost:8000/.

If you'd like to take a look at how the admin interface works, make yourself a
superuser account (you may be prompted to do this by some of the previous
commands):

    ./manage.py createsuperuser

Then make sure the server is running and point your browser to
http://localhost:8000/admin/.

Running on OpenShift
--------------------

Word Wiinaq is configured to run out of the box on RedHat OpenShift. You'll
need to create an account at http://openshift.com/ and initialize an app with
the Django, MySQL, and cron cartridges.

(TODO: add relevant instructions from `README_OPENSHIFT.md`)

Setting up Dropbox backup
-------------------------

If you only want to back up the database from your local installation, you can
periodically run

    ./backup

The first time you run the script, you'll be prompted to set up your
information on the Dropbox Apps website.

To configure this as a daily job in OpenShift, run the setup script (from your
local installation):

    ./openshift_setup_dropbox

Bulk editing/adding
===================

The admin interface allows you to easily edit individual entries, but for
adding or changing large numbers of entries in bulk, it can be inconvenient.
You can look through and edit a CSV dump of the database by running

    ./export_csv > data_dump.csv

`data_dump.csv` can be called anything you'd like, and placed anywhere. The
columns correpond to fields shown in the `Chunk` admin interface (the exact
order is listed in `dictionary/json_to_csv.py`).

Once you've made your edits, replace the contents of the database with the new
version:

    ./import_csv data_dump.csv

You'll be prompted to confirm this potentially destructive operation. The
script will automatically back up the database to a file in
`dictionary/fixtures` first in case something goes wrong.

License
=======

See the file `LICENSE` for the full text of the GNU General Public License.

Copyright (C) 2015 William Monroe

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
