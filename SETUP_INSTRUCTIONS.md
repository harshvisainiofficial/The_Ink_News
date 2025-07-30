# Push Notification Setup Instructions

## 1. Install Dependencies
Run the following command to install all required dependencies:
```bash
pip install -r requirements.txt
# If you encounter issues with VAPID key generation, also install:
pip install py-vapid cryptography
```

## 2. Generate VAPID Keys
Run the provided script to generate your VAPID keys:
```bash
python generate_vapid_keys.py
```

This will output something like:
```
VAPID Keys Generated:
Private Key: <your-private-key>
Public Key: <your-public-key>
```

## 3. Update Configuration

### Update main.py
Replace the placeholder in `main.py` line 83:
```python
VAPID_PRIVATE_KEY = "your-private-key-here"  # Replace with your actual private key
```

### Update base.html
Replace the public key in `base.html` around line 250:
```javascript
const applicationServerPublicKey = 'BEl62iUYgUivxIkv69yViEuiBIa40HdHSWgMfHXPJeuNiJ7Ek00jVNPSyeQX-QbVFPLwqyBFWAlVfY9OCLXiAiA';  // Replace with your actual public key
```

## 4. Database Setup
Make sure your database is properly configured and the tables are created. The app will automatically create tables when you run it.

## 5. Test the System

### Start the Application
```bash
python main.py
```

### Test Subscription
1. Open your website in a browser
2. Click the "🔔 सब्सक्राइब" button in the top navigation
3. Allow notifications when prompted
4. The button should change to "🔔 सब्सक्राइब्ड"

### Test Notifications
1. Visit `/send-test-notification` to send a test notification
2. Use the `/notify-new-news` endpoint with POST data: `{"news_id": <id>}`
3. Use the `/auto-notify/<news_id>` endpoint for automatic notifications

## 6. Integration with Admin Panel

To automatically send notifications when news is approved, make a POST request to:
```
/auto-notify/<news_id>
```

This endpoint will:
- Check if the news exists and is approved
- Send notifications to all active subscribers
- Handle any subscription errors automatically

## 7. Features Included

✅ **Subscribe Button**: Users can subscribe/unsubscribe to notifications
✅ **Service Worker**: Handles push notifications in the background
✅ **Database Model**: Stores subscriber information securely
✅ **Notification System**: Sends push notifications to all subscribers
✅ **Error Handling**: Automatically removes invalid subscriptions
✅ **Hindi Language Support**: All UI text is in Hindi
✅ **Responsive Design**: Works on mobile and desktop
✅ **Auto Notifications**: Can be triggered when news is approved

## 8. API Endpoints

- `POST /subscribe` - Subscribe to notifications
- `POST /unsubscribe` - Unsubscribe from notifications
- `GET /send-test-notification` - Send test notification
- `POST /notify-new-news` - Manual notification trigger
- `POST /auto-notify/<news_id>` - Automatic notification trigger

## 9. Security Notes

- Keep your VAPID private key secure and never commit it to version control
- The public key can be safely included in your frontend code
- Subscriber data is stored securely in the database
- Invalid subscriptions are automatically cleaned up

## 10. Troubleshooting

- If notifications don't work, check browser console for errors
- Ensure HTTPS is enabled in production (required for push notifications)
- Verify that the service worker is properly registered
- Check that VAPID keys are correctly configured