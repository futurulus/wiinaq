Overview
========

Word Wiinaq is a [Kodiak Alutiiq](http://www.alutiiqlanguage.org/) dictionary
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
    ./manage.py loaddata sources words_free

Finally, start the server:

    ./server

Once you do this, your browser should be able to load the site locally at
http://localhost:8000/.

If you'd like to take a look at how the admin interface works, make yourself a
superuser account:

    ./manage.py createsuperuser

Then make sure the server is running, point your browser to
http://localhost:8000/admin/, and enter the username and password you created
in the previous command.

Running on Heroku
-----------------

Word Wiinaq is configured to run out of the box on Heroku. You'll
need to create an account at http://heroku.com/, initialize a Python app,
and install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-command-line).
Then issue these commands from your git repository:

    heroku login
    heroku git:remote -a <app-name>
    heroku config:set ON_HEROKU=true
    git push heroku master

The environment variable `ON_HEROKU` changes a few things to make the app play
well with Heroku.
A link to connect to the running website will show up near the end of the output
from `git push`. However, the website won't quite work yet&mdash;first
you need to run the same commands as above but on the Heroku box:

    heroku run ./manage.py migrate
    heroku run ./manage.py loaddata sources words_free
    heroku run ./manage.py createsuperuser

Finally, start up a dyno for hosting the app:

    heroku ps:scale web=1

If you have additional dictionary files to load, you'll need to start a shell on
Heroku and pull them in from some other Internet-accessible location, since Heroku
disallows incoming scp connections:

    heroku run bash
    $ scp some_online_location:new_words.csv dict_sources/
    $ ./reload_data

Setting up Dropbox backup
-------------------------

If you only want to back up the database from your local installation, you can
periodically run

    ./backup

The first time you run the script, you'll be prompted to set up your
information on the Dropbox Apps website.

To configure this as a recurring job in Heroku, run the setup script (from your
local installation):

    ./heroku_setup_dropbox

Then create a [Scheduler task](https://devcenter.heroku.com/articles/scheduler)
to run `./backup` every so often.

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

Copyright (C) 2015-2016 William Monroe

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
