from marshmallow import fields
from ecommerce_api.api.rest.schema import BaseSchema


class ProductSchema(BaseSchema):
  name = fields.String()
  description = fields.String()
  price = fields.Decimal(as_string=True)
  
  coupons = fields.Nested('CouponSchema', exclude=('products',), many=True)
