from ecommerce_api.model.user import User
from ecommerce_api.api.rest.schema.user import UserSchema
from ecommerce_api.api.rest.resource import BaseResource

class UserResource(BaseResource):
  def __init__(self):
    BaseResource.__init__(self, User)

  def _methods(self):
    return {
        'GET': True,
        'POST': True,
        'QUERY': True,
        'PATCH': True,
        'DELETE': True,
    }

  def _schema(self, method):
    return UserSchema

  def _make_query(self, query):

    return query