document.addEventListener('DOMContentLoaded', function() {
    // Set up WebSocket connection
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const host = window.location.hostname || '127.0.0.1';
    
    // Use nginx proxy for production, direct connection for development
    let wsUrl;
    if (window.location.hostname === 'tengo.thisisemmanuel.pro') {
        // Production: use nginx proxy (no port specified)
        wsUrl = `${protocol}${host}/ws/delivery/`;
    } else {
        // Development: connect directly to Daphne server
        const port = '8060'; // Daphne server port
        wsUrl = `${protocol}${host}:${port}/ws/delivery/`;
    }
    
    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    
    // Enable console debugging to track WebSocket status
    console.log(`Attempting to connect WebSocket to: ${wsUrl}`);
    
    const pendingDeliveriesTableBody = document.querySelector('#pending-deliveries-table tbody');
    const acceptedDeliveriesTableBody = document.querySelector('table:not(#pending-deliveries-table) tbody');
    let currentForm = null;
    
    // Keep track of processed orders to avoid duplicate notifications
    const processedOrders = new Set();

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.accepted--alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Update connection status display
    function updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            if (connected) {
                statusElement.innerHTML = `
                    <span class="badge bg-success">Connected</span>
                    <small class="text-muted ms-2">Real-time updates enabled</small>
                `;
            } else {
                statusElement.innerHTML = `
                    <span class="badge bg-danger">Disconnected</span>
                    <small class="text-muted ms-2">Reconnecting...</small>
                `;
            }
        }
    }

    function showNotification(message, type = 'info') {
        const notificationsDiv = document.getElementById('notifications');
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
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }

    function updatePendingDeliveriesTable(order) {
        console.log("Updating pending deliveries with order:", order);
        
        // Check if order already exists in table
        let existingRow = document.querySelector(`#pending-deliveries-table tbody tr#order-${order.id}`);
        
        if (existingRow) {
            // Update existing row
            existingRow.querySelector('td:nth-child(2)').innerText = order.restaurant_name;
            existingRow.querySelector('td:nth-child(3)').innerText = order.customer_name;
            existingRow.querySelector('td:nth-child(4)').innerText = order.customer_address;
        } else {
            // Create new row for order
            const newRow = document.createElement('tr');
            newRow.setAttribute('id', `order-${order.id}`);
            
            // Get CSRF token for the form
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? 
                document.querySelector('[name=csrfmiddlewaretoken]').value : '';
            
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
            
            // Update the pending count
            const pendingCountEl = document.getElementById('pending-count');
            if (pendingCountEl) {
                const currentCount = parseInt(pendingCountEl.textContent) || 0;
                pendingCountEl.textContent = currentCount + 1;
            }
            
            // Hide the "no pending orders" message if it's visible
            const noOrdersEl = document.getElementById('no-pending-orders');
            if (noOrdersEl) {
                noOrdersEl.classList.add('d-none');
            }
            
            // Only show notification if we haven't processed this order before
            if (!processedOrders.has(order.id)) {
                showNotification(`New delivery order #${order.id} from ${order.restaurant_name} is ready!`, 'success');
                processedOrders.add(order.id);
                
                // Play notification sound if available
                const notificationSound = document.getElementById('notification-sound');
                if (notificationSound) {
                    notificationSound.play().catch(e => console.log("Could not play notification sound:", e));
                }
            }
        }
    }
    
    function moveOrderBetweenTables(order, fromStatus, toStatus) {
        console.log(`Moving order #${order.id} from ${fromStatus} to ${toStatus}`);
        
        // If order is already in the right place, just update its content
        if ((toStatus === 'Ready for Delivery' && fromStatus !== 'Ready for Delivery') || 
            (toStatus !== 'Ready for Delivery' && fromStatus === 'Ready for Delivery')) {
            
            // Need to move order between tables (from pending to accepted or vice versa)
            
            // 1. Remove from current table
            const oldRow = document.querySelector(`tr#order-${order.id}`);
            if (oldRow) {
                oldRow.remove();
                
                // If removing from pending table, update counter
                if (fromStatus === 'Ready for Delivery') {
                    const pendingCountEl = document.getElementById('pending-count');
                    if (pendingCountEl) {
                        const currentCount = parseInt(pendingCountEl.textContent) || 0;
                        if (currentCount > 0) {
                            pendingCountEl.textContent = currentCount - 1;
                        }
                        
                        // Show "no pending orders" message if this was the last one
                        if (currentCount - 1 === 0) {
                            const noOrdersEl = document.getElementById('no-pending-orders');
                            if (noOrdersEl) {
                                noOrdersEl.classList.remove('d-none');
                            }
                        }
                    }
                }
            }
            
            // 2. Add to correct table based on new status
            if (toStatus === 'Ready for Delivery') {
                // Add to pending deliveries table
                updatePendingDeliveriesTable(order);
            } else {
                // Add to accepted deliveries table
                addToAcceptedDeliveriesTable(order);
            }
            
            // Show notification about the move
            let actionVerb = '';
            let actionType = 'info';
            
            switch (toStatus) {
                case 'Accepted':
                    actionVerb = 'accepted by you';
                    actionType = 'success';
                    break;
                case 'Out for delivery':
                    actionVerb = 'is now out for delivery';
                    actionType = 'info';
                    break;
                case 'Delivered':
                    actionVerb = 'has been delivered';
                    actionType = 'success';
                    break;
                default:
                    actionVerb = `changed status to ${toStatus}`;
            }
            
            showNotification(`Order #${order.id} ${actionVerb}`, actionType);
        } else {
            // Just update the content if it's in the same section
            updateOrderContent(order);
        }
    }
    
    function updateOrderContent(order) {
        // Find the order row in either table
        const orderRow = document.querySelector(`tr#order-${order.id}`);
        
        if (orderRow) {
            // Update basic info
            const cells = orderRow.querySelectorAll('td');
            if (cells.length >= 5) {
                // Update order status if this cell exists
                if (cells[4] && order.status) {
                    cells[4].textContent = order.status;
                }
            }
        }
    }
    
    function addToAcceptedDeliveriesTable(order) {
        if (!acceptedDeliveriesTableBody) {
            console.error("Accepted deliveries table body not found");
            return;
        }
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? 
            document.querySelector('[name=csrfmiddlewaretoken]').value : '';
            
        const newRow = document.createElement('tr');
        newRow.setAttribute('id', `order-${order.id}`);
        
        newRow.innerHTML = `
            <td>${order.id}</td>
            <td>${order.restaurant_name}</td>
            <td>${order.customer_name || 'Customer'}</td>
            <td>${order.customer_address || order.delivery_address || 'Address pending'}</td>
            <td>${order.status}</td>
            <td>
                <form method="POST" class="status-form" data-order-id="${order.id}">
                    {% csrf_token %}
                    <select name="status" class="form-select">
                        <option value="" disabled selected>Select status</option>
                        <option value="Out for delivery">Out for delivery</option>
                        <option value="Delivered">Delivered</option>
                    </select>
                </form>
            </td>
        `;
        
        // Replace the Django template tag with actual value
        newRow.innerHTML = newRow.innerHTML.replace('{% csrf_token %}', 
            `<input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">`);
        
        acceptedDeliveriesTableBody.appendChild(newRow);
    }
    
    function handleReadyForDeliveryOrder(order) {
        // For orders specifically marked as "Ready for Delivery"
        if (order.status === "Ready for Delivery") {
            console.log("Processing Ready for Delivery order:", order);
            
            updatePendingDeliveriesTable({
                id: order.id,
                restaurant_name: order.restaurant_name,
                customer_name: order.customer_name,
                customer_address: order.customer_address,
                delivery_address: order.delivery_address
            });
        }
    }
    
    function handleOrderStatusChange(order) {
        console.log("Handling order status change for:", order);
        
        if (!order || !order.status) return;
        
        // Get current location of order (pending or accepted table)
        const isPendingOrder = !!document.querySelector(`#pending-deliveries-table tbody tr#order-${order.id}`);
        const isAcceptedOrder = !!document.querySelector(`table:not(#pending-deliveries-table) tbody tr#order-${order.id}`);
        
        // Ready for Delivery orders go to pending table
        const shouldBeInPendingTable = order.status === 'Ready for Delivery';
        
        // Other statuses go to accepted table
        const shouldBeInAcceptedTable = ['Accepted', 'Out for delivery', 'Delivered'].includes(order.status);
        
        // Move order if it's in the wrong table
        if (shouldBeInPendingTable && !isPendingOrder) {
            moveOrderBetweenTables(order, 'Other', 'Ready for Delivery');
        } 
        else if (shouldBeInAcceptedTable && !isAcceptedOrder) {
            moveOrderBetweenTables(order, 'Ready for Delivery', order.status);
        }
        // If it's already in the correct table, just update its content
        else {
            updateOrderContent(order);
        }
    }

    // Function to create and setup WebSocket connection
    function createWebSocketConnection() {
        try {
            // Close existing connection if any
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close(1000, 'Creating new connection');
            }
            
            socket = new WebSocket(wsUrl);
            
            socket.onopen = function(event) {
                console.log("WebSocket connection established");
                updateConnectionStatus(true);
                showNotification("Connected to delivery updates service", "success");
                reconnectAttempts = 0; // Reset reconnection attempts on successful connection
            };
            
            socket.onmessage = function(event) {
                console.log("WebSocket message received:", event.data);
                
                try {
                    const data = JSON.parse(event.data);
                    
                    // Skip showing the generic notification message for orders
                    // We'll show a custom one later for orders
                    if (data.message && !data.order) {
                        showNotification(data.message);
                    }
                    
                    // Handle order data from send_order_data event - this is our primary entry point
                    if (data.order) {
                        const order = data.order;
                        
                        // Handle specifically for "Ready for Delivery" orders
                        if (order.status === "Ready for Delivery") {
                            handleReadyForDeliveryOrder(order);
                        } else {
                            // Handle other order status changes (accepted, out for delivery, delivered, etc)
                            handleOrderStatusChange(order);
                        }
                    }
                    
                    // Handle explicit order_update events
                    if (data.type === 'order_update' && data.order) {
                        handleOrderStatusChange(data.order);
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            socket.onerror = function(e) {
                console.error('WebSocket error:', e);
                updateConnectionStatus(false);
            };
            
            socket.onclose = function(e) {
                console.log('WebSocket closed. Code:', e.code, 'Reason:', e.reason);
                updateConnectionStatus(false);
                
                // Don't try to reconnect if it was a normal closure or user-initiated close
                if (e.code === 1000 || e.code === 1001) {
                    console.log('WebSocket closed normally, not attempting to reconnect');
                    return;
                }
                
                // Only attempt reconnection if we haven't exceeded max attempts
                if (reconnectAttempts < maxReconnectAttempts) {
                    attemptReconnect();
                } else {
                    showNotification('Failed to reconnect after several attempts. Please refresh the page.', 'danger');
                }
            };
            
        } catch (error) {
            console.error('Error creating WebSocket connection:', error);
            updateConnectionStatus(false);
        }
    }
    
    // Function to attempt reconnection
    function attemptReconnect() {
        if (reconnectAttempts >= maxReconnectAttempts) {
            showNotification('Failed to reconnect after several attempts. Please refresh the page.', 'danger');
            return;
        }
        
        reconnectAttempts++;
        const timeout = Math.min(1000 * reconnectAttempts, 5000); // Exponential backoff with max 5 seconds
        
        console.log(`Reconnection attempt ${reconnectAttempts} in ${timeout/1000} seconds...`);
        showNotification('Connection to server lost. Attempting to reconnect...', 'warning');
        
        setTimeout(() => {
            createWebSocketConnection();
        }, timeout);
    }
    
    // Initialize WebSocket connection
    createWebSocketConnection();
    
    // OTP handling code
    document.addEventListener('change', function(event) {
        if (event.target.matches('.status-form select[name="status"]')) {
            event.preventDefault();
            const form = event.target.closest('.status-form');
            const orderId = form.getAttribute('data-order-id');
            const status = event.target.value;
            
            if (status === "Out for delivery" || status === "Delivered") {
                currentForm = form;
                showOtpModal(orderId, status);
                localStorage.setItem('modalActive', 'true');
                localStorage.setItem('currentFormId', form.getAttribute('data-order-id'));
            }
        }
    });

    // Handle accept delivery forms with AJAX to prevent page reload
    document.addEventListener('submit', function(event) {
        if (event.target.matches('form[action*="/delivery/accept/"]')) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            
            // Show loading state
            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Accepting...';
            
            // Add proper headers for Django
            const headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            };
            
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: headers
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Success - remove the order from pending table and show notification
                    const orderRow = form.closest('tr');
                    const orderId = orderRow.id.replace('order-', '');
                    
                    showNotification(data.message || `Successfully accepted order #${orderId}!`, 'success');
                    
                    // Remove from pending table
                    orderRow.remove();
                    
                    // Update pending count
                    updatePendingCount();
                    
                    // Verify WebSocket connection is still alive after accepting order
                    if (socket && socket.readyState === WebSocket.OPEN) {
                        console.log('WebSocket connection maintained after accepting order');
                    } else if (socket && socket.readyState === WebSocket.CONNECTING) {
                        console.log('WebSocket is connecting...');
                    } else {
                        console.log('WebSocket connection state after accepting order:', socket ? socket.readyState : 'null');
                        // Don't attempt reconnection here as it might be handled by the main onclose handler
                    }
                } else {
                    showNotification(data.message || 'Failed to accept order', 'error');
                }
            })
            .catch(error => {
                console.error('Error accepting order:', error);
                showNotification('Error accepting order. Please try again.', 'error');
            })
            .finally(() => {
                // Reset button state
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            });
        }
    });

    function showOtpModal(orderId, status) {
        document.getElementById('order_id').value = orderId;
        document.getElementById('status').value = status;
        document.getElementById('otpForm').action = `/delivery/update/${orderId}/`;
        
        var modal = new bootstrap.Modal(document.getElementById('myModal'));
        modal.show();
        
        document.getElementById('myModal').addEventListener('hidden.bs.modal', function() {
            if (!document.getElementById('otpForm').dataset.otpValid) {
                currentForm.querySelector('select[name="status"]').value = "";
            }
            localStorage.removeItem('modalActive');
            localStorage.removeItem('currentFormId');
        }, { once: true });
    }

    // Function to update pending deliveries count
    function updatePendingCount() {
        const pendingCountEl = document.getElementById('pending-count');
        if (pendingCountEl) {
            const currentCount = parseInt(pendingCountEl.textContent) || 0;
            if (currentCount > 0) {
                pendingCountEl.textContent = currentCount - 1;
            }
            
            // Show "no pending orders" message if this was the last one
            if (currentCount - 1 === 0) {
                const noOrdersEl = document.getElementById('no-pending-orders');
                if (noOrdersEl) {
                    noOrdersEl.classList.remove('d-none');
                }
            }
        }
    }
    
    document.getElementById('otpForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const otpCode = document.getElementById('otp_code').value;
        const orderId = document.getElementById('order_id').value;
        const status = document.getElementById('status').value;
        
        fetch(`/delivery/update/${orderId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                otp_code: otpCode,
                status: status
            })
        })
        .then(response => response.json())
        .then(data => {
            const messageContainer = document.getElementById('messageContainer');
            if (data.success) {
                document.getElementById('otpForm').dataset.otpValid = true;
                messageContainer.innerHTML = `<div class="alert alert-success">Success</div>`;
                
                setTimeout(() => {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('myModal'));
                    modal.hide();
                    currentForm.submit();
                }, 3000);
            } else {
                document.getElementById('otpForm').dataset.otpValid = false;
                messageContainer.innerHTML = `<div class="alert alert-danger">OTP is not valid please try again</div>`;
                
                setTimeout(() => {
                    messageContainer.innerHTML = '';
                }, 2000);
                
                currentForm.querySelector('select[name="status"]').value = "";
                currentForm.querySelector('select[name="status"]').disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const messageContainer = document.getElementById('messageContainer');
            messageContainer.innerHTML = `<div class="alert alert-danger">An error occurred while validating the OTP code.</div>`;
            
            setTimeout(() => {
                messageContainer.innerHTML = '';
            }, 2000);
            
            currentForm.querySelector('select[name="status"]').value = "";
            currentForm.querySelector('select[name="status"]').disabled = false;
        });
    });
    
    if (localStorage.getItem('modalActive') === 'true') {
        const formId = localStorage.getItem('currentFormId');
        const form = document.querySelector(`.status-form[data-order-id="${formId}"]`);
        
        if (form) {
            form.querySelector('select[name="status"]').value = "";
        }
        localStorage.removeItem('modalActive');
        localStorage.removeItem('currentFormId');
    }
});