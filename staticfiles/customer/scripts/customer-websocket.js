// Customer WebSocket for real-time order updates - Production Ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize WebSocket if user is authenticated and user ID is available
    const userDataElement = document.getElementById('user-data');
    if (!userDataElement) return;
    
    const userId = userDataElement.dataset.userId;
    if (!userId) return;

    // WebSocket connection management - optimized for production
    let socket = null;
    let reconnectAttempts = 0;
    let reconnectTimeout = null;
    let isReconnecting = false;
    let hasConnectedBefore = false;
    const maxReconnectAttempts = 5;
    const baseReconnectDelay = 2000;
    
    // Set up WebSocket connection
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const host = window.location.hostname || '127.0.0.1';
    
    // Use nginx proxy for production, direct connection for development
    let wsUrl;
    if (window.location.hostname === 'tengo.thisisemmanuel.pro') {
        wsUrl = `${protocol}${host}/ws/customer/${userId}/`;
    } else {
        const port = '8060';
        wsUrl = `${protocol}${host}:${port}/ws/customer/${userId}/`;
    }

    // Show notification function (simplified for production)
    function showNotification(message, type = 'info', duration = 5000) {
        let notificationContainer = document.getElementById('customer-notifications');
        
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'customer-notifications';
            notificationContainer.className = 'position-fixed top-0 end-0 p-3';
            notificationContainer.style.zIndex = '9999';
            document.body.appendChild(notificationContainer);
        }

        const notification = document.createElement('div');
        notification.className = `toast align-items-center text-white bg-${type} border-0 show`;
        notification.setAttribute('role', 'alert');
        notification.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>TenGo:</strong> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        notificationContainer.appendChild(notification);

        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }
        }, duration);

        // Play notification sound if available
        playNotificationSound();
    }

    // Simplified audio notification
    function playNotificationSound() {
        const notificationSound = document.getElementById('notification-sound');
        if (notificationSound) {
            notificationSound.play().catch(() => {});
        }
    }

    // Update order status in the UI
    function updateOrderStatus(order) {
        const orderElements = document.querySelectorAll(`[data-order-id="${order.id}"]`);
        
        orderElements.forEach(element => {
            const statusElement = element.querySelector('.order-status, .status');
            if (statusElement) {
                statusElement.textContent = order.status;
                statusElement.className = `order-status status-${order.status.toLowerCase().replace(/\s+/g, '-')}`;
            }

            if (order.delivery_person) {
                const deliveryPersonElement = element.querySelector('.delivery-person');
                if (deliveryPersonElement) {
                    deliveryPersonElement.textContent = `Delivery Person: ${order.delivery_person}`;
                }
            }

            if (order.estimated_time) {
                const etaElement = element.querySelector('.estimated-time');
                if (etaElement) {
                    etaElement.textContent = `ETA: ${order.estimated_time}`;
                }
            }
        });

        updateOrderTracking(order);
    }

    // Update order tracking specific elements
    function updateOrderTracking(order) {
        const driverNameElement = document.querySelector('.driver-name, .driver-info h5');
        const driverEstimateElement = document.querySelector('.estimated-delivery-time');
        
        if (order.delivery_person && driverNameElement) {
            driverNameElement.textContent = order.delivery_person;
        }
        
        if (order.estimated_time && driverEstimateElement) {
            driverEstimateElement.textContent = order.estimated_time;
        }

        updateProgressTracking(order.status);
    }

    // Update progress tracking visual indicators
    function updateProgressTracking(status) {
        const progressSteps = document.querySelectorAll('.progress-step, .shipping-step');
        
        const statusOrder = ['Confirmed', 'Preparing', 'Ready for Delivery', 'Accepted', 'Out for delivery', 'Delivered'];
        const currentIndex = statusOrder.indexOf(status);

        progressSteps.forEach((step, index) => {
            const stepElement = step.querySelector('.step-indicator, .step-circle');
            if (stepElement) {
                if (index <= currentIndex) {
                    stepElement.classList.add('completed', 'active');
                } else {
                    stepElement.classList.remove('completed', 'active');
                }
            }
        });
    }

    // Handle different types of order updates (production optimized)
    function handleOrderUpdate(data) {
        const order = data.order;
        const message = data.message;
        const notificationType = data.notification_type || 'general';

        // Only show critical notifications to users
        let shouldShowNotification = false;
        let toastType = 'info';
        let duration = 5000;
        
        switch (notificationType) {
            case 'payment_confirmed':
            case 'payment_success':
                toastType = 'success';
                shouldShowNotification = true;
                break;
            case 'delivery_accepted':
            case 'out_for_delivery':
                toastType = 'primary';
                shouldShowNotification = true;
                duration = 6000;
                break;
            case 'delivery_completed':
                toastType = 'success';
                shouldShowNotification = true;
                duration = 8000;
                break;
            case 'order_cancelled':
                toastType = 'danger';
                shouldShowNotification = true;
                duration = 10000;
                break;
            default:
                // Handle legacy format - only show critical status changes
                if (order && order.status) {
                    if (order.status === 'Delivered') {
                        toastType = 'success';
                        shouldShowNotification = true;
                        duration = 6000;
                    } else if (order.status === 'Cancelled') {
                        toastType = 'danger';
                        shouldShowNotification = true;
                        duration = 8000;
                    } else if (order.status === 'Out for delivery') {
                        toastType = 'primary';
                        shouldShowNotification = true;
                        duration = 5000;
                    }
                }
                break;
        }

        // Show notification only for critical updates
        if (shouldShowNotification) {
            showNotification(message, toastType, duration);
        }

        // Update UI elements
        if (order) {
            updateOrderStatus(order);
            
            // Handle special actions based on notification type
            switch (notificationType) {
                case 'delivery_completed':
                    if (order.action_required === 'rate_order') {
                        setTimeout(() => {
                            showRatingPrompt(order.id, order.restaurant_name);
                        }, 3000);
                    }
                    break;
                case 'order_cancelled':
                    updateCancelledOrderUI(order);
                    break;
                case 'delivery_accepted':
                    updateDeliveryPersonInfo(order);
                    break;
                case 'out_for_delivery':
                    enableOrderTracking(order);
                    break;
            }
        }
    }

    // Enhanced delivery person info update
    function updateDeliveryPersonInfo(order) {
        if (order.delivery_person) {
            const deliveryInfoElements = document.querySelectorAll('.driver-info, .delivery-person-info');
            deliveryInfoElements.forEach(element => {
                const nameElement = element.querySelector('.driver-name, h5');
                if (nameElement) {
                    nameElement.textContent = order.delivery_person;
                }
                
                if (order.delivery_person_phone) {
                    const phoneElement = element.querySelector('.driver-phone, .contact-info');
                    if (phoneElement) {
                        phoneElement.textContent = order.delivery_person_phone;
                    }
                }
            });
        }
    }

    // Show rating prompt
    function showRatingPrompt(orderId, restaurantName) {
        const ratingModal = showRatingModal(orderId, restaurantName);
        if (ratingModal) {
            ratingModal.show();
        }
    }

    // Update cancelled order UI
    function updateCancelledOrderUI(order) {
        const orderElements = document.querySelectorAll(`[data-order-id="${order.id}"]`);
        orderElements.forEach(element => {
            element.classList.add('order-cancelled');
            const statusElement = element.querySelector('.order-status, .status');
            if (statusElement) {
                statusElement.className = 'order-status badge bg-danger';
                statusElement.textContent = 'Cancelled';
            }
        });
    }

    // Enable order tracking features
    function enableOrderTracking(order) {
        const trackingButton = document.querySelector(`[data-order-id="${order.id}"] .track-order-btn`);
        if (trackingButton) {
            trackingButton.style.display = 'block';
            trackingButton.href = `/order-tracking/${order.id}/`;
        }
    }

    // Get CSS class for status badges
    function getStatusBadgeClass(status) {
        const statusClasses = {
            'Pending': 'bg-warning',
            'Confirmed': 'bg-info',
            'Preparing': 'bg-primary',
            'Ready for Delivery': 'bg-warning',
            'Accepted': 'bg-info',
            'Out for delivery': 'bg-primary',
            'Delivered': 'bg-success',
            'Cancelled': 'bg-danger'
        };
        return statusClasses[status] || 'bg-secondary';
    }

    // Show rating modal
    function showRatingModal(orderId, restaurantName = '') {
        const existingModal = document.getElementById('ratingModal');
        if (existingModal) {
            existingModal.remove();
        }

        const modalHtml = `
            <div class="modal fade" id="ratingModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Rate Your Experience</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>How was your experience with ${restaurantName}?</p>
                            <div class="rating-stars text-center mb-3">
                                ${[1,2,3,4,5].map(i => `<i class="ri-star-line fs-2 text-warning rating-star" data-rating="${i}"></i>`).join('')}
                            </div>
                            <textarea class="form-control" placeholder="Leave a comment (optional)" id="ratingComment"></textarea>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Skip</button>
                            <button type="button" class="btn btn-primary" id="submitRating">Submit Rating</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        const modal = new bootstrap.Modal(document.getElementById('ratingModal'));
        
        // Add rating functionality
        const stars = document.querySelectorAll('.rating-star');
        let selectedRating = 0;
        
        stars.forEach(star => {
            star.addEventListener('click', function() {
                selectedRating = parseInt(this.dataset.rating);
                stars.forEach((s, index) => {
                    if (index < selectedRating) {
                        s.classList.remove('ri-star-line');
                        s.classList.add('ri-star-fill');
                    } else {
                        s.classList.remove('ri-star-fill');
                        s.classList.add('ri-star-line');
                    }
                });
            });
        });

        document.getElementById('submitRating').addEventListener('click', function() {
            if (selectedRating > 0) {
                // Submit rating logic would go here
                modal.hide();
                showNotification('Thank you for your rating!', 'success');
            } else {
                showNotification('Please select a rating', 'warning');
            }
        });

        return modal;
    }

    // Update connection status indicator
    function updateConnectionStatus(connected) {
        const statusElement = document.getElementById('ws-connection-status');
        if (statusElement) {
            if (connected) {
                statusElement.innerHTML = '<span class="badge bg-success"><i class="ri-wifi-line"></i> Connected</span>';
                statusElement.style.display = 'block';
                setTimeout(() => {
                    statusElement.style.display = 'none';
                }, 3000);
            } else {
                statusElement.innerHTML = '<span class="badge bg-danger"><i class="ri-wifi-off-line"></i> Disconnected</span>';
                statusElement.style.display = 'block';
            }
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
                const wasReconnecting = reconnectAttempts > 0;
                reconnectAttempts = 0;
                isReconnecting = false;
                if (reconnectTimeout) {
                    clearTimeout(reconnectTimeout);
                    reconnectTimeout = null;
                }
                updateConnectionStatus(true);
 
                hasConnectedBefore = true;
            };

            socket.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    handleOrderUpdate(data);
                } catch (error) {
                    // Invalid JSON received, ignore silently
                }
            };

            socket.onclose = function(event) {
                updateConnectionStatus(false);

                // Only attempt reconnection if we had a connection before and it wasn't a normal close
                if (hasConnectedBefore && !isReconnecting && reconnectAttempts < maxReconnectAttempts && event.code !== 1000) {
                    isReconnecting = true;
                    reconnectAttempts++;
                    
                    const delay = Math.min(baseReconnectDelay * Math.pow(1.5, reconnectAttempts - 1), 10000);
                    
                    reconnectTimeout = setTimeout(() => {
                        isReconnecting = false;
                        connectWebSocket();
                    }, delay);
                } else if (reconnectAttempts >= maxReconnectAttempts) {
                    showNotification('Unable to maintain connection. Please refresh the page.', 'danger', 10000);
                }
            };

            socket.onerror = function(error) {
                updateConnectionStatus(false);
                // Production: Don't show error notifications unless critical
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

    // Handle page visibility changes to manage connections efficiently
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            if (!socket || socket.readyState === WebSocket.CLOSED) {
                connectWebSocket();
            }
        }
    });
});
