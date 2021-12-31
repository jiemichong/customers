import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
if os.environ.get('db_conn'):
    uri = os.environ.get('db_conn') + '/customer'
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = None
# uri = 'mysql+mysqlconnector://cs302:cs302@host.docker.internal:3306/customer'
# app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 100,
                                           'pool_recycle': 280}

db = SQLAlchemy(app)

CORS(app)


class Customer(db.Model):
    __tablename__ = 'customer'

    cust_id = db.Column(db.Integer, primary_key=True)
    cust_name = db.Column(db.String(225), nullable=False)
    cust_phone = db.Column(db.Integer, nullable=False)
    cust_email = db.Column(db.String(225), nullable=False)

    def __init__(self, cust_name, cust_phone, cust_email):
        self.cust_name = cust_name
        self.cust_phone = cust_phone
        self.cust_email = cust_email

    def to_dict(self):
        return {
            "cust_id": self.cust_id,
            "cust_name": self.cust_name,
            "cust_phone": self.cust_phone,
            "cust_email": self.cust_email
        }


@app.route("/health")
def health_check():
    return jsonify(
        {
            "message": "Customers service is healthy."
        }
    ), 200


@app.route("/customer")
def get_all():
    cust_list = Customer.query.all()
    if len(cust_list) != 0:
        return jsonify(
            {
                "data": {
                    "customers": [customer.to_dict() for customer in cust_list]
                }
            }
        ), 200
    return jsonify(
        {
            "message": "There are no customers."
        }
    )


@app.route("/customer/<int:cust_id>")
def find_by_id(cust_id):
    cust = Customer.query.filter_by(cust_id=cust_id).first()
    if cust:
        return jsonify(
            {
                "data": cust.to_dict()
            }
        ), 200
    return jsonify(
        {
            "message": "Customer not found."
        }
    ), 404


@app.route("/customer/<string:cust_email>")
def find_by_email(cust_email):
    cust = Customer.query.filter_by(cust_email=cust_email).first()
    if cust:
        return jsonify(
            {
                "data": cust.to_dict()
            }
        ), 200
    return jsonify(
        {
            "message": "Customer not found."
        }
    ), 404


@app.route("/customer", methods=['POST'])
def new_cust():
    try:
        data = request.get_json()
        cust = Customer(**data)
        db.session.add(cust)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred creating the customer.",
                "error": str(e)
            }
        ), 500

    return jsonify(
        {
            "data": cust.to_dict()
        }
    ), 201


@app.route("/customer/<int:cust_id>", methods=['PATCH'])
def update_cust(cust_id):
    cust = Customer.query.filter_by(cust_id=cust_id).first()
    if cust is None:
        return jsonify(
            {
                "data": {
                    "cust_id": cust_id
                },
                "message": "Customer not found."
            }
        ), 404
    data = request.get_json()
    if 'cust_name' in data.keys():
        cust.cust_name = data['cust_name']
    if 'cust_phone' in data.keys():
        cust.cust_phone = data['cust_phone']
    if 'cust_email' in data.keys():
        cust.cust_email = data['cust_email']
    try:
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred in updating the customer.",
                "error": str(e)
            }
        ), 500
    return jsonify(
        {
            "data": cust.to_dict()
        }
    ), 200


@app.route("/customer/<int:cust_id>", methods=['DELETE'])
def delete_cust(cust_id):
    cust = Customer.query.filter_by(cust_id=cust_id).first()
    if cust is not None:
        try:
            db.session.delete(cust)
            db.session.commit()
        except Exception as e:
            return jsonify(
                {
                    "message": "An error occurred deleting the customer.",
                    "error": str(e)
                }
            ), 500
        return jsonify(
            {
                "data": {
                    "cust_id": cust_id
                }
            }
        ), 200
    return jsonify(
        {
            "data": {
                "cust_id": cust_id
            },
            "message": "Customer not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
