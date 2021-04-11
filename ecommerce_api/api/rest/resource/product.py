from ecommerce_api.model.product import Product
from ecommerce_api.api.rest.schema.product import ProductSchema
from ecommerce_api.api.rest.resource import BaseResource

class ProductResource(BaseResource):
  def __init__(self):
    BaseResource.__init__(self, Product)

  def _methods(self):
    return {
        'GET': self.check_authentication(),
        'POST': self.check_authentication(),
        'QUERY': self.check_authentication(),
        'PATCH': self.check_authentication(),
        'DELETE': self.check_authentication(),
    }

  def _schema(self, method):
    return ProductSchema

  def _make_query(self, query):

    return query