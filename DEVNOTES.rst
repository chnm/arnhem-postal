Development Instructions
========================

Setup and installation
-----------------------

Initial setup and installation:

1. Install and activate Python 3.11.0. It's recommended to use `pyenv <https://github.com/pyenv/pyenv>`_ for this.

2. Install `Poetry <https://python-poetry.org/docs/>`_ for Python dependency management.

3. Once you have Poetry, install required Python dependencies:

.. code-block:: bash

    poetry install

4. Use `Volta <https://volta.sh/>`_ for Node version management

5. Install required Javascript dependencies:

.. code-block:: bash

    npm install

6. Set secrets to a local ``.env`` file. From the terminal, run the following two lines:

.. code-block:: bash

    echo DEBUG=True >> .env
    echo DJANGO_SECRET_KEY=$(poetry run python -c "import secrets; print(secrets.token_urlsafe())") >> .env

7. Then, update your ``settings.py`` file.

.. code-block:: python

    import environ
    from dotenv import load_dotenv

    load_dotenv()

    env = environ.FileAwareEnv(
        DEBUG=(bool, False)
    )

    # [...]

    # Update this existing value
    DEBUG = env('DEBUG')

    # Update this existing value
    SECRET_KEY = env('DJANGO_SECRET_KEY')

8. Create a new database and update your database settings accordingly.

9. Note that the repository contains the file ``.env.example`` as an example of how to set up your local ``.env`` file. The parameters in the example file should be copied to your local `.env` file and updated as necessary. In particular, you must ensure that ``DJANGO_ALLOWED_HOSTS`` and ``DJANGO_CSRF_TRUSTED_ORIGINS`` are set to ``localhost`` for local development and are updated for your development/production URLs. In production, remove ``localhost`` and set ``DEBUG=True`` to ``DEBUG=False``.

10. Run database migrations:

.. code-block:: bash

    make migrate

The application should now be ready to run.

Install pre-commmit hooks
~~~~~~~~~~~~~~~~~~~~~~~~~

The project uses `pre-commit <https://pre-commit.com/>`_ to install and manage commit hooks to ensure consistently formatted code during development. To install, run:

.. code-block:: bash

    pre-commit install

Current hooks include Black for Python formatting, isort for standardized imports, djhtml for consistent indentation in templates, and prettier for Javascript, CSS, and related files.

Using the Makefile for common tasks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``Makefile`` contains several common tasks for development. The following are available: 

- ``make migrate``: Run database migrations.
- ``make mm``: Create a new migration.
- ``make preview``: Run the local server. 
- ``make test``: Run the test suite.
- ``make check``: Run the Django check command.

Unit Tests
----------

Python tests are written with `py.test <http://doc.pytest.org/>`_ and should be run with ``pytest``. To run a test, make sure to call pytest with poetry (e.g., ``poetry run pytest``).

Server Installation 
===================

1. Install and activate Python 3.11.0. It's recommended to use ``pyenv``
2. Create the PostgreSQL database and user for the project. The database name and user name should be the same as the project name.
3. Install `Poetry <https://python-poetry.org/docs/>`_ for Python dependency management.
4. Once you have Poetry, install required Python dependencies as described above. 
5. Install `Volta <https://volta.sh/>`_ for Node version management and install required Javascript dependencies as described above.
6. Set secrets to a local ``.env`` file as described above.
7. Then, update your ``settings.py`` file as described above.
8. Run database migrations. Note that there are helpers in the Makefile.
9. Create a superuser account for sysadmin. You can do this with the following command:

.. code-block:: bash

    python manage.py createsuperuser

10. Once the database and dependencies are ready, we need to load in the data. There are two ways to do this. 

Loading data from spreadsheets
-------------------------------

If you are loading data from spreadsheets, the following steps are necessary.  See more details below under the heading "Data Importing."

1. Before we can run a data import, a fixture must be installed. The fixture is located in the `postcards/fixtures` directory. To install the fixture, run the following command:

.. code-block:: bash

    poetry run python manage.py loaddata postcards/fixtures/languages.yaml

2. Next, any images that need to be associated with data in the database must be added to the ``/static/uploads`` directory.

3. Then, we can load the data in order of the commands listed below (locations, transcriptions, tags, objects, and images). The postal data is stored in an Excel file (see the Project Manager for access) and should be run on the sheet called "Database ready." To load the data, run the following command (there are default values in the ``Makefile`` if you use the helper commands such as ``make loadobjects``):
  
.. code-block:: bash

    poetry run python manage.py load_objects --filepath="./arnhem.xlsx" --sheet="Database ready"
    poetry run python manage.py load_locations --filepath="./arnhem.xlsx" --sheet="Database ready"
    poetry run python manage.py load_transcriptions --filepath="./arnhemv.xlsx" --sheet="Database ready"
    poetry run python manage.py load_tags --filepath="./arnhemv.xlsx" --sheet="Database ready"
    poetry run python manage.py load_objects --filepath="./arnhemv.xlsx" --sheet="Database ready"`
    poetry run python manage.py populate_images

4. Once these steps are complete, the current set of working data should be available.

Loading data from the PostgreSQL dump
--------------------------------------

1. If you are loading data from a PostgreSQL dump, you will need to have access to the dump file (``arnhem.sql``). The dump file should be placed in the root directory of the project.
2. To load the data, run the following command:

.. code-block:: bash
  psql -U <username> -d <database> -f arnhem.sql

3. The data should now be loaded into the database. You may have to run the ``populate_images`` command to associate images with their appropriate records.

Data Models 
===========

Detailed `model and database documentation <https://dbdocs.io/hepplerj/Arnhem-Postal>`_ is autogenerated and hosted via dbdocs.io.

Data Importing
==============

There are several import scripts available for getting data into the system. They will not likely be used since the RRCHNM team will be providing a PostgreSQL dump of the data, but are available if data importing is happening from scratch.

The import scripts are designed to load data from an Excel file into the database. It performs the following actions:

1. Reads data from the Excel file using ``pandas``.
2. Iterates through each row of the data, creating or updating model instances.
3. Handles various data validations for date fields, notes, and postmark information.
4. Associates postcards with people, collections, and postmark information.

Usage
------

The management scripts are located in the ``postcards/management/commands`` directory. To load all data from scratch, they must be run in the following order: 

1. ``poetry run python manage.py loaddata languages.yaml``: Load the languages fixture.
2. ``poetry run python manage.py load_locations --filepath="./arnhemv.xlsx" --sheet="Database ready``: Load the locations from the spreadsheet.
3. ``poetry run python manage.py load_transcriptions --filepath="./arnhemv.xlsx" --sheet="Database ready"``: Load the transcriptions from the spreadsheet.
4. ``poetry run python manage.py load_tags --filepath="./arnhemv.xlsx" --sheet="Database ready"``: Load the tags from the spreadsheet.
5. ``poetry run python manage.py load_objects --filepath="./arnhemv.xlsx" --sheet="Database ready"``: Load the objects from the spreadsheet.
6. ``poetry run python manage.py populate_images``: Load images that are stored in the ``static/upload`` directory.

Deploying with Docker 
=====================

- Docker 17.05+
- Docker Compose 1.20+

Using Docker
------------

Note in the root of the project two files: 

- ``docker-compose.yml``: This file is the main configuration file for the Docker setup. It defines the services that will be run in the Docker containers. 
- ``docker-compose.yml.j2``: This file is a Jinja2 template that is used to generate the actual ``docker-compose.yml`` file. This file is used to generate the actual configuration file that is used to run the Docker containers.

To get started, the following steps are necessary.

1. First, build the Docker stack with the following command (you can also consult the Makefile for frequently used Docker commands):

.. code-block:: bash
  docker-compose build

2. Then, you can run the stack with the following command, which will start the Django application and the PostgreSQL database:

.. code-block:: bash
  docker-compose up

To run the Docker container in detached mode, run the following command: 

.. code-block:: bash
  docker-compose up -d

