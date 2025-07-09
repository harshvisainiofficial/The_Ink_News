from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Harsh/Desktop/The Ink NEWS/The Ink NEWS/SharedDB/ink.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'C:/Users/Harsh/Desktop/The Ink NEWS/The Ink NEWS/SharedUploads'

db = SQLAlchemy(app)

# Custom Jinja2 filters
def isfile(path):
    if not path:
        return False
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(path))
    return os.path.isfile(full_path)

def basename(path):
    if not path:
        return ''
    return os.path.basename(path)

app.jinja_env.filters['isfile'] = isfile
app.jinja_env.filters['basename'] = basename

# Models
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)  # Represents City
    location_text = db.Column(db.String(200), nullable=True)  # Text-based Location
    date_published = db.Column(db.DateTime, nullable=False)
    head_approved = db.Column(db.Boolean, nullable=False, default=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)

class ContentBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    block_type = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, nullable=False)

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    top_banner = db.Column(db.String(200), nullable=True)
    right_sidebar = db.Column(db.String(200), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False)

@app.route('/')
def index():
    try:
        news_articles = News.query.filter_by(head_approved=True).order_by(News.date_published.desc()).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('index.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error querying database: {e}")
        return render_template('index.html', news_articles=[], ad=None)

@app.route('/category/<category>')
def category(category):
    try:
        news_articles = News.query.filter_by(category=category, head_approved=True).order_by(News.date_published.desc()).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('index.html', news_articles=news_articles, ad=ad, selected_category=category)
    except Exception as e:
        print(f"Error querying database: {e}")
        return render_template('index.html', news_articles=[], ad=None, selected_category=category)

@app.route('/video')
def video():
    try:
        news_articles = News.query.filter(
            News.head_approved == True,
            News.id.in_(db.session.query(ContentBlock.news_id).filter(ContentBlock.block_type == 'video'))
        ).order_by(News.date_published.desc()).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('video.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error querying video articles: {e}")
        return render_template('video.html', news_articles=[], ad=None)

@app.route('/search')
def search():
    try:
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('search.html', ad=ad)
    except Exception as e:
        print(f"Error querying search page: {e}")
        return render_template('search.html', ad=None)

@app.route('/webstory')
def webstory():
    try:
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('webstory.html', ad=ad)
    except Exception as e:
        print(f"Error querying webstory page: {e}")
        return render_template('webstory.html', ad=None)

@app.route('/epaper')
def epaper():
    try:
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('epaper.html', ad=ad)
    except Exception as e:
        print(f"Error querying epaper page: {e}")
        return render_template('epaper.html', ad=None)

@app.route('/live-news')
def live_news():
    try:
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('live-news.html', ad=ad)
    except Exception as e:
        print(f"Error querying live-news page: {e}")
        return render_template('live-news.html', ad=None)

@app.route('/news/<int:id>')
def news_detail(id):
    try:
        news = News.query.get_or_404(id)
        print(f"News ID {id}: title={news.title}, head_approved={news.head_approved}, location={news.location}, location_text={news.location_text}, date_published={news.date_published}")
        if not news.head_approved:
            print(f"News ID {id} not approved, returning 404")
            return "News article not found or not approved.", 404
        blocks = ContentBlock.query.filter_by(news_id=news.id).order_by(ContentBlock.order_index).all()
        print(f"News ID {id}: found {len(blocks)} content blocks")
        for block in blocks:
            print(f"Block ID {block.id}: type={block.block_type}, content={block.content}, order_index={block.order_index}")
        return render_template('news_detail.html', news=news, blocks=blocks)
    except Exception as e:
        print(f"Error querying news ID {id}: {e}")
        return "Error loading news article.", 500

@app.route('/Uploads/<path:filename>')
def serve_uploads(filename):
    try:
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Serving file: {full_path}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        return "File not found.", 404

if __name__ == '__main__':
    with app.app_context():
        try:
            # Update existing rashifal articles to top-news
            rashifal_news = News.query.filter_by(category='rashifal').all()
            for news in rashifal_news:
                news.category = 'top-news'
                print(f"Updated news ID {news.id} from rashifal to top-news")
            # Update existing Pilani and Chirawa locations to empty string
            city_news = News.query.filter(News.location.in_(['Pilani', 'Chirawa'])).all()
            for news in city_news:
                news.location = ''
                print(f"Updated news ID {news.id} location from {news.location} to empty")
            db.session.commit()
        except Exception as e:
            print(f"Error updating database: {e}")
            db.session.rollback()
    app.run(debug=True, port=5000)