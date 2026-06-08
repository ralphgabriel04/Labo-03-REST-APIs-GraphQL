"""
Tests for orders manager
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import pytest
from store_manager import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    result = client.get('/health-check')
    assert result.status_code == 200
    assert result.get_json() == {'status':'ok'}

def test_stock_flow(client):
    # 1. Creez un article (POST /products)
    product_data = {'name': 'Some Item', 'sku': '12345', 'price': 99.90}
    response = client.post('/products',
                          data=json.dumps(product_data),
                          content_type='application/json')
    assert response.status_code == 201
    product_id = response.get_json()['product_id']
    assert product_id > 0

    # 2. Ajoutez 5 unites au stock de cet article (POST /stocks)
    stock_data = {'product_id': product_id, 'quantity': 5}
    response = client.post('/stocks',
                          data=json.dumps(stock_data),
                          content_type='application/json')
    assert response.status_code == 201

    # 3. Verifiez le stock: 5 unites (GET /stocks/:id)
    response = client.get(f'/stocks/{product_id}')
    assert response.status_code == 200
    assert response.get_json()['quantity'] == 5

    # 4. Faites une commande de 2 unites (POST /orders)
    order_data = {'user_id': 1, 'items': [{'product_id': product_id, 'quantity': 2}]}
    response = client.post('/orders',
                          data=json.dumps(order_data),
                          content_type='application/json')
    assert response.status_code == 201
    order_id = response.get_json()['order_id']
    assert order_id > 0

    # 5. Verifiez le stock encore une fois: 5 - 2 = 3 unites
    response = client.get(f'/stocks/{product_id}')
    assert response.status_code == 200
    assert response.get_json()['quantity'] == 3

    # 6. Etape extra: supprimez la commande et verifiez le stock (doit remonter a 5)
    response = client.delete(f'/orders/{order_id}')
    assert response.status_code == 200

    response = client.get(f'/stocks/{product_id}')
    assert response.status_code == 200
    assert response.get_json()['quantity'] == 5
