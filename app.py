from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
import os
import logging

from config import config
from models import db, User, Prediction
from forms import LoginForm, SignupForm, HousePredictionForm
from ml_model import predictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    # Use environment variable or default to production
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    
    logger.info(f"Starting app with config: {config_name}")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    # Routes
    @app.route('/')
    def index():
        """Home page"""
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            
            if user and user.check_password(form.password.data):
                # Update last login
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                login_user(user, remember=True)
                flash(f'Welcome back, {user.get_full_name()}!', 'success')
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
        
        return render_template('login.html', form=form)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        """User registration"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = SignupForm()
        if form.validate_on_submit():
            # Check if user already exists
            existing_user = User.query.filter(
                (User.username == form.username.data) | 
                (User.email == form.email.data)
            ).first()
            
            if existing_user:
                flash('Username or email already exists.', 'danger')
                return render_template('signup.html', form=form)
            
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('signup.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        """User logout"""
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard with prediction history"""
        # Get user's recent predictions
        recent_predictions = Prediction.query.filter_by(user_id=current_user.id)\
                                           .order_by(Prediction.prediction_date.desc())\
                                           .limit(10).all()
        
        # Calculate some stats
        total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
        
        if recent_predictions:
            avg_price = sum(p.predicted_price for p in recent_predictions) / len(recent_predictions)
            max_price = max(p.predicted_price for p in recent_predictions)
            min_price = min(p.predicted_price for p in recent_predictions)
        else:
            avg_price = max_price = min_price = 0
        
        stats = {
            'total_predictions': total_predictions,
            'avg_price': avg_price,
            'max_price': max_price,
            'min_price': min_price
        }
        
        return render_template('dashboard.html', 
                             predictions=recent_predictions, 
                             stats=stats)

    @app.route('/predict', methods=['GET', 'POST'])
    @login_required
    def predict():
        """House price prediction"""
        form = HousePredictionForm()
        
        if form.validate_on_submit():
            # Prepare house features for prediction
            house_features = {
                'area': form.area.data,
                'bedrooms': form.bedrooms.data,
                'bathrooms': form.bathrooms.data,
                'stories': form.stories.data,
                'parking': form.parking.data,
                'mainroad': form.mainroad.data,
                'guestroom': form.guestroom.data,
                'basement': form.basement.data,
                'hotwaterheating': form.hotwaterheating.data,
                'airconditioning': form.airconditioning.data,
                'prefarea': form.prefarea.data,
                'furnishingstatus': form.furnishingstatus.data
            }
            
            # Make prediction
            predicted_price, error = predictor.predict_price(house_features)
            
            if predicted_price is not None:
                # Convert to Python float if it's numpy type (avoid PostgreSQL error)
                predicted_price = float(predicted_price)
                
                # Save prediction to database
                prediction = Prediction(
                    user_id=current_user.id,
                    **house_features,
                    predicted_price=predicted_price
                )
                
                db.session.add(prediction)
                db.session.commit()
                
                flash(f'Prediction successful! Estimated price: ${predicted_price:,.2f}', 'success')
                return render_template(
                    'predict_result.html',
                    prediction=prediction,
                    house_features=house_features
                )
            else:
                flash(f'Prediction failed: {error}', 'danger')
        
        return render_template('predict.html', form=form)

    @app.route('/history')
    @login_required
    def history():
        """Full prediction history"""
        page = request.args.get('page', 1, type=int)
        predictions = Prediction.query.filter_by(user_id=current_user.id)\
                                    .order_by(Prediction.prediction_date.desc())\
                                    .paginate(page=page, per_page=20, error_out=False)
        
        return render_template('history.html', predictions=predictions)

    @app.route('/delete_prediction/<int:prediction_id>')
    @login_required
    def delete_prediction(prediction_id):
        """Delete a prediction"""
        prediction = Prediction.query.get_or_404(prediction_id)
        
        # Check if user owns this prediction
        if prediction.user_id != current_user.id:
            flash('You can only delete your own predictions.', 'danger')
            return redirect(url_for('history'))
        
        db.session.delete(prediction)
        db.session.commit()
        flash('Prediction deleted successfully.', 'success')
        
        return redirect(url_for('history'))

    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=False)
