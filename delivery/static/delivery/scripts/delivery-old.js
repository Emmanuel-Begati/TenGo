document.addEventListener('DOMContentLoaded', function() {
    // Set up WebSocket connection
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const host = window.location.hostname || '127.0.0.1';
    
    // Use nginx proxy for production, direct connection for development
    let wsUrl;
    if (window.location.hostname === 'tengo.thisisemmanuel.pro') {
        wsUrl = `${protocol}${host}/ws/delivery/`;
    } else {
        const port = '8060';
        wsUrl = `${protocol}${host}:${port}/ws/delivery/`;
    }
    
    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    let isReconnecting = false;
    
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
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Update connection status display
    function updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.innerHTML = connected 
                ? `<span class="badge bg-success">Connected</span><small class="text-muted ms-2">Real-time updates enabled</small>`
                : `<span class="badge bg-danger">Disconnected</span><small class="text-muted ms-2">Reconnecting...</small>`;
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
        console.log("Updating pending deliveries with order:", order);
        
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
            updatePendingCount(1);
            hideNoOrdersMessage();
            
            // Show notification only for new orders
            if (!processedOrders.has(order.id)) {
                showNotification(`New delivery order #${order.id} from ${order.restaurant_name} is ready!`, 'success');
                processedOrders.add(order.id);
                
                // Play notification sound if available
                const notificationSound = document.getElementById('notification-sound');
                notificationSound?.play().catch(e => console.log("Could not play notification sound:", e));
            }
        }
    }
    
    function addToAcceptedDeliveriesTable(order) {
        if (!acceptedDeliveriesTableBody) {
            console.error("Accepted deliveries table body not found");
            return;
        }
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
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
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                    <select name="status" class="form-select">
                        <option value="" disabled selected>Select status</option>
                        <option value="Out for delivery">Out for delivery</option>
                        <option value="Delivered">Delivered</option>
                    </select>
                </form>
            </td>
        `;
        
        acceptedDeliveriesTableBody.appendChild(newRow);
    }
    
    function moveOrderBetweenTables(order, fromStatus, toStatus) {
        console.log(`Moving order #${order.id} from ${fromStatus} to ${toStatus}`);
        
        const oldRow = document.querySelector(`tr#order-${order.id}`);
        if (oldRow) {
            oldRow.remove();
            
            // Update pending count if removing from pending table
            if (fromStatus === 'Ready for Delivery') {
                updatePendingCount(-1);
            }
        }
        
        // Add to correct table
        if (toStatus === 'Ready for Delivery') {
            updatePendingDeliveriesTable(order);
        } else {
            addToAcceptedDeliveriesTable(order);
        }
        
        // Show notification
        const actionMessages = {
            'Accepted': { verb: 'accepted by you', type: 'success' },
            'Out for delivery': { verb: 'is now out for delivery', type: 'info' },
            'Delivered': { verb: 'has been delivered', type: 'success' }
        };
        
        const action = actionMessages[toStatus] || { verb: `changed status to ${toStatus}`, type: 'info' };
        showNotification(`Order #${order.id} ${action.verb}`, action.type);
    }
    
    function updateOrderContent(order) {
        const orderRow = document.querySelector(`tr#order-${order.id}`);
        if (orderRow) {
            const statusCell = orderRow.querySelector('td:nth-child(5)');
            if (statusCell && order.status) {
                statusCell.textContent = order.status;
            }
        }
    }
    
    function handleOrderStatusChange(order) {
        console.log("Handling order status change for:", order);
        
        if (!order?.status) return;
        
        const isPendingOrder = !!document.querySelector(`#pending-deliveries-table tbody tr#order-${order.id}`);
        const isAcceptedOrder = !!document.querySelector(`table:not(#pending-deliveries-table) tbody tr#order-${order.id}`);
        
        const shouldBeInPendingTable = order.status === 'Ready for Delivery';
        const shouldBeInAcceptedTable = ['Accepted', 'Out for delivery', 'Delivered'].includes(order.status);
        
        if (shouldBeInPendingTable && !isPendingOrder) {
            moveOrderBetweenTables(order, 'Other', 'Ready for Delivery');
        } else if (shouldBeInAcceptedTable && !isAcceptedOrder) {
            moveOrderBetweenTables(order, 'Ready for Delivery', order.status);
        } else {
            updateOrderContent(order);
        }
    }

    // Improved WebSocket connection handling
    function createWebSocketConnection() {
        if (isReconnecting) return;
        
        try {
            // Close existing connection cleanly
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close(1000, 'Creating new connection');
            }
            
            socket = new WebSocket(wsUrl);
            
            socket.onopen = function(event) {
                console.log("WebSocket connection established");
                updateConnectionStatus(true);
                showNotification("Connected to delivery updates service", "success");
                reconnectAttempts = 0;
                isReconnecting = false;
            };
            
            socket.onmessage = function(event) {
                console.log("WebSocket message received:", event.data);
                
                try {
                    const data = JSON.parse(event.data);
                    
                    // Show generic messages only if no order data
                    if (data.message && !data.order) {
                        showNotification(data.message);
                    }
                    
                    // Handle order updates
                    if (data.order) {
                        if (data.order.status === "Ready for Delivery") {
                            updatePendingDeliveriesTable(data.order);
                        } else {
                            handleOrderStatusChange(data.order);
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
                
                // Don't reconnect for normal closures
                if (e.code === 1000 || e.code === 1001 || isReconnecting) {
                    console.log('WebSocket closed normally or already reconnecting');
                    return;
                }
                
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
    
    function attemptReconnect() {
        if (isReconnecting || reconnectAttempts >= maxReconnectAttempts) return;
        
        isReconnecting = true;
        reconnectAttempts++;
        const timeout = Math.min(1000 * reconnectAttempts, 5000);
        
        console.log(`Reconnection attempt ${reconnectAttempts} in ${timeout/1000} seconds...`);
        showNotification('Connection to server lost. Attempting to reconnect...', 'warning');
        
        setTimeout(() => {
            createWebSocketConnection();
        }, timeout);
    }
    
    // Initialize WebSocket connection
    createWebSocketConnection();
    
    // Helper functions
    function updatePendingCount(change) {
        const pendingCountEl = document.getElementById('pending-count');
        if (pendingCountEl) {
            const currentCount = Math.max(0, (parseInt(pendingCountEl.textContent) || 0) + change);
            pendingCountEl.textContent = currentCount;
            
            if (currentCount === 0) {
                showNoOrdersMessage();
            }
        }
    }
    
    function hideNoOrdersMessage() {
        const noOrdersEl = document.getElementById('no-pending-orders');
        noOrdersEl?.classList.add('d-none');
    }
    
    function showNoOrdersMessage() {
        const noOrdersEl = document.getElementById('no-pending-orders');
        noOrdersEl?.classList.remove('d-none');
    }
    
    // Event handlers
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
                localStorage.setItem('currentFormId', orderId);
            }
        }
    });

    // Handle accept delivery forms with AJAX
    document.addEventListener('submit', function(event) {
        if (event.target.matches('form[action*="/delivery/accept/"]')) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            
            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Accepting...';
            
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const orderRow = form.closest('tr');
                    const orderId = orderRow.id.replace('order-', '');
                    
                    showNotification(data.message || `Successfully accepted order #${orderId}!`, 'success');
                    orderRow.remove();
                    updatePendingCount(-1);
                } else {
                    showNotification(data.message || 'Failed to accept order', 'error');
                }
            })
            .catch(error => {
                console.error('Error accepting order:', error);
                showNotification('Error accepting order. Please try again.', 'error');
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            });
        }
    });

    function showOtpModal(orderId, status) {
        document.getElementById('order_id').value = orderId;
        document.getElementById('status').value = status;
        document.getElementById('otpForm').action = `/delivery/update/${orderId}/`;
        
        const modal = new bootstrap.Modal(document.getElementById('myModal'));
        modal.show();
        
        document.getElementById('myModal').addEventListener('hidden.bs.modal', function() {
            if (!document.getElementById('otpForm').dataset.otpValid) {
                currentForm.querySelector('select[name="status"]').value = "";
            }
            localStorage.removeItem('modalActive');
            localStorage.removeItem('currentFormId');
        }, { once: true });
    }
    
    // OTP form handling
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
            body: new URLSearchParams({ otp_code: otpCode, status: status })
        })
        .then(response => response.json())
        .then(data => {
            const messageContainer = document.getElementById('messageContainer');
            if (data.success) {
                document.getElementById('otpForm').dataset.otpValid = true;
                messageContainer.innerHTML = `<div class="alert alert-success">Success</div>`;
                
                setTimeout(() => {
                    bootstrap.Modal.getInstance(document.getElementById('myModal')).hide();
                    currentForm.submit();
                }, 3000);
            } else {
                document.getElementById('otpForm').dataset.otpValid = false;
                messageContainer.innerHTML = `<div class="alert alert-danger">OTP is not valid please try again</div>`;
                
                setTimeout(() => messageContainer.innerHTML = '', 2000);
                
                const statusSelect = currentForm.querySelector('select[name="status"]');
                statusSelect.value = "";
                statusSelect.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const messageContainer = document.getElementById('messageContainer');
            messageContainer.innerHTML = `<div class="alert alert-danger">An error occurred while validating the OTP code.</div>`;
            
            setTimeout(() => messageContainer.innerHTML = '', 2000);
            
            const statusSelect = currentForm.querySelector('select[name="status"]');
            statusSelect.value = "";
            statusSelect.disabled = false;
        });
    });
    
    // Handle modal state from localStorage
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