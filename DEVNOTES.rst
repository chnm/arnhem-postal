Development Instructions
========================

Setup and installation
-----------------------

Initial setup and installation:

- Install and activate Python 3.11.0. It's recommended to use `pyenv <https://github.com/pyenv/pyenv>`_ for this.

- Install `Poetry <https://python-poetry.org/docs/>` _ for Python dependency management.

- Once you have Poetry, install required Python dependencies::

.. code-block:: bash

    poetry install

- Use `Volta <https://volta.sh/>`_ for Node version management

- Install required Javascript dependencies::

.. code-block:: bash

    npm install

- Set secrets to a local `.env` file::

.. code-block:: bash

    % echo DEBUG=True >> .env
    % echo DJANGO_SECRET_KEY=$(poetry run python -c "import secrets; print(secrets.token_urlsafe())") >> .env

- Then, update your settings.py file.

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

- Create a new database and update your database settings accordingly

- Run database migrations::

.. code-block:: bash

    make migrate

Install pre-commmit hooks
~~~~~~~~~~~~~~~~~~~~~~~~~

The project uses `pre-commit <https://pre-commit.com/>`_ to install and manage commit hooks to ensure consistently formatted code. To install, run::

.. code-block:: bash
    
    pre-commit install

Current hooks include Black for Python formatting, isort for standardized imports, djhtml for consistent indentation in templates, and prettier for Javascript, CSS, and related files.

Unit Tests
----------

Python tests are written with `py.test <http://doc.pytest.org/>`_
and should be run with ``pytest``. To run a test, make sure to call pytest with poetry.


Models 
======

Object Model
------------

The `Object` model represents a postcard object and is defined as follows:

- `title`: CharField, the title of the postcard.
- `description`: TextField, a detailed description of the postcard.
- `date_received`: DateField, the date the postcard was received.
- `date_sent`: DateField, the date the postcard was sent.
- `date_of_correspondence`: DateField, the date of correspondence.
- `notes`: TextField, additional notes about the postcard.
- `collection`: ManyToManyField to `Collection`, representing the collection(s) to which the postcard belongs.
- `postmark`: ManyToManyField to `Postmark`, representing postmark information associated with the postcard.

Collection Model
-----------------

The `Collection` model represents a collection to which postcards belong and is defined as follows:

- `name`: CharField, the name of the collection.

Location Model
-----------------

The `Location` model represents a town or city associated with postmark information and is defined as follows:

- `town_city`: CharField, the name of the town or city.

Postmark Model
----------------

The `Postmark` model represents postmark information and is defined as follows:

- `location`: ForeignKey to `Location`, representing the town or city where the postmark was made.
- `date`: DateField, the date of the postmark.
- `ordered_by_arrival`: IntegerField, indicating the order of arrival (e.g., 1 for postmark 1, 2 for postmark 2).

Import Script
==============

The import script (`load_objects.py`) is designed to load postcard data from an Excel file into the database. It performs the following actions:

1. Reads data from the Excel file using `pandas`.
2. Iterates through each row of the data, creating or updating `Object` instances.
3. Handles various data validations for date fields, notes, and postmark information.
4. Associates postcards with people, collections, and postmark information.

Usage
------

To use the script, run the following command:

.. code-block:: bash
    python manage.py load_objects path/to/excel/file.xlsx
