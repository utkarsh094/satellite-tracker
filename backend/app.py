from flask import Flask
from flask_cors import CORS
import config
from api.routes import api

app = Flask(__name__)
CORS(app)
app.register_blueprint(api)

@app.route("/")
def index():
    return {
        "status": "ok",
        "message": "Satellite tracker API is running.",
        "endpoints": ["/satellites", "/track?sat=<norad_id>"],}
if __name__ == "__main__":
    app.run(host=config.API_HOST, port=config.API_PORT, debug=True)