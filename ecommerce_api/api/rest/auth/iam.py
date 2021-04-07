import logging
import base64
import hashlib
import hmac
import jwt

from flask import Blueprint, request, redirect, jsonify, current_app
from passlib.context import CryptContext

from ecommerce_api.resources import db
from ecommerce_api.model.user import User

LOGGER = logging.getLogger(__name__)


# Error codes
SIGN_UP_MISSING_FIELDS = 4000
SIGN_IN_MISSING_FIELDS = 4001
USER_DOES_NOT_EXIST = 4002
INVALID_AUTHENTICATION = 4003


class _ApiError(Exception):
  """Representa um erro à ser retornado para o cliente"""

  def __init__(self, status_code=None, code=None, description=None, data=None):
      # Código http
      self._status_code = status_code

      # Código interno
      self._code = code

      # Descrição breve do erro
      self._description = description

      # Algum conteudo extra para ser retornado
      self._data = data

  @property
  def status_code(self):
      return self._status_code

  @property
  def code(self):
      return self._code

  @property
  def description(self):
      return self._description

  @property
  def data(self):
      return self._data


class Iam():
  def __init__(self):
        self.app = None
        self.__url_prefix = None
        self.__session = None
        self.__secret = None
        self.__crypt_context = CryptContext(
          schemes=['bcrypt', 'des_crypt', 'pbkdf2_sha256', 'pbkdf2_sha512', 'sha256_crypt', 'sha512_crypt', 'plaintext'], 
          default='sha512_crypt', deprecated=['auto']
        )


  def init_app(self, app, url_prefix=None):
        self.app = app
        self.__session = db.session
        self.__salt = self.app.config['PASSWORD_SALT']

        if url_prefix:
            if not url_prefix.startswith('/'):
                url_prefix = "/" + str(url_prefix)

            self.__url_prefix = str(url_prefix)

        # self._agrinvest_auth.init_app(app, auth_apps)

        app.register_blueprint(self.__create_blueprint())

  def __create_blueprint(self):
    blueprint = Blueprint(
      'iam',
      __name__,
      url_prefix=self.__url_prefix
    )
    blueprint.route('/login', methods=['POST'])(self.__login)

    return blueprint

  def generate_token(self, user):
    """Generate a JWT toker for user authentication"""

    payload = {
        'id': user.id,
        'username': user.username,
    }
    return jwt.encode(payload, self.app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

  
  def __get_hmac(self, password):
    """NOTE: Copy from flask-securty"""

    password_salt = self.__salt

    h = hmac.new(password_salt.encode('utf-8'), password.encode('utf-8'), hashlib.sha512)
    return base64.b64encode(h.digest())

  def encrypt_password(self, password):
    """NOTE: Copy from flask-securty

    This function encrypt the password to be save in DB
    """

    signed = self.__get_hmac(password)
    return self.__crypt_context.hash(signed)

  
  def __verify_and_updated_password(self, password, user):
    """Check if passwork is the same as in database
    """

    if self.__crypt_context.identify(user.password) != 'plaintext':
        password = self.__get_hmac(password)

    verified, new_password = self.__crypt_context.verify_and_update(password, user.password)
    if verified and new_password:
        user.password = self.encrypt_password(password)
        self.__session.add(user)
        self.__session.commit()

    return verified

  
  def __login(self, _type=None):
    """
    Process to sigin the user
    """

    data = request.get_json()

    required_fields = [
      'username',
      'password'
    ]
    for field in required_fields:
      if field not in data or not data[field]:
        raise _ApiError(
          status_code=400,
          code=SIGN_IN_MISSING_FIELDS,
          description='Enter username and password'
        )

    username = data['username']
    password = data['password']
    user = User.query.filter(User.username == username).first()
    LOGGER.info('User found!')

    if not user:
      raise _ApiError(status_code=404, code=USER_DOES_NOT_EXIST, description='User does not exist')

    if not self.__verify_and_updated_password(password, user):
      LOGGER.exception('Invalid password')
      raise _ApiError(status_code=422, code=INVALID_AUTHENTICATION, description='Invalid authentication')

    return jsonify({
      'token': self.generate_token(user)
    })
