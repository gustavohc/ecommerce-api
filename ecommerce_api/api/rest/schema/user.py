from marshmallow import fields

from ecommerce_api.api.rest.schema import BaseSchema


class UserSchema(BaseSchema):
  username = fields.String()
  password = fields.String()
