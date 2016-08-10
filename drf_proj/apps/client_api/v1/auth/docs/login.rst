Authentication api
------------------

Allows to authenticate user or get current authenticated user.

CHANGELOG:

- 2016-08-01 (v1.0.0): added endpoint

----

Current user's state
====================

``GET /api/login``

**Response:**

.. code:: json

    {
        "status": "OK",
        "msg": null,
        "code": 0,
        "data": {
            "username": "newtestuser123",
            "email": "newtestuser123@example.com",
            "isAuthenticated": true,
            "id": 1
        }
    }

----


Login action
============

``POST /api/1.0.0/login``

**Payload:**

Accepts:

- `email`
- `password`

.. code:: json

    {
        "username": "newtestuser123",
        "password": "qwerty321"
    }

**Response:**

.. code:: json

    {
        "status": "OK",
        "msg": null,
        "code": 0,
        "data": {
            "username": "newtestuser123",
            "email": "newtestuser123@example.com",
            "isAuthenticated": true,
            "id": 1
        }
    }

