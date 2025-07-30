// Service Worker for Push Notifications
self.addEventListener('push', function(event) {
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body,
            icon: 'https://res.cloudinary.com/dmvfrdzrl/image/upload/v1752772701/SharedUploads/ink-news-logo.png?f_auto,q_auto',
            badge: 'https://res.cloudinary.com/dmvfrdzrl/image/upload/v1752772701/SharedUploads/ink-news-logo.png?f_auto,q_auto',
            vibrate: [200, 100, 200],
            data: {
                url: data.url || '/'
            },
            actions: [
                {
                    action: 'open',
                    title: 'पढ़ें',
                    icon: '/static/images/read-icon.png'
                },
                {
                    action: 'close',
                    title: 'बंद करें',
                    icon: '/static/images/close-icon.png'
                }
            ]
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    if (event.action === 'open' || !event.action) {
        event.waitUntil(
            clients.openWindow(event.notification.data.url)
        );
    }
});

self.addEventListener('notificationclose', function(event) {
    console.log('Notification closed:', event.notification.tag);
});