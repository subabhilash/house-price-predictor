from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship to predictions
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __repr__(self):
        return f'<User {self.username}>'

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # House features (matching your ML model)
    area = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    stories = db.Column(db.Integer, nullable=False)
    parking = db.Column(db.Integer, nullable=False)
    mainroad = db.Column(db.String(10), nullable=False)
    guestroom = db.Column(db.String(10), nullable=False)
    basement = db.Column(db.String(10), nullable=False)
    hotwaterheating = db.Column(db.String(10), nullable=False)
    airconditioning = db.Column(db.String(10), nullable=False)
    prefarea = db.Column(db.String(10), nullable=False)
    furnishingstatus = db.Column(db.String(20), nullable=False)
    
    # Prediction result
    predicted_price = db.Column(db.Float, nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'area': self.area,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'stories': self.stories,
            'parking': self.parking,
            'mainroad': self.mainroad,
            'guestroom': self.guestroom,
            'basement': self.basement,
            'hotwaterheating': self.hotwaterheating,
            'airconditioning': self.airconditioning,
            'prefarea': self.prefarea,
            'furnishingstatus': self.furnishingstatus,
            'predicted_price': self.predicted_price,
            'prediction_date': self.prediction_date.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<Prediction {self.id}: ${self.predicted_price:,.2f}>'
