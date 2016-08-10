Authentication api
------------------

Allows to authenticate user or get current authenticated user.

CHANGELOG:

- 2016-08-01 (v1.1.0): require `email` instead of `username`
- 2016-08-01 (v1.0.0): added endpoint

----

Current user's state
====================

``GET /api/1.1.0/login``

**Response:**

.. code:: json

    {
        "status": "OK",
        "msg": null,
        "code": 0,
        "data": {
            "username": "test_user",
            "email": "test_user@example.com",
            "isAuthenticated": true,
            "id": 1
        }
    }

----


Login action
============

``POST /api/1.1.0/login``

**Payload:**

Accepts:

- `email`
- `password`

.. code:: json

    {
        "email": "test_user@example.com",
        "password": "test_pass"
    }

**Response:**

.. code:: json

    {
        "status": "OK",
        "msg": null,
        "code": 0,
        "data": {
            "username": "test_user",
            "email": "test_user@example.com",
            "isAuthenticated": true,
            "id": 1
        }
    }

