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
    const acceptedDeliveriesTableBody = document.querySelector('#accepted-deliveries-table tbody');
    
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
            
            // Update action buttons based on status
            const actionCell = existingRow.querySelector('td:last-child');
            if (actionCell) {
                updateActionButtons(actionCell, order);
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
                <td></td>
            `;
            
            if (acceptedDeliveriesTableBody) {
                acceptedDeliveriesTableBody.appendChild(newRow);
                // Update action buttons after adding the row
                const actionCell = newRow.querySelector('td:last-child');
                updateActionButtons(actionCell, order);
            }
        }
    }

    function updateActionButtons(actionCell, order) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        
        if (order.status === 'Accepted') {
            actionCell.innerHTML = `
                <form method="POST" class="status-form d-inline" data-order-id="${order.id}">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                    <select name="status" class="form-select form-select-sm">
                        <option value="" disabled selected>Update Status</option>
                        <option value="Out for delivery">Mark Out for Delivery</option>
                    </select>
                </form>
            `;
        } else if (order.status === 'Out for delivery') {
            actionCell.innerHTML = `
                <form method="POST" class="status-form d-inline" data-order-id="${order.id}">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                    <select name="status" class="form-select form-select-sm">
                        <option value="" disabled selected>Update Status</option>
                        <option value="Delivered">Mark as Delivered</option>
                    </select>
                </form>
            `;
        } else {
            actionCell.innerHTML = `<span class="text-muted">${order.status}</span>`;
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

    // Handle status form submissions for OTP popup
    document.addEventListener('change', function(e) {
        if (e.target.name === 'status' && e.target.value) {
            e.preventDefault(); // Prevent any default behavior
            
            const form = e.target.closest('form');
            const orderId = form.dataset.orderId;
            const status = e.target.value;
            
            console.log('Status change detected:', {orderId, status}); // Debug log
            
            // Reset the select to show "Update Status" option
            e.target.value = '';
            
            // Show OTP modal
            showOTPModal(orderId, status);
        }
    });

    // Prevent form submission for status forms
    document.addEventListener('submit', function(e) {
        if (e.target.classList.contains('status-form')) {
            e.preventDefault();
            console.log('Form submission prevented for status form');
        }
    });

    function showOTPModal(orderId, status) {
        console.log('showOTPModal called with:', {orderId, status}); // Debug log
        
        const modal = document.getElementById('myModal');
        const otpForm = document.getElementById('otpForm');
        const orderIdInput = document.getElementById('order_id');
        const statusInput = document.getElementById('status');
        const otpCodeInput = document.getElementById('otp_code');
        const messageContainer = document.getElementById('messageContainer');
        
        if (!modal) {
            console.error('Modal element not found');
            return;
        }
        
        if (!otpForm) {
            console.error('OTP form not found');
            return;
        }
        
        // Clear previous messages and OTP input
        if (messageContainer) {
            messageContainer.innerHTML = '';
        }
        if (otpCodeInput) {
            otpCodeInput.value = '';
        }
        
        // Set form data
        if (orderIdInput) {
            orderIdInput.value = orderId;
        }
        if (statusInput) {
            statusInput.value = status;
        }
        if (otpForm) {
            otpForm.action = `/delivery/update/${orderId}/`;
        }
        
        // Update modal title based on status
        const modalTitle = document.getElementById('exampleModalLabel');
        if (modalTitle) {
            if (status === 'Out for delivery') {
                modalTitle.textContent = 'Enter Restaurant OTP Code';
            } else if (status === 'Delivered') {
                modalTitle.textContent = 'Enter Customer OTP Code';
            }
        }
        
        console.log('About to show modal'); // Debug log
        
        // Show the modal
        try {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            console.log('Modal shown successfully'); // Debug log
        } catch (error) {
            console.error('Error showing modal:', error);
            // Fallback - try to show modal using jQuery if available
            if (typeof $ !== 'undefined') {
                console.log('Trying jQuery modal fallback');
                $(modal).modal('show');
            } else {
                // Last resort - direct style manipulation
                modal.style.display = 'block';
                modal.classList.add('show');
                document.body.classList.add('modal-open');
            }
        }
    }

    // Handle OTP form submission
    const otpForm = document.getElementById('otpForm');
    if (otpForm) {
        otpForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('OTP form submitted'); // Debug log
            
            const formData = new FormData(this);
            const orderId = formData.get('order_id');
            const status = formData.get('status');
            const otpCode = formData.get('otp_code');
            
            console.log('Form data:', {orderId, status, otpCode}); // Debug log
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Verifying...';
            submitBtn.disabled = true;
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log('Response received:', response); // Debug log
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data); // Debug log
                if (data.success) {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('myModal'));
                    if (modal) {
                        modal.hide();
                    }
                    
                    // Show success notification
                    showNotification(`Order #${orderId} status updated to: ${status}`, 'success');
                    
                    // Refresh the page to reflect changes
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    // Show error in modal
                    const messageContainer = document.getElementById('messageContainer');
                    if (messageContainer) {
                        messageContainer.innerHTML = `
                            <div class="alert alert-danger">
                                Invalid OTP code. Please try again.
                            </div>
                        `;
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const messageContainer = document.getElementById('messageContainer');
                if (messageContainer) {
                    messageContainer.innerHTML = `
                        <div class="alert alert-danger">
                            An error occurred. Please try again.
                        </div>
                    `;
                }
            })
            .finally(() => {
                // Reset button state
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    } else {
        console.error('OTP form not found during initialization');
    }
});
