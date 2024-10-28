document.addEventListener('DOMContentLoaded', function() {
    const restaurantData = document.getElementById('restaurant-data');
    const restaurantId = restaurantData.getAttribute('data-restaurant-id');
    const socket = new WebSocket((window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws/restaurant/' + restaurantId + '/');
    
    socket.onopen = function() {
        console.log('WebSocket connection opened.');
    };

    socket.onmessage = function(event) {
        console.log('WebSocket message received:', event.data); // Log the raw data
        const data = JSON.parse(event.data);
        console.log('Parsed WebSocket message:', data); // Log the parsed data
        
        if (data.message) {
            showNotification(data.message);
        }
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
        showErrorNotification('WebSocket error occurred. Please try again later.');
    };

    socket.onclose = function(e) {
        console.log('WebSocket connection closed.');
        showErrorNotification('WebSocket connection closed. Please refresh the page.');
    };

    function showNotification(message) {
        const notificationsDiv = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = 'alert alert-info';
        notification.innerText = message;
        notificationsDiv.appendChild(notification);

        // Set timeout for the notification to disappear after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    function showErrorNotification(message) {
        const notificationBox = document.getElementById('notification-box');
        const notificationHTML = `
            <div class="notification alert alert-danger">
                <p>${message}</p>
            </div>
        `;
        notificationBox.insertAdjacentHTML('beforeend', notificationHTML);

        // Remove the notification after a few seconds
        setTimeout(() => {
            const notification = notificationBox.querySelector('.notification');
            if (notification) {
                notification.remove();                                                                                             
            }
        }, 5000); // Adjust the timeout duration as needed
    }
});