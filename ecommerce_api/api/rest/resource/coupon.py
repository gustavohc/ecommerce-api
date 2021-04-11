from ecommerce_api.model.coupon import Coupon
from ecommerce_api.api.rest.schema.coupon import CouponSchema
from ecommerce_api.api.rest.resource import BaseResource

class CouponResource(BaseResource):
  def __init__(self):
    BaseResource.__init__(self, Coupon)

  def _methods(self):
    return {
        'GET': self.check_authentication(),
        'POST': self.check_authentication(),
        'QUERY': self.check_authentication(),
        'PATCH': self.check_authentication(),
        'DELETE': self.check_authentication(),
    }

  def _schema(self, method):
    return CouponSchema

  def _make_query(self, query):

    return query