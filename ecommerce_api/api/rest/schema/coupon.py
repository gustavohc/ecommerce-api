from marshmallow import fields

from ecommerce_api.api.rest.schema import BaseSchema


class CouponSchema(BaseSchema):
  code = fields.String()
  discount_percent = fields.Decimal(as_string=True)
  discount_value = fields.Decimal(as_string=True)
