Installiation Guide
===================

Following guide explains how to install and ready the postITU project.

After installing all the requirements user/developer can execute the website from the main directory with:

.. code-block:: python

    python server.py

Requirements:
    * Python_
    * Flask_
    * Psycopg2_
    * PostgreSQL_
    * flask_wtf_
    * googlemaps_
    * pillow_
    * passlib_

Python
------

Python can be found from the link: 

https://www.python.org/downloads/


Flask
-----

Flask can be installed from command line via:

pip install Flask

You need a working linux, or bash integrated windows command line to use pip.

Psycopg2
--------

Psycopg2 can be installed from command line via:

pip install psycopg2

PostgreSQL
----------

PostgreSQL is used to work on project locally without having to change the bluemix db all the time.

Can be downloaded from:

https://www.postgresql.org/download/

flask_wtf
---------

Another dependency which is used in the website.

pip install Flask-WTF

googlemaps
----------

Googlemaps needs to be integrated to website in order to see locations etc. Details about how to get an api key and use it can be found at the following link:

https://developers.google.com/maps/

pillow
------

Another dependency which is used in the website.

pip install pillow

passlib
-------

Another dependency which is used in the website.

pip install passlib