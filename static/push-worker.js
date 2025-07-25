self.addEventListener('push', function(event) {
    const data = event.data ? event.data.json() : {};
    const options = {
        body: data.body || 'New article available!',
        icon: '/static/images/logo.png',
        data: {
            url: data.url || window.location.origin
        }
    };
    event.waitUntil(
        self.registration.showNotification(data.title || 'The Ink News', options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});