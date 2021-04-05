from ecommerce_api.api.rest.resource import (
  product,
  coupon,
  user
)

def create_json_api(api):
  api.add_resource(product.ProductResource, '/product/<id>', '/product')
  api.add_resource(coupon.CouponResource, '/coupon/<id>', '/coupon')
  api.add_resource(user.UserResource, '/user/<id>', '/user')
