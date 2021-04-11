import logging
from flask_cors import cross_origin
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from ecommerce_api.model.product import Product
from ecommerce_api.model.coupon import Coupon
from ecommerce_api.api.rest.schema import product, coupon
from ecommerce_api.resources import db
from ecommerce_api.utils import create_api_blueprint
from ecommerce_api.api.auth import auth_required

actions = create_api_blueprint('attach', 'action', 'v1')
LOGGER = logging.getLogger(__name__)

@actions.route('/coupons', methods=['POST'])
@cross_origin()
@auth_required()
def _attach(auth_data=None):
  """Action to create the relations
  with product and coupons

  Args:
      auth_data ([type], optional): [description]. Defaults to None.

  Returns:
      str: operations message
  """
  _request = request.get_json(silent=True)
  _product = _request.get('product' or None)

  if _product:
    _coupons = _request.get('coupons' or None)

    product_ = Product.query.filter(Product.id == _product['id']).first()
    product_.coupons.clear()
    for c in _coupons:
      coupon_ = Coupon.query.filter(Coupon.id == c['id']).first()
      if coupon_:
        product_.coupons.append(coupon_)
    
    try:
      db.session.add(product_)
      db.session.commit()
    except IntegrityError as ex:
      db.session.rollback()
      LOGGER.exception(ex)
      return {'error': ex}, 422
    

    return 'success', 200
