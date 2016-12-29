
.. sectnum::
Parts Implemented by Alim Özdemir
================================

You can find all informations about images, locations and filters here.

General Database Design
-----------------------

ER DIAGRAM
~~~~~~~~~~
.. figure:: member3er.png


Images
------

Table
^^^^^

.. code-block:: sql
    CREATE TABLE IF NOT EXISTS images(
        image_id serial primary key,
        user_id int REFERENCES users(ID) ON DELETE CASCADE,
        path text ,
        time date ,
        text text
    );

Locations
---------

Table
^^^^^

.. code-block:: sql
    CREATE TABLE IF NOT EXISTS locations(
        Id serial primary key,
        name text,
        latitude numeric,
        longitude numeric,
        formatted_address text,
        rating real
    );

Filters
-------

Table
^^^^^

.. code-block:: sql
    CREATE TABLE IF NOT EXISTS filter(
        id serial primary key,
        name text,
        user_id int REFERENCES users (ID) ON DELETE CASCADE,
        Contrast int,
        Brightness int,
        Sharpness int,
        Blur int,
        UnsharpMask int
    );
