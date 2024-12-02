from flask import Flask, jsonify
from datetime import datetime

def create_app():
    app = Flask(__name__)
    
    # Import and register blueprints
    from .resources.clickup import clickup_bp
    
    app.register_blueprint(clickup_bp, url_prefix='/api/clickup')

    # Add health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "message": "Server is up and running",
            "timestamp": datetime.now().isoformat()
        }), 200
    
    return app