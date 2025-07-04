from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import traceback

app = Flask(__name__)
# Use shared database and uploads folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Harsh/Desktop/The Ink NEWS/The Ink NEWS/SharedDB/ink.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'C:/Users/Harsh/Desktop/The Ink NEWS/The Ink NEWS/SharedUploads'

# Ensure SharedDB directory exists
shared_db_dir = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
if not os.path.exists(shared_db_dir):
    try:
        os.makedirs(shared_db_dir)
        print(f"Created directory: {shared_db_dir}")
    except Exception as e:
        print(f"Error creating directory {shared_db_dir}: {e}")

db = SQLAlchemy(app)

# Models
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    video = db.Column(db.String(200), nullable=True)
    date_published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    top_banner = db.Column(db.String(200), nullable=True)
    right_sidebar = db.Column(db.String(200), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Route to serve uploaded files
@app.route('/Uploads/<path:filename>')
def serve_uploaded_file(filename):
    try:
        # Remove 'admin/uploads/' prefix if present
        clean_filename = filename.replace('admin/uploads/', '')
        return send_from_directory(app.config['UPLOAD_FOLDER'], clean_filename)
    except Exception as e:
        print(f"Error serving file {filename}: {e}\n{traceback.format_exc()}")
        return "File not found.", 404

# Helper function to get the latest advertisement
def get_latest_ad():
    try:
        return Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
    except Exception as e:
        print(f"Error fetching advertisement: {e}\n{traceback.format_exc()}")
        return None

# Routes for each section
@app.route('/')
def index():
    try:
        news_articles = News.query.order_by(News.date_published.desc()).limit(10).all()
        ad = get_latest_ad()
        return render_template('index.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error in index route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading the homepage.", 500

@app.route('/top-news')
def top_news():
    try:
        news_articles = News.query.filter_by(category='top-news').order_by(News.date_published.desc()).all()
        ad = get_latest_ad()
        return render_template('top-news.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error in top news route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading top-news.", 500

@app.route('/rajya-shehar')
def rajya_shehar():
    try:
        news_articles = News.query.filter_by(category='rajya-shehar').order_by(News.date_published.desc()).all()
        ad = get_latest_ad()
        return render_template('rajya-shehar.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error in rajya-shehar route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading rajya shehar.", 500

@app.route('/the-ink-khas')
def the_ink_khas():
    try:
        news_articles = News.query.filter_by(category='the-ink-khas').order_by(News.date_published.desc()).all()
        ad = get_latest_ad()
        return render_template('the-ink-khas.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error in the-ink-khas route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading the ink khas.", 500

@app.route('/cricket')
def cricket():
    try:
        news_articles = News.query.filter_by(category='cricket').order_by(News.date_published.desc()).all()
        ad = get_latest_ad()
        return render_template('cricket.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error in cricket route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading cricket.", 500

@app.route('/sports')
def sports():
    try:
        news_articles = News.query.filter_by(category='sports').order_by(News.date_published.desc()).all()
        ad = get_latest_ad()
        return render_template('sports.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error in sports route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading sports.", 500

@app.route('/jiveen-mantra')
def jiveen_mantra():
    try:
        news_articles = News.query.filter_by(category='jiveen-mantra').order_by(News.date_published.desc()).all()
        ad = get_latest_ad()
        return render_template('jiveen-mantra.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error in jiveen-mantra route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading jiveen mantra.", 500

@app.route('/rashifal')
def rashifal():
    try:
        news_articles = News.query.filter_by(category='rashifal').order_by(News.date_published.desc()).all()
        ad = get_latest_ad()
        return render_template('rashifal.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error in rashifal route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading rashifal.", 500

@app.route('/business')
def business():
    try:
        news_articles = News.query.filter_by(category='business').order_by(News.date_published.desc()).all()
        ad = get_latest_ad()
        return render_template('business.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error in business route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading business.", 500

@app.route('/video')
def video():
    try:
        video_articles = News.query.filter(News.video != None).order_by(News.date_published.desc()).all()
        ad = get_latest_ad()
        return render_template('video.html', video_articles=video_articles, ad=ad)
    except Exception as e:
        print(f"Error in video route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading videos.", 500

@app.route('/live-news')
def live_news():
    try:
        ad = get_latest_ad()
        return render_template('live-news.html', ad=ad)
    except Exception as e:
        print(f"Error in live-news route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading live news.", 500

@app.route('/search')
def search():
    try:
        ad = get_latest_ad()
        return render_template('search.html', ad=ad)
    except Exception as e:
        print(f"Error in search route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading search.", 500

@app.route('/webstory')
def webstory():
    try:
        ad = get_latest_ad()
        return render_template('webstory.html', ad=ad)
    except Exception as e:
        print(f"Error in webstory route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading webstory.", 500

@app.route('/epaper')
def epaper():
    try:
        ad = get_latest_ad()
        return render_template('epaper.html', ad=ad)
    except Exception as e:
        print(f"Error in epaper route: {e}\n{traceback.format_exc()}")
        return "An error occurred while loading epaper.", 500

if __name__ == '__main__':
    with app.app_context():
        try:
            # Check if database file exists, create tables if necessary
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if not os.path.exists(db_path):
                print(f"Database file {db_path} not found, creating new database.")
                db.create_all()
                print("Database created successfully.")
            else:
                print(f"Database file {db_path} found.")
                db.create_all()  # Ensure tables are created
        except Exception as e:
            print(f"Error initializing database: {e}\n{traceback.format_exc()}")
            raise
        print("Database path:", app.config['SQLALCHEMY_DATABASE_URI'])
        print("Database file exists:", os.path.exists(db_path))
    app.run(debug=True, port=5000)