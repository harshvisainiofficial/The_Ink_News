from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'application_name': 'the_ink_news'},
    'pool_pre_ping': True
}

try:
    db = SQLAlchemy(app)
    logger.info("SQLAlchemy initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize SQLAlchemy: {e}")
    raise

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

# Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    about = db.Column(db.Text, nullable=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='General')
    head_approved = db.Column(db.Boolean, nullable=False, default=False)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    location_text = db.Column(db.String(200), nullable=True)
    date_published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    head_approved = db.Column(db.Boolean, nullable=False, default=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    admin = db.relationship('Admin', backref='news')

class ContentBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    block_type = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, nullable=False)
    news = db.relationship('News', backref='content_blocks')

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    top_banner = db.Column(db.String(200), nullable=True)
    right_sidebar = db.Column(db.String(200), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=True)
    news = db.relationship('News', backref='advertisements')

class Epapers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    head_approved = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.relationship('Admin', backref='epapers')

# PushEngage Configuration
PUSHENGAGE_API_KEY = os.environ.get('PUSHENGAGE_API_KEY', 'YOUR_PUSHENGAGE_API_KEY')
PUSHENGAGE_API_URL = 'https://api.pushengage.com/v4.0/notifications'

def send_push_notification(title, body, url):
    headers = {
        'Authorization': f'Bearer {PUSHENGAGE_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'title': title,
        'message': body,
        'url': url,
        'icon': 'https://res.cloudinary.com/dmvfrdzrl/image/upload/v1752772701/SharedUploads/ink-news-logo.png?f_auto,q_auto'
    }
    try:
        response = requests.post(PUSHENGAGE_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"Push notification sent: {title}")
    except requests.RequestException as e:
        logger.error(f"Error sending push notification: {e}")

# Routes
@app.route('/')
def index():
    try:
        news_articles = News.query.filter_by(head_approved=True).order_by(News.date_published.desc()).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        logger.info(f"Index Route - Articles Fetched: {len(news_articles)}")
        for article in news_articles:
            logger.debug(f" - ID: {article.id}, Title: {article.title}, Location: '{article.location}', Category: {article.category}")
        return render_template('index.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        logger.error(f"Error in index route: {e}", exc_info=True)
        return "Internal Server Error", 500

@app.route('/article/<int:id>')
def article(id):
    try:
        news = News.query.get_or_404(id)
        if not news.head_approved:
            logger.warning(f"Article {id} not approved")
            return "News article not found or not approved.", 404
        blocks = ContentBlock.query.filter_by(news_id=news.id).order_by(ContentBlock.order_index).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        logger.info(f"Article Route - ID: {id}, Title: {news.title}, Blocks: {len(blocks)}")
        return render_template('article.html', news=news, blocks=blocks, ad=ad)
    except Exception as e:
        logger.error(f"Error in article route {id}: {e}", exc_info=True)
        return "Internal Server Error", 500

@app.route('/rajya-shehar')
def rajya_shehar():
    try:
        selected_city = request.args.get('city', '').strip()
        query = News.query.filter_by(head_approved=True)
        if selected_city:
            query = query.filter(db.func.lower(db.func.trim(News.location)) == db.func.lower(selected_city))
        news_articles = query.order_by(News.date_published.desc()).all()
        cities = ['Bagar', 'Khetri', 'Bissau', 'Buhana', 'Chirawa', 'Gudhagorji', 'Jhunjhunu', 'Mandawa', 'Mukandgarh', 'Nawalgarh', 'Pilani', 'Surajgarh', 'Udaipurwati']
        all_news = News.query.filter_by(head_approved=True).all()
        all_locations = db.session.query(News.location).filter(
            News.head_approved == True,
            News.location != ''
        ).distinct().all()
        all_locations = [loc[0] for loc in all_locations if loc[0]]
        logger.info(f"Rajya Shehar, Selected City: '{selected_city}', Available Cities in DB: {all_locations}")
        logger.debug(f"All Head-Approved News Articles: {len(all_news)}")
        for article in all_news:
            logger.debug(f" - ID: {article.id}, Title: {article.title}, Location: '{article.location}', Category: {article.category}, Head Approved: {article.head_approved}")
        logger.info(f"Filtered News Articles Found: {len(news_articles)}")
        for article in news_articles:
            logger.debug(f" - ID: {article.id}, Title: {article.title}, Location: '{article.location}', Category: {article.category}, Head Approved: {article.head_approved}")
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('rajya-shehar.html', 
                              news_articles=news_articles, 
                              ad=ad, 
                              selected_category='rajya-shehar', 
                              cities=cities, 
                              selected_city=selected_city)
    except Exception as e:
        logger.error(f"Error in rajya-shehar route: {e}", exc_info=True)
        return "Internal Server Error", 500

@app.route('/category/<category>')
def category(category):
    try:
        if category == 'rajya-shehar':
            return rajya_shehar()
        selected_city = request.args.get('city', '').strip()
        query = News.query.filter_by(category=category, head_approved=True)
        if selected_city:
            query = query.filter(db.func.lower(db.func.trim(News.location)) == db.func.lower(selected_city))
        news_articles = query.order_by(News.date_published.desc()).all()
        cities = ['Bagar', 'Khetri', 'Bissau', 'Buhana', 'Chirawa', 'Gudhagorji', 'Jhunjhunu', 'Mandawa', 'Mukandgarh', 'Nawalgarh', 'Pilani', 'Surajgarh', 'Udaipurwati']
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        logger.info(f"Category Route - Category: {category}, Articles Fetched: {len(news_articles)}")
        for article in news_articles:
            logger.debug(f" - ID: {article.id}, Title: {article.title}, Location: '{article.location}', Category: {article.category}")
        return render_template('index.html', 
                              news_articles=news_articles, 
                              ad=ad, 
                              selected_category=category, 
                              cities=cities, 
                              selected_city=selected_city)
    except Exception as e:
        logger.error(f"Error in category route {category}: {e}", exc_info=True)
        return "Internal Server Error", 500

@app.route('/video')
def video():
    try:
        news_articles = News.query.filter(
            News.head_approved == True,
            News.id.in_(db.session.query(ContentBlock.news_id).filter(ContentBlock.block_type == 'video'))
        ).order_by(News.date_published.desc()).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        logger.info(f"Video Route - Articles Fetched: {len(news_articles)}")
        for article in news_articles:
            logger.debug(f" - ID: {article.id}, Title: {article.title}, Location: '{article.location}', Category: {article.category}")
        return render_template('video.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        logger.error(f"Error in video route: {e}", exc_info=True)
        return "Internal Server Error", 500

@app.route('/search')
def search():
    try:
        query = request.args.get('q', '').strip()
        news_articles = []
        if query:
            news_articles = News.query.filter(
                News.head_approved == True,
                db.or_(
                    News.title.ilike(f'%{query}%'),
                    News.id.in_(
                        db.session.query(ContentBlock.news_id).filter(
                            ContentBlock.block_type.in_(['text', 'subheading']),
                            ContentBlock.content.ilike(f'%{query}%')
                        )
                    )
                )
            ).order_by(News.date_published.desc()).all()
            logger.info(f"Search Query: '{query}', Found Articles: {len(news_articles)}")
            for article in news_articles:
                logger.debug(f" - ID: {article.id}, Title: {article.title}, Location Text: '{article.location_text}', Category: {article.category}")
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('search.html', news_articles=news_articles, ad=ad, query=query)
    except Exception as e:
        logger.error(f"Error in search route: {e}", exc_info=True)
        return "Internal Server Error", 500

@app.route('/webstory')
def webstory():
    try:
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        logger.info("Webstory Route - Accessed")
        return render_template('webstory.html', ad=ad)
    except Exception as e:
        logger.error(f"Error in webstory route: {e}", exc_info=True)
        return "Internal Server Error", 500

@app.route('/epaper')
def epaper():
    try:
        epapers = Epapers.query.filter_by(head_approved=True).order_by(Epapers.uploaded_at.desc()).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        logger.info(f"Epaper Route - Epapers Fetched: {len(epapers)}")
        for epaper in epapers:
            logger.debug(f" - ID: {epaper.id}, Image URL: {epaper.image_url}, Uploaded At: {epaper.uploaded_at}")
        return render_template('epaper.html', epapers=epapers, ad=ad)
    except Exception as e:
        logger.error(f"Error in epaper route: {e}", exc_info=True)
        return "Internal Server Error", 500

@app.route('/live-news')
def live_news():
    try:
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        logger.info("Live News Route - Accessed")
        return render_template('live-news.html', ad=ad)
    except Exception as e:
        logger.error(f"Error in live-news route: {e}", exc_info=True)
        return "Internal Server Error", 500

@app.route('/news/<int:id>')
def news_detail(id):
    try:
        news = News.query.get_or_404(id)
        if not news.head_approved:
            logger.warning(f"News {id} not approved")
            return "News article not found or not approved.", 404
        blocks = ContentBlock.query.filter_by(news_id=news.id).order_by(ContentBlock.order_index).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        logger.info(f"News Detail Route - ID: {id}, Title: {news.title}, Blocks: {len(blocks)}")
        return render_template('news_detail.html', news=news, blocks=blocks, ad=ad, selected_category=news.category)
    except Exception as e:
        logger.error(f"Error in news detail route {id}: {e}", exc_info=True)
        return "Internal Server Error", 500

@app.route('/add_news', methods=['POST'])
def add_news():
    try:
        data = request.get_json() or request.form
        title = data.get('title')
        category = data.get('category')
        location = data.get('location', '')
        location_text = data.get('location_text', '')
        blocks = data.get('content_blocks', [])
        head_approved = data.get('head_approved', False)
        admin_id = data.get('admin_id')  # Assume admin is authenticated

        if not title or not category:
            logger.warning("Missing title or category in add_news")
            return jsonify({'status': 'error', 'message': 'Title and category are required'}), 400

        # Create News article
        news = News(
            title=title,
            category=category,
            location=location,
            location_text=location_text,
            head_approved=bool(head_approved),
            admin_id=admin_id,
            date_published=datetime.utcnow()
        )
        db.session.add(news)
        db.session.flush()  # Get news.id before commit

        # Add Content Blocks
        for index, block in enumerate(blocks):
            content_block = ContentBlock(
                news_id=news.id,
                block_type=block.get('block_type', 'text'),
                content=block.get('content'),
                order_index=index
            )
            db.session.add(content_block)

        db.session.commit()
        logger.info(f"News article added: ID {news.id}, Title: {news.title}")

        # Send push notification if head_approved
        if news.head_approved:
            article_url = f"{request.url_root}news/{news.id}"
            body = next((block.content for block in blocks if block.get('block_type') == 'text'), title)[:100] + "..."
            send_push_notification(title, body, article_url)

        return jsonify({'status': 'success', 'news_id': news.id})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in add_news route: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500