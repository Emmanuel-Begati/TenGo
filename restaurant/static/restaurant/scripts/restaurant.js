// WebSocket connection manager for restaurant dashboard
document.addEventListener('DOMContentLoaded', function() {
    // WebSocket connection variable
    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    
    // Function to safely get restaurant ID
    function getRestaurantId() {
        // Look for restaurant ID in multiple possible locations
        const sources = [
            document.getElementById('restaurant-data'),
            document.querySelector('[data-restaurant-id]'),
            document.querySelector('meta[name="restaurant-id"]')
        ];
        
        for (const source of sources) {
            if (source && source.getAttribute('data-restaurant-id')) {
                return source.getAttribute('data-restaurant-id');
            }
        }
        
        // Fallback: try to get from URL if in path format /restaurant/ID/
        const urlMatch = window.location.pathname.match(/\/restaurant\/(\d+)/);
        if (urlMatch && urlMatch[1]) {
            return urlMatch[1];
        }
        
        // Hard-coded fallback - replace with appropriate value if known
        console.warn("Could not find restaurant ID, using fallback value");
        return document.getElementById('restaurant-id')?.value || '3';
    }
    
    // Function to create WebSocket connection
    function connectWebSocket() {
        if (socket && socket.readyState !== WebSocket.CLOSED) {
            console.log('Closing existing WebSocket before creating new one');
            socket.close();
        }
        
        const restaurantId = getRestaurantId();
        console.log(`Connecting WebSocket for restaurant ID: ${restaurantId}`);
        
        // Determine correct protocol (ws or wss)
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const host = window.location.hostname || '127.0.0.1';
        const port = '8001'; // Daphne server port
        const wsUrl = `${protocol}${host}:${port}/ws/restaurant/${restaurantId}/`;
        
        try {
            console.log(`Attempting WebSocket connection to: ${wsUrl}`);
            socket = new WebSocket(wsUrl);
            
            socket.onopen = function(e) {
                console.log('WebSocket connection established');
                reconnectAttempts = 0;
                showNotification('Connected to order updates');
            };
            
            socket.onmessage = function(e) {
                const data = JSON.parse(e.data);
                console.log('WebSocket message received:', data);
                
                if (data.type === 'order_update' || data.type === 'new_order') {
                    updateOrderDisplay(data);
                    showNotification(`Order update: ${data.message}`);
                }
            };
            
            socket.onclose = function(e) {
                console.log('WebSocket connection closed', e);
                
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000); // Exponential backoff
                    console.log(`Reconnecting in ${timeout/1000}s (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
                    
                    setTimeout(function() {
                        connectWebSocket();
                    }, timeout);
                } else {
                    console.error('Maximum reconnection attempts reached');
                    showNotification('Connection lost. Please refresh the page.', 'error');
                }
            };
            
            socket.onerror = function(e) {
                console.error('WebSocket error:', e);
                // Error handling is done in onclose
            };
        } catch (error) {
            console.error('Error creating WebSocket:', error);
        }
    }
    
    // Function to update UI when orders change
    function updateOrderDisplay(data) {
        // Find the order in the DOM
        const orderId = data.order?.id;
        if (!orderId) return;
        
        const orderElement = document.querySelector(`[data-order-id="${orderId}"]`);
        if (orderElement) {
            // Update status if present
            const statusElement = orderElement.querySelector('.order-status');
            if (statusElement && data.order.status) {
                statusElement.textContent = data.order.status;
                
                // Update status classes
                statusElement.classList.remove('pending', 'preparing', 'delivered', 'cancelled');
                statusElement.classList.add(data.order.status.toLowerCase());
            }
            
            // Update payment status if present
            const paymentElement = orderElement.querySelector('.payment-status');
            if (paymentElement && data.order.payment_status !== undefined) {
                paymentElement.textContent = data.order.payment_status ? 'Paid' : 'Unpaid';
                paymentElement.classList.toggle('paid', data.order.payment_status);
                paymentElement.classList.toggle('unpaid', !data.order.payment_status);
            }
        } else {
            // If order not found in DOM, we might want to refresh the entire list
            console.log('Order element not found in DOM, consider refreshing the order list');
        }
    }
    
    // Function to show notifications
    function showNotification(message, type = 'info') {
        const notificationBox = document.getElementById('notification-box');
        if (!notificationBox) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `<p>${message}</p>`;
        
        notificationBox.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                notificationBox.removeChild(notification);
            }, 500);
        }, 5000);
    }
    
    // Make functions globally available
    window.websocketManager = {
        connect: connectWebSocket,
        getStatus: () => socket ? socket.readyState : 'Not initialized',
        showNotification: showNotification
    };
    
    // Connect WebSocket when the page loads
    setTimeout(connectWebSocket, 1000);
});