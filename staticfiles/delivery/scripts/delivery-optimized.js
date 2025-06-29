// Delivery WebSocket - Production Optimized
document.addEventListener('DOMContentLoaded', function() {
    // WebSocket connection management
    let socket = null;
    let reconnectAttempts = 0;
    let reconnectTimeout = null;
    let isReconnecting = false;
    const maxReconnectAttempts = 3;
    const baseReconnectDelay = 3000;
    
    // Set up WebSocket connection
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const host = window.location.hostname || '127.0.0.1';
    
    let wsUrl;
    if (window.location.hostname === 'tengo.thisisemmanuel.pro') {
        wsUrl = `${protocol}${host}/ws/delivery/`;
    } else {
        const port = '8060';
        wsUrl = `${protocol}${host}:${port}/ws/delivery/`;
    }
    
    const pendingDeliveriesTableBody = document.querySelector('#pending-deliveries-table tbody');
    const acceptedDeliveriesTableBody = document.querySelector('table:not(#pending-deliveries-table) tbody');
    
    // Keep track of processed orders to avoid duplicate notifications
    const processedOrders = new Set();

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Update connection status display
    function updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.innerHTML = connected 
                ? `<span class="badge bg-success">Connected</span>`
                : `<span class="badge bg-danger">Disconnected</span>`;
        }
    }

    function showNotification(message, type = 'info') {
        const notificationsDiv = document.getElementById('notifications');
        if (!notificationsDiv) return;
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        notificationsDiv.appendChild(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    function updatePendingDeliveriesTable(order) {
        let existingRow = document.querySelector(`#pending-deliveries-table tbody tr#order-${order.id}`);
        
        if (existingRow) {
            // Update existing row
            existingRow.querySelector('td:nth-child(2)').innerText = order.restaurant_name;
            existingRow.querySelector('td:nth-child(3)').innerText = order.customer_name || 'Customer';
            existingRow.querySelector('td:nth-child(4)').innerText = order.customer_address || order.delivery_address || 'Address pending';
        } else {
            // Create new row
            const newRow = document.createElement('tr');
            newRow.setAttribute('id', `order-${order.id}`);
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            
            newRow.innerHTML = `
                <td>${order.id}</td>
                <td>${order.restaurant_name}</td>
                <td>${order.customer_name || 'Customer'}</td>
                <td>${order.customer_address || order.delivery_address || 'Address pending'}</td>
                <td>
                    <form method="POST" action="/delivery/accept/${order.id}/">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                        <button type="submit" class="btn btn-success">Accept</button>
                    </form>
                </td>
            `;
            
            pendingDeliveriesTableBody.appendChild(newRow);
            
            // Update pending count and hide "no orders" message
            updatePendingCount();
            hideNoOrdersMessage();
        }
    }

    function updateAcceptedDeliveriesTable(order) {
        let existingRow = document.querySelector(`#accepted-deliveries-table tbody tr#order-${order.id}`);
        
        if (existingRow) {
            // Update status
            const statusCell = existingRow.querySelector('.order-status');
            if (statusCell) {
                statusCell.textContent = order.status;
                statusCell.className = `badge order-status ${getStatusClass(order.status)}`;
            }
        } else {
            // Create new row in accepted deliveries
            const newRow = document.createElement('tr');
            newRow.setAttribute('id', `order-${order.id}`);
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            
            newRow.innerHTML = `
                <td>${order.id}</td>
                <td>${order.restaurant_name}</td>
                <td>${order.customer_name || 'Customer'}</td>
                <td>${order.customer_address || order.delivery_address || 'Address pending'}</td>
                <td><span class="badge order-status ${getStatusClass(order.status)}">${order.status}</span></td>
                <td>
                    ${order.status === 'Accepted' ? `
                        <form method="POST" action="/delivery/mark-out-for-delivery/${order.id}/" style="display: inline;">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                            <button type="submit" class="btn btn-primary btn-sm">Mark Out for Delivery</button>
                        </form>
                    ` : ''}
                    ${order.status === 'Out for delivery' ? `
                        <form method="POST" action="/delivery/mark-delivered/${order.id}/" style="display: inline;">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                            <button type="submit" class="btn btn-success btn-sm">Mark Delivered</button>
                        </form>
                    ` : ''}
                </td>
            `;
            
            if (acceptedDeliveriesTableBody) {
                acceptedDeliveriesTableBody.appendChild(newRow);
            }
        }
    }

    function getStatusClass(status) {
        const statusClasses = {
            'Accepted': 'bg-info',
            'Out for delivery': 'bg-primary',
            'Delivered': 'bg-success'
        };
        return statusClasses[status] || 'bg-secondary';
    }

    function updatePendingCount() {
        const pendingRows = document.querySelectorAll('#pending-deliveries-table tbody tr');
        const countElement = document.getElementById('pending-count');
        if (countElement) {
            countElement.textContent = pendingRows.length;
        }
    }

    function hideNoOrdersMessage() {
        const noOrdersMessage = document.querySelector('.no-orders-message');
        if (noOrdersMessage) {
            noOrdersMessage.style.display = 'none';
        }
    }

    function removePendingOrder(orderId) {
        const row = document.querySelector(`#pending-deliveries-table tbody tr#order-${orderId}`);
        if (row) {
            row.remove();
            updatePendingCount();
        }
    }

    function handleOrderUpdate(data) {
        const order = data.order;
        
        // Avoid duplicate processing
        const updateKey = `${order.id}-${order.status}-${Date.now()}`;
        if (processedOrders.has(updateKey)) {
            return;
        }
        processedOrders.add(updateKey);
        
        // Clean up old processed orders (keep only last 50)
        if (processedOrders.size > 50) {
            const ordersArray = Array.from(processedOrders);
            processedOrders.clear();
            ordersArray.slice(-25).forEach(key => processedOrders.add(key));
        }

        // Show notification for important updates
        const notificationType = data.notification_type || '';
        if (['new_order_available', 'order_cancelled', 'order_reassigned'].includes(notificationType)) {
            showNotification(data.message, 'info');
        }

        // Update appropriate table based on order status
        switch (order.status) {
            case 'Ready for Delivery':
                updatePendingDeliveriesTable(order);
                break;
            case 'Accepted':
            case 'Out for delivery':
            case 'Delivered':
                updateAcceptedDeliveriesTable(order);
                removePendingOrder(order.id);
                break;
            default:
                // Handle other statuses if needed
                break;
        }

        // Handle special cases
        if (order.no_longer_available) {
            removePendingOrder(order.id);
        }
    }

    // Optimized WebSocket connection function
    function connectWebSocket() {
        if (socket && (socket.readyState === WebSocket.CONNECTING || socket.readyState === WebSocket.OPEN)) {
            return; // Already connecting or connected
        }

        if (isReconnecting) {
            return; // Already attempting to reconnect
        }

        try {
            socket = new WebSocket(wsUrl);

            socket.onopen = function(event) {
                reconnectAttempts = 0;
                isReconnecting = false;
                if (reconnectTimeout) {
                    clearTimeout(reconnectTimeout);
                    reconnectTimeout = null;
                }
                updateConnectionStatus(true);
            };

            socket.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    
                    if (data.order) {
                        handleOrderUpdate(data);
                    } else if (data.message) {
                        showNotification(data.message, 'info');
                    }
                } catch (error) {
                    // Invalid JSON received, ignore
                }
            };

            socket.onclose = function(event) {
                updateConnectionStatus(false);

                if (!isReconnecting && reconnectAttempts < maxReconnectAttempts) {
                    isReconnecting = true;
                    reconnectAttempts++;
                    
                    const delay = baseReconnectDelay * Math.pow(2, reconnectAttempts - 1);
                    
                    reconnectTimeout = setTimeout(() => {
                        isReconnecting = false;
                        connectWebSocket();
                    }, delay);
                } else if (reconnectAttempts >= maxReconnectAttempts) {
                    showNotification('Unable to maintain connection. Please refresh the page.', 'warning');
                }
            };

            socket.onerror = function(error) {
                updateConnectionStatus(false);
            };

        } catch (error) {
            if (reconnectAttempts < maxReconnectAttempts) {
                setTimeout(() => connectWebSocket(), baseReconnectDelay);
            }
        }
    }

    // Initialize connection
    connectWebSocket();

    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        if (reconnectTimeout) {
            clearTimeout(reconnectTimeout);
        }
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close();
        }
    });

    // Handle page visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            if (!socket || socket.readyState === WebSocket.CLOSED) {
                connectWebSocket();
            }
        }
    });

    // Initial count update
    updatePendingCount();
});
