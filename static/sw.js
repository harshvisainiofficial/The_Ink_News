// Service Worker for Push Notifications
self.addEventListener('push', function(event) {
    console.log('Push event received:', event);
    
    if (event.data) {
        try {
            const data = event.data.json();
            console.log('Push notification data:', data);
            
            const options = {
                body: data.body,
                icon: 'https://res.cloudinary.com/dmvfrdzrl/image/upload/v1752772701/SharedUploads/ink-news-logo.png?f_auto,q_auto',
                badge: 'https://res.cloudinary.com/dmvfrdzrl/image/upload/v1752772701/SharedUploads/ink-news-logo.png?f_auto,q_auto',
                image: data.image || null, // Article's first image
                vibrate: [200, 100, 200, 100, 200],
                requireInteraction: data.requireInteraction || true,
                silent: data.silent || false,
                timestamp: data.timestamp ? new Date(data.timestamp).getTime() : Date.now(),
                tag: 'ink-news-notification',
                renotify: true,
                data: {
                    url: data.url || '/'
                },
                actions: [
                    {
                        action: 'open',
                        title: 'पढ़ें'
                    },
                    {
                        action: 'close',
                        title: 'बंद करें'
                    }
                ]
            };
            
            console.log('Showing notification with options:', options);
            
            event.waitUntil(
                self.registration.showNotification(data.title, options)
                    .then(() => {
                        console.log('Notification shown successfully');
                    })
                    .catch(error => {
                        console.error('Error showing notification:', error);
                    })
            );
        } catch (error) {
            console.error('Error parsing push data:', error);
            
            // Fallback notification
            event.waitUntil(
                self.registration.showNotification('द इंक न्यूज़', {
                    body: 'नई खबर उपलब्ध है',
                    icon: 'https://res.cloudinary.com/dmvfrdzrl/image/upload/v1752772701/SharedUploads/ink-news-logo.png?f_auto,q_auto',
                    tag: 'ink-news-fallback'
                })
            );
        }
    } else {
        console.log('Push event received but no data');
        
        // Show a generic notification
        event.waitUntil(
            self.registration.showNotification('द इंक न्यूज़', {
                body: 'नई अपडेट उपलब्ध है',
                icon: 'https://res.cloudinary.com/dmvfrdzrl/image/upload/v1752772701/SharedUploads/ink-news-logo.png?f_auto,q_auto',
                tag: 'ink-news-generic'
            })
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