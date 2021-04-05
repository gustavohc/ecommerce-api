from marshmallow import fields
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class BaseSchema(ma.Schema):
  id = fields.Integer()
  created_at = fields.DateTime('%Y-%m-%dT%H:%M:%S')
  updated_at = fields.DateTime('%Y-%m-%dT%H:%M:%S')
