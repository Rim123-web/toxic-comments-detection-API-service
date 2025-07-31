from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import joblib
import numpy as np
from flask_cors import CORS
from config import Config

# Import models
from models import db, User, APIKey, UsageLog
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


# === Flask App Setup ===
app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500"], supports_credentials=True)

app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

 
admin = Admin(app, name='Toxicity Admin')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(APIKey, db.session))
admin.add_view(ModelView(UsageLog, db.session))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///toxicity.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.config.from_object(Config)

# === Load ML model ===
model = joblib.load('xgb_model.joblib')
vectorizer = joblib.load('tfidf_vectorizer.joblib')


# === Create all DB tables ===
with app.app_context():
    db.create_all()

# === Config ===
MAX_REQUESTS = 2000  # Free requests per API key


# === Home Route ===
@app.route('/')
def home():
    return jsonify({"message": "✅ Toxicity Detection API is live"})


# === Register Route ===
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    role = data.get("role")
    organization = data.get("organization")
    project_purpose = data.get("project_purpose")
    country = data.get("country")
    agreed_terms = data.get("agreed_terms")

    # Validate input
    required_fields = [username, email, role, organization, project_purpose, country, agreed_terms]
    if not all(required_fields):
        return jsonify({"error": "All fields are required."}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Username or email already exists."}), 400

    if agreed_terms is not True:
        return jsonify({"error": "You must agree to the terms to register."}), 400

    # Create user (password removed intentionally, since you want simple API key)
    user = User(
        username=username,
        email=email,
        role=role,
        organization=organization,
        project_purpose=project_purpose,
        country=country,
        agreed_terms=True
    )
    db.session.add(user)
    db.session.commit()

    # Generate API key
    api_key = APIKey(user_id=user.id)
    db.session.add(api_key)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully.",
        "api_key": api_key.key
    }), 201



from flask import request, jsonify
from datetime import datetime
import numpy as np

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    api_key_str = data.get("api_key")

    if not api_key_str:
        return jsonify({"error": "API key required"}), 400

    api_key = APIKey.query.filter_by(key=api_key_str, revoked=False).first()
    if not api_key:
        return jsonify({"error": "Invalid or revoked API key"}), 403

    usage_count = UsageLog.query.filter_by(api_key_id=api_key.id).count()
    total_allowed = MAX_REQUESTS + api_key.paid_requests

    if usage_count >= total_allowed:
        return jsonify({
            "error": "You’ve reached your request limit. Please upgrade or purchase more.",
            "requests_used": usage_count,
            "allowed": total_allowed
        }), 429

    # Log the request
    usage_log = UsageLog(api_key_id=api_key.id, timestamp=datetime.utcnow())
    db.session.add(usage_log)
    db.session.commit()

    # === Text-Based Prediction ===
    try:
        text = data["text"]
        X_input = vectorizer.transform([text])  # vectorize using trained TF-IDF
        prediction = model.predict(X_input)[0]
        probability = model.predict_proba(X_input)[0][1]
    except KeyError:
        return jsonify({"error": "Missing required field: 'text'"}), 400

    return jsonify({
        "prediction": int(prediction),
        "probability_toxic": float(probability),
        "requests_used": usage_count + 1,
        "requests_remaining": total_allowed - usage_count - 1
    })



# === Buy Paid Requests (Simulated Payment) ===
@app.route('/buy-requests', methods=['POST'])
def buy_requests():
    data = request.get_json()
    api_key_str = data.get("api_key")
    amount = int(data.get("amount", 0))

    if not api_key_str or amount <= 0:
        return jsonify({"error": "API key and amount > 0 required."}), 400

    api_key = APIKey.query.filter_by(key=api_key_str, revoked=False).first()
    if not api_key:
        return jsonify({"error": "Invalid or revoked API key"}), 403

    api_key.paid_requests += amount
    db.session.commit()

    return jsonify({
        "message": f"{amount} paid requests added.",
        "total_paid_requests": api_key.paid_requests
    })


# === Run App ===
if __name__ == '__main__':
    app.run(debug=True)
@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200  # Handle CORS preflight

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password."}), 401

    api_key = APIKey.query.filter_by(user_id=user.id, revoked=False).first()
    if not api_key:
        api_key = APIKey(user_id=user.id)
        db.session.add(api_key)
        db.session.commit()

    return jsonify({
        "message": "Login successful.",
        "api_key": api_key.key,
        "username": user.username,
        "user_id": user.id
    }), 200



from flask import Flask, request, jsonify
from models import db, User, APIKey

@app.route('/api/recover', methods=['POST'])
def recover_api_key():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if user and user.api_keys:
        keys = [key.key for key in user.api_keys if not key.revoked]
        if keys:
            return jsonify({'api_keys': keys}), 200
        else:
            return jsonify({'error': 'No active API keys found'}), 404
    else:
        return jsonify({'error': 'User not found'}), 404
