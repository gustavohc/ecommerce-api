from sqlalchemy import Column, String, DECIMAL
from sqlalchemy.orm import relationship

from ecommerce_api.model.base import ModelBase, AuditedModelBase
from ecommerce_api.resources import db


class Coupon(AuditedModelBase, ModelBase, db.Model):
  code = Column(String(64), nullable=False)
  discount_percent = Column(DECIMAL(
    precision=15, scale=2, asdecimal=False
  ))
  discount_value = Column(DECIMAL(
    precision=15, scale=2, asdecimal=False
  ))

  products = relationship('Product', secondary='products_coupons')
