from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

@app.route('/')
def index():
    try:
        news_articles = News.query.filter_by(head_approved=True).order_by(News.date_published.desc()).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('index.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error querying database: {e}")
        return render_template('index.html', news_articles=[], ad=None)

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
        print(f"Rajya Shehar, Selected City: '{selected_city}', Available Cities in DB: {all_locations}")
        print(f"All Head-Approved News Articles: {len(all_news)}")
        for article in all_news:
            print(f" - ID: {article.id}, Title: {article.title}, Location: '{article.location}', Category: {article.category}, Head Approved: {article.head_approved}")
        print(f"Filtered News Articles Found: {len(news_articles)}")
        for article in news_articles:
            print(f" - ID: {article.id}, Title: {article.title}, Location: '{article.location}', Category: {article.category}, Head Approved: {article.head_approved}")
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('rajya-shehar.html', 
                              news_articles=news_articles, 
                              ad=ad, 
                              selected_category='rajya-shehar', 
                              cities=cities, 
                              selected_city=selected_city)
    except Exception as e:
        print(f"Error querying database for rajya-shehar: {e}")
        return render_template('rajya-shehar.html', 
                              news_articles=[], 
                              ad=None, 
                              selected_category='rajya-shehar', 
                              cities=cities, 
                              selected_city='')

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
        return render_template('index.html', 
                              news_articles=news_articles, 
                              ad=ad, 
                              selected_category=category, 
                              cities=cities, 
                              selected_city=selected_city)
    except Exception as e:
        print(f"Error querying database for category {category}: {e}")
        return render_template('index.html', 
                              news_articles=[], 
                              ad=None, 
                              selected_category=category, 
                              cities=cities, 
                              selected_city='')

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
            print(f"Search Query: '{query}', Found Articles: {len(news_articles)}")
            for article in news_articles:
                print(f" - ID: {article.id}, Title: {article.title}, Location Text: '{article.location_text}', Category: {article.category}")
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('search.html', news_articles=news_articles, ad=ad, query=query)
    except Exception as e:
        print(f"Error querying search: {e}")
        return render_template('search.html', news_articles=[], ad=None, query=query)

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
        if not news.head_approved:
            return "News article not found or not approved.", 404
        blocks = ContentBlock.query.filter_by(news_id=news.id).order_by(ContentBlock.order_index).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        return render_template('news_detail.html', news=news, blocks=blocks, ad=ad, selected_category=news.category)
    except Exception as e:
        print(f"Error querying news: {e}")
        return "Error loading news article.", 500