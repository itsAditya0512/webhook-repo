from flask import Flask
from app.extensions import mongo
from app.webhook.routes import webhook  # This is the Blueprint object

def create_app(template_folder=None):
    app = Flask(__name__, template_folder=template_folder or "templates")
    
    # MongoDB configuration
    app.config["MONGO_URI"] = "mongodb+srv://admin:admin@cluster0py.kkxwtyy.mongodb.net/webhookDB?retryWrites=true&w=majority"
    
    # Initialize Mongo with Flask app
    mongo.init_app(app)
    
    # Register blueprint
    app.register_blueprint(webhook)
    
    return app
