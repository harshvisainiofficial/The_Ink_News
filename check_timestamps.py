from main import *
import pytz
from datetime import datetime

with app.app_context():
    # Check all news articles
    all_news = News.query.all()
    print(f'Total news articles: {len(all_news)}')
    
    if all_news:
        for i, news in enumerate(all_news[:3]):  # Show first 3
            print(f'News {i+1}: {news.title[:50]}...')
            print(f'  Timestamp: {news.date_published}')
            print(f'  Timezone: {news.date_published.tzinfo}')
            print(f'  Formatted: {news.date_published.strftime("%Y-%m-%d %H:%M")}')
            print()
    else:
        print('No news found in database')
        # Let's create a test article to verify timezone
        print('Creating test article...')
        test_news = News(
            title='Test Article for Timezone',
            category='test',
            location='test',
            location_text='Test Location'
        )
        db.session.add(test_news)
        db.session.commit()
        print(f'Test article created with timestamp: {test_news.date_published}')
        print(f'Timezone: {test_news.date_published.tzinfo}')