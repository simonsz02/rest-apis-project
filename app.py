import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from db import db
from blocklist import BLOCKLIST
import models # __init__.py file is the default place where you import when you import a package

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

# factory pattern
def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['API_TITLE'] = "Stores REST API"
    app.config['API_VERSION'] = "v1"
    app.config['OPENAPI_VERSION'] = "3.0.3"
    app.config['OPENAPI_URL_PREFIX'] = "/"
    app.config['OPENAPI_SWAGGER_UI_PATH'] = "/swagger-ui"
    app.config['OPENAPI_SWAGGER_UI_URL'] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    # all database providers, such as MySQL, Postgres, SQLite or any other use a connection string 
    # that has all the necessary information for a client to connect to a database.
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # initializes the Flask SQLAlchemy extension, giving it our Flask app so that 
    # it can connect the Flask app to SQLAlchemy.
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app) # connects the flask-smorest extention to flask app

    app.config["JWT_SECRET_KEY"] = "323687083836848671134669988331181526019"
    # Secret key is used for signing the JWT. this is not the same as encryption.
    # When a user sends us back a JWT to tell us who they are.
    # Our app can check the secret key and can use it to verify that this app generated thaz JWT
    # Therefore the JWT is valid.
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        # whenever we receive a jwt, this function runs 
        # and it checks if the token in the blocklist
        # if function returns true, than the request is terminated and the user will get an error 
        # that says the token has been revoked.
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return(
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return{
            jsonify(
            {
                "description": "The token is not fresh.",
                "error": "fresh_token_required",
            }
            ),
            401,
        }

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required"
                }
            ),
            401,
        )
    
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app