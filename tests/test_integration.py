import json
import pytest


def call(client, path, method='GET', body=None):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }

    if method == 'POST':
        response = client.post(path, data=json.dumps(body), headers=headers)
    elif method == 'PUT':
        response = client.put(path, data=json.dumps(body), headers=headers)
    elif method == 'PATCH':
        response = client.patch(path, data=json.dumps(body), headers=headers)
    elif method == 'DELETE':
        response = client.delete(path)
    else:
        response = client.get(path)

    return {
        "json": json.loads(response.data.decode('utf-8')),
        "code": response.status_code
    }


@pytest.mark.dependency()
def test_health(client):
    result = call(client, 'health')
    assert result['code'] == 200


@pytest.mark.dependency()
def test_get_all(client):
    result = call(client, 'customer')
    assert result['code'] == 200
    assert result['json']['data']['customers'] == [
        {
            "cust_id": 1,
            "cust_name": "Carmen Yip",
            "cust_phone": 98765432,
            "cust_email": "carmenyip@abc.com"
        },
        {
            "cust_id": 2,
            "cust_name": "Nikki Poo",
            "cust_phone": 97654321,
            "cust_email": "nikkipoo@abc.com"
        },
        {
            "cust_id": 3,
            "cust_name": "Jie Mi",
            "cust_phone": 96543218,
            "cust_email": "jiemi@abc.com"
        }
    ]


@pytest.mark.dependency(depends=['test_get_all'])
def test_one_valid(client):
    result = call(client, 'customer/2')
    assert result['code'] == 200
    assert result['json']['data'] == {
        "cust_id": 2,
        "cust_name": "Nikki Poo",
        "cust_phone": 97654321,
        "cust_email": "nikkipoo@abc.com"
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_one_invalid(client):
    result = call(client, 'customer/55')
    assert result['code'] == 404
    assert result['json'] == {
        "message": "Customer not found."
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_update_existing_customer(client):
    result = call(client, 'customer/1', 'PATCH', {
        "cust_email": "carmen@abc.com"
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "cust_id": 1,
        "cust_name": "Carmen Yip",
        "cust_phone": 98765432,
        "cust_email": "carmen@abc.com"
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_update_nonexisting_customer(client):
    result = call(client, 'customer/555', 'PATCH', {
        "cust_name": "Sin Yee"
    })
    assert result['code'] == 404


@pytest.mark.dependency(depends=['test_get_all'])
def test_create_no_body(client):
    result = call(client, 'customer', 'POST', {})
    assert result['code'] == 500


@pytest.mark.dependency(depends=['test_get_all', 'test_create_no_body'])
def test_create_one_customer(client):
    result = call(client, 'customer', 'POST', {
        "cust_name": "Sin Yee",
        "cust_phone": 96647332,
        "cust_email": "sinyee@abc.com"
    })
    assert result['code'] == 201
    assert result['json']['data'] == {
        "cust_id": 4,
        "cust_name": "Sin Yee",
        "cust_phone": 96647332,
        "cust_email": "sinyee@abc.com"
    }


@pytest.mark.dependency(depends=['test_create_one_customer'])
def test_update_new_customer(client):
    call(client, 'customer', 'POST', {
        "cust_name": "Sin Yee",
        "cust_phone": 96647332,
        "cust_email": "sinyee@abc.com"
    })
    result = call(client, 'customer/4', 'PATCH', {
        "cust_phone": 96345678,
        "cust_email": "sinyeekwek@abc.com"
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "cust_id": 4,
        "cust_name": "Sin Yee",
        "cust_phone": 96345678,
        "cust_email": "sinyeekwek@abc.com"
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_delete_customer(client):
    result = call(client, 'customer/2', 'DELETE')
    assert result['code'] == 200
    assert result['json']['data'] == {
        "cust_id": 2
    }


@pytest.mark.dependency(depends=['test_delete_customer'])
def test_deleted_customer(client):
    call(client, 'customer/2', 'DELETE')
    result = call(client, 'customer/2', 'GET')
    assert result['code'] == 404
    assert result['json'] == {
        "message": "Customer not found."
    }
