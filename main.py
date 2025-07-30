from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from unidecode import unidecode
import re
import json
from pywebpush import webpush, WebPushException

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///news_app.db')
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

class Epapers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    head_approved = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.relationship('Admin', backref='epapers')

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.Text, nullable=False, unique=True)
    p256dh_key = db.Column(db.Text, nullable=False)
    auth_key = db.Column(db.Text, nullable=False)
    subscribed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

def slugify(value):
    value = str(value)
    value = unidecode(value)  # Transliterate to Latin
    value = re.sub(r'[^\w\s-]', '', value)  # Remove non-word characters
    value = re.sub(r'[-\s]+', '-', value)   # Replace spaces/hyphens with single hyphen
    return value.strip('-').lower()

app.jinja_env.filters['slugify'] = slugify

# VAPID Configuration (You should generate your own keys)
# Generate keys using: webpush.generate_vapid_keys()
VAPID_PRIVATE_KEY = "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgx9xZSXWNGuNigzbBaAVP+Lqtmk87p3GjtfySp+vgCcqhRANCAAR58UIahF3XcbOabVXx/P97iKVgWb1BblvV6f0DKXlG8643DByhu98AXzUL/6KJQ7ReDNxR0oFrIPIujf9GC6IU"
VAPID_PUBLIC_KEY = "BHnxQhqEXddxs5ptVfH8_3uIpWBZvUFuW9Xp_QMpeUbzrjcMHKG73wBfNQv_oolDtF4M3FHSgWsg8i6N_0YLohQ"
VAPID_CLAIMS = {
    "sub": "mailto:admin@theinknews.com"
}

def send_notification_to_subscribers(title, body, url, image=None):
    """Send push notification to all active subscribers"""
    try:
        subscribers = Subscriber.query.filter_by(is_active=True).all()
        print(f"Found {len(subscribers)} active subscribers")
        
        # Enhanced notification data with more fields for better mobile support
        notification_data = {
            "title": title,
            "body": body,
            "url": url,
            "image": image,
            "timestamp": datetime.utcnow().isoformat(),
            "requireInteraction": True,
            "silent": False
        }
        
        success_count = 0
        failure_count = 0
        
        for subscriber in subscribers:
            try:
                subscription_info = {
                    "endpoint": subscriber.endpoint,
                    "keys": {
                        "p256dh": subscriber.p256dh_key,
                        "auth": subscriber.auth_key
                    }
                }
                
                print(f"Sending notification to subscriber {subscriber.id} at endpoint: {subscriber.endpoint[:30]}...")
                
                # Add TTL for better mobile delivery
                webpush(
                    subscription_info=subscription_info,
                    data=json.dumps(notification_data),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims=VAPID_CLAIMS,
                    ttl=86400  # 24 hours
                )
                print(f"✅ Notification successfully sent to subscriber {subscriber.id}")
                success_count += 1
                
            except WebPushException as ex:
                failure_count += 1
                print(f"❌ Failed to send notification to subscriber {subscriber.id}: {ex}")
                print(f"Subscription details: {subscription_info}")
                
                # If the subscription is invalid, deactivate it
                if ex.response and ex.response.status_code in [400, 404, 410]:
                    print(f"Deactivating invalid subscription for subscriber {subscriber.id}")
                    subscriber.is_active = False
                    db.session.commit()
                
                # Print full exception details for debugging
                import traceback
                traceback.print_exc()
                    
        print(f"Notification sending complete: {success_count} successful, {failure_count} failed")
        return success_count, failure_count
                    
    except Exception as e:
        print(f"Error sending notifications: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

def auto_notify_new_news(news_id):
    """Automatically send notification when news is approved"""
    try:
        news = News.query.get(news_id)
        if news and news.head_approved:
            # Get the first image from content blocks
            first_image = None
            content_blocks = ContentBlock.query.filter_by(news_id=news_id).order_by(ContentBlock.order_index).all()
            for block in content_blocks:
                if block.block_type == 'image' and block.content:
                    first_image = block.content
                    break
            
            # Create notification title and body
            title = "🔥 नई खबर - The Ink News"
            body = f"{news.title[:100]}{'...' if len(news.title) > 100 else ''}"
            url = f"/article/{news.id}-{slugify(news.title)}"
            
            # Send notification to all subscribers with image
            send_notification_to_subscribers(title, body, url, first_image)
            print(f"Auto notification sent for news ID: {news_id}")
    except Exception as e:
        print(f"Error in auto notification for news {news_id}: {e}")

@app.route('/')
def index():
    try:
        news_articles = News.query.filter_by(head_approved=True).order_by(News.date_published.desc()).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        print(f"Index Route - Articles Fetched: {len(news_articles)}")
        for article in news_articles:
            print(f" - ID: {article.id}, Title: {article.title}, Location: '{article.location}', Category: {article.category}")
        return render_template('index.html', news_articles=news_articles, ad=ad)
    except Exception as e:
        print(f"Error querying database in index: {e}")
        return render_template('index.html', news_articles=[], ad=None)

@app.route('/article/<int:id>-<slug>')
def article(id, slug):
    try:
        news = News.query.get_or_404(id)
        if not news.head_approved:
            return "News article not found or not approved.", 404
        blocks = ContentBlock.query.filter_by(news_id=news.id).order_by(ContentBlock.order_index).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        print(f"Article Route - ID: {id}, Title: {news.title}, Blocks: {len(blocks)}")
        return render_template('article.html', news=news, blocks=blocks, ad=ad)
    except Exception as e:
        print(f"Error querying article {id}: {e}")
        return "Error loading article.", 500

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
        print(f"Category Route - Category: {category}, Articles Fetched: {len(news_articles)}")
        for article in news_articles:
            print(f" - ID: {article.id}, Title: {article.title}, Location: '{article.location}', Category: {article.category}")
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
        print(f"Video Route - Articles Fetched: {len(news_articles)}")
        for article in news_articles:
            print(f" - ID: {article.id}, Title: {article.title}, Location: '{article.location}', Category: {article.category}")
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
        epapers = Epapers.query.filter_by(head_approved=True).order_by(Epapers.uploaded_at.desc()).all()
        ad = Advertisement.query.order_by(Advertisement.updated_at.desc()).first()
        print(f"Epaper Route - Epapers Fetched: {len(epapers)}")
        for epaper in epapers:
            print(f" - ID: {epaper.id}, Image URL: {epaper.image_url}, Uploaded At: {epaper.uploaded_at}")
        return render_template('epaper.html', epapers=epapers, ad=ad)
    except Exception as e:
        print(f"Error querying epaper page: {e}")
        return render_template('epaper.html', epapers=[], ad=None)

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
        print(f"News Detail Route - ID: {id}, Title: {news.title}, Blocks: {len(blocks)}")
        return render_template('news_detail.html', news=news, blocks=blocks, ad=ad, selected_category=news.category)
    except Exception as e:
        print(f"Error querying news: {e}")
        return "Error loading news article.", 500

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        print(f"Subscription request received: {data}")
        
        endpoint = data.get('endpoint')
        keys = data.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')
        
        print(f"Endpoint: {endpoint[:50]}..." if endpoint else "No endpoint")
        print(f"P256DH key: {p256dh[:20]}..." if p256dh else "No P256DH key")
        print(f"Auth key: {auth[:20]}..." if auth else "No Auth key")
        
        if not endpoint or not p256dh or not auth:
            print("Invalid subscription data - missing required fields")
            return jsonify({'success': False, 'message': 'Invalid subscription data'}), 400
        
        # Check if already subscribed
        existing = Subscriber.query.filter_by(endpoint=endpoint).first()
        if existing:
            print(f"Updating existing subscriber: {existing.id}")
            existing.is_active = True
            existing.p256dh_key = p256dh
            existing.auth_key = auth
        else:
            print("Creating new subscriber")
            subscriber = Subscriber(
                endpoint=endpoint,
                p256dh_key=p256dh,
                auth_key=auth
            )
            db.session.add(subscriber)
        
        db.session.commit()
        
        # Verify the subscription was saved
        total_subscribers = Subscriber.query.filter_by(is_active=True).count()
        print(f"Subscription successful! Total active subscribers: {total_subscribers}")
        
        return jsonify({'success': True, 'message': 'Successfully subscribed to notifications'})
    except Exception as e:
        print(f"Error subscribing user: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to subscribe'}), 500

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    try:
        data = request.get_json()
        endpoint = data.get('endpoint')
        
        if not endpoint:
            return jsonify({'success': False, 'message': 'Invalid endpoint'}), 400
        
        subscriber = Subscriber.query.filter_by(endpoint=endpoint).first()
        if subscriber:
            subscriber.is_active = False
            db.session.commit()
            return jsonify({'success': True, 'message': 'Successfully unsubscribed'})
        else:
            return jsonify({'success': False, 'message': 'Subscription not found'}), 404
    except Exception as e:
        print(f"Error unsubscribing user: {e}")
        return jsonify({'success': False, 'message': 'Failed to unsubscribe'}), 500

@app.route('/check-subscription', methods=['POST'])
def check_subscription():
    """Check if a subscription endpoint is active"""
    try:
        data = request.get_json()
        endpoint = data.get('endpoint')
        
        if not endpoint:
            return jsonify({'success': False, 'message': 'Invalid endpoint'}), 400
        
        subscriber = Subscriber.query.filter_by(endpoint=endpoint, is_active=True).first()
        if subscriber:
            return jsonify({'success': True, 'subscribed': True, 'message': 'Subscription is active'})
        else:
            return jsonify({'success': True, 'subscribed': False, 'message': 'No active subscription found'})
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return jsonify({'success': False, 'message': 'Failed to check subscription'}), 500

@app.route('/send-test-notification')
def send_test_notification():
    """Send a test notification to all subscribers"""
    try:
        print("Sending test notification to all active subscribers")
        
        # Test with a sample image
        test_image = "https://res.cloudinary.com/dmvfrdzrl/image/upload/v1752772701/SharedUploads/ink-news-logo.png?f_auto,q_auto"
        
        # Send a simple test notification
        result = send_notification_to_subscribers(
            title="🔔 Test Notification - The Ink News",
            body="यह एक टेस्ट नोटिफिकेशन है। अगर आपको यह दिख रहा है तो नोटिफिकेशन सिस्टम काम कर रहा है!",
            url="/",
            image=test_image
        )
        
        return jsonify({
            'success': True, 
            'message': 'Test notification sent successfully',
            'result': result
        })
    except Exception as e:
        print(f"Error sending test notification: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to send test notification'}), 500

@app.route('/add-test-subscriber')
def add_test_subscriber():
    """Add a test subscriber for debugging"""
    try:
        # Create a dummy subscriber for testing
        test_subscriber = Subscriber(
            endpoint="https://fcm.googleapis.com/fcm/send/test-endpoint-123",
            p256dh_key="test-p256dh-key",
            auth_key="test-auth-key"
        )
        
        # Check if test subscriber already exists
        existing = Subscriber.query.filter_by(endpoint=test_subscriber.endpoint).first()
        if not existing:
            db.session.add(test_subscriber)
            db.session.commit()
            message = "Test subscriber added successfully"
        else:
            existing.is_active = True
            db.session.commit()
            message = "Test subscriber already exists and activated"
        
        total_subscribers = Subscriber.query.filter_by(is_active=True).count()
        print(f"Test subscriber operation complete. Total active subscribers: {total_subscribers}")
        
        return jsonify({
            'success': True, 
            'message': message,
            'total_subscribers': total_subscribers
        })
    except Exception as e:
        print(f"Error adding test subscriber: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to add test subscriber'}), 500

@app.route('/notify-new-news', methods=['POST'])
def notify_new_news():
    """Endpoint for admin to trigger notification for specific news"""
    try:
        data = request.get_json()
        news_id = data.get('news_id')
        
        if not news_id:
            return jsonify({'success': False, 'message': 'News ID is required'}), 400
        
        news = News.query.get(news_id)
        if not news:
            return jsonify({'success': False, 'message': 'News not found'}), 404
        
        if not news.head_approved:
            return jsonify({'success': False, 'message': 'News is not approved'}), 400
        
        # Use the auto notification function
        auto_notify_new_news(news_id)
        
        return jsonify({'success': True, 'message': 'Notification sent successfully'})
        
    except Exception as e:
        print(f"Error in notify_new_news: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/auto-notify/<int:news_id>', methods=['POST'])
def auto_notify_endpoint(news_id):
    """Endpoint that can be called automatically when news is approved"""
    try:
        auto_notify_new_news(news_id)
        return jsonify({'success': True, 'message': f'Auto notification triggered for news {news_id}'})
    except Exception as e:
        print(f"Error in auto_notify_endpoint: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
    app.run(debug=True)
else:
    # For production deployment, ensure tables are created
    with app.app_context():
        db.create_all()