from flask import Flask
from src.parts import parts_bp

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secret'
app.register_blueprint(parts_bp)

if __name__ == "__main__":
    app.run(debug=True)
