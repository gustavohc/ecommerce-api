from sqlalchemy import (
  Column, 
  String, 
  Text, 
  DECIMAL, 
)
from sqlalchemy.orm import relationship

from ecommerce_api.model.base import ModelBase, AuditedModelBase
from ecommerce_api.resources import db

products_coupons = db.Table(
  'products_coupons',
  db.Column('product_id', db.Integer(), db.ForeignKey('product.id')),
  db.Column('coupon_id', db.Integer(), db.ForeignKey('coupon.id'))
)


class Product(AuditedModelBase, ModelBase, db.Model):
  name = Column(String(256), nullable=False)
  description = Column(Text)
  price = Column(DECIMAL(
    precision=15, scale=2, asdecimal=False
  ), nullable=False)

  coupons = relationship('Coupon', secondary=products_coupons)
