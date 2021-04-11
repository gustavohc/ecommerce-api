import jwt
import logging
from flask import request, jsonify
from functools import wraps

from ecommerce_api.config import Config

LOGGER = logging.getLogger(__name__)


def get_auth_data():
    """
    Verifica se tem usuario atenticado de acordo com o tipo de autenticação.
    :return:
    """
    authorization = request.headers.get('authorization')
    if not authorization:
        return None
    token = authorization.split(' ')
    if token[0] != 'Bearer':
      return None

    auth_data = {}
    try:
        # User authentication
        auth_data['user'] = jwt.decode(token[1], Config.SECRET_KEY)
        auth_data['type'] = 'user'
        
        return auth_data
    except Exception as exc:
        LOGGER.error("AUTH DATA: %s" % exc)
        return None


def auth_required(*args, **kwargs):
  """
  Decorator que verifica o token de autenticação informado na requisição.
  Excemplo de utilização:

  @actions.route('/me', methods=['POST'])
  @auth_required('user', roles_allowed=['master'])
  def me(auth_data=None):
      return {'name': 'josé'}

  :param args:
  :param kwargs:
  :return:
  """
  def wrapper(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
      unauthorized = jsonify(error='Unauthorized'), 401

      auth_data = get_auth_data()
      if auth_data is None:
          return unauthorized

      kwargs['auth_data'] = auth_data
      return fn(*args, **kwargs)
    return decorator
  return wrapper