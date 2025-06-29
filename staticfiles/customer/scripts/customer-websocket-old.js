// Customer WebSocket for real-time order updates
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize WebSocket if user is authenticated and user ID is available
    const userDataElement = document.getElementById('user-data');
    if (!userDataElement) return;
    
    const userId = userDataElement.dataset.userId;
    if (!userId) return;

    // WebSocket connection management
    let socket = null;
    let reconnectAttempts = 0;
    let reconnectTimeout = null;
    let isReconnecting = false;
    const maxReconnectAttempts = 3;
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
        const notificationSound = document.getElementById('notification-sound');
        if (notificationSound) {
            notificationSound.play().catch(() => {});
        }
    }

    // Update order status in the UI
    function updateOrderStatus(order) {
        // Update order status in any order lists or tracking pages
        const orderElements = document.querySelectorAll(`[data-order-id="${order.id}"]`);
        
        orderElements.forEach(element => {
            // Update status text
            const statusElement = element.querySelector('.order-status, .status');
            if (statusElement) {
                statusElement.textContent = order.status;
                statusElement.className = `order-status status-${order.status.toLowerCase().replace(/\s+/g, '-')}`;
            }

            // Update delivery person info if available
            if (order.delivery_person) {
                const deliveryPersonElement = element.querySelector('.delivery-person');
                if (deliveryPersonElement) {
                    deliveryPersonElement.textContent = `Delivery Person: ${order.delivery_person}`;
                }
            }

            // Update estimated time if available
            if (order.estimated_time) {
                const etaElement = element.querySelector('.estimated-time');
                if (etaElement) {
                    etaElement.textContent = `ETA: ${order.estimated_time}`;
                }
            }
        });

        // If on order tracking page, update tracking info
        updateOrderTracking(order);
    }

    // Update order tracking specific elements
    function updateOrderTracking(order) {
        // Update delivery driver info if on tracking page
        const driverNameElement = document.querySelector('.driver-name, .driver-info h5');
        const driverEstimateElement = document.querySelector('.estimated-delivery-time');
        
        if (order.delivery_person && driverNameElement) {
            driverNameElement.textContent = order.delivery_person;
        }
        
        if (order.estimated_time && driverEstimateElement) {
            driverEstimateElement.textContent = order.estimated_time;
        }

        // Update progress tracking based on status
        updateProgressTracking(order.status);
    }

    // Update progress tracking visual indicators
    function updateProgressTracking(status) {
        const progressSteps = document.querySelectorAll('.progress-step, .shipping-step');
        
        // Define status order for progress tracking
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
        const priority = data.priority || 'medium';

        // Only show important notifications to users
        let shouldShowNotification = false;
        let toastType = 'info';
        let duration = 5000;
        
        switch (notificationType) {
            case 'payment_confirmed':
            case 'payment_success':
                toastType = 'success';
                shouldShowNotification = true;
                break;
            case 'ready_for_delivery':
                toastType = 'warning';
                shouldShowNotification = true;
                duration = 7000;
                break;
            case 'delivery_accepted':
            case 'out_for_delivery':
                toastType = 'primary';
                shouldShowNotification = true;
                duration = 8000;
                break;
            case 'delivery_completed':
                toastType = 'success';
                shouldShowNotification = true;
                duration = 10000;
                break;
            case 'order_cancelled':
                toastType = 'danger';
                shouldShowNotification = true;
                duration = 12000;
                break;
            default:
                // Handle legacy format - only show important status changes
                if (order && order.status) {
                    if (order.status === 'Delivered') {
                        toastType = 'success';
                        shouldShowNotification = true;
                        duration = 8000;
                    } else if (order.status === 'Cancelled') {
                        toastType = 'danger';
                        shouldShowNotification = true;
                        duration = 10000;
                    } else if (order.status === 'Out for delivery') {
                        toastType = 'primary';
                        shouldShowNotification = true;
                        duration = 7000;
                    }
                }
                break;
        }

        // Show notification only for important updates
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
            if (!window.audioContext) {
                window.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            const audioContext = window.audioContext;
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // Enhanced sound patterns for different notification types
            switch (type) {
                case 'success':
                    // Happy upward melody
                    playMelody([523, 659, 784], [0.15, 0.15, 0.3], audioContext);
                    return;
                case 'attention':
                    // Gentle notification sound
                    playTone(800, 0.2, audioContext);
                    setTimeout(() => playTone(600, 0.2, audioContext), 250);
                    return;
                case 'error':
                    // Lower tone for errors
                    playTone(400, 0.4, audioContext);
                    return;
                default:
                    // Simple notification
                    playTone(600, 0.2, audioContext);
                    return;
            }
        } catch (error) {
            console.log('Audio notification not available:', error.message);
        }
    }

    // Helper function to play a single tone
    function playTone(frequency, duration, audioContext) {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + duration);
    }

    // Helper function to play a melody
    function playMelody(frequencies, durations, audioContext) {
        let currentTime = audioContext.currentTime;
        
        frequencies.forEach((freq, index) => {
            const duration = durations[index] || 0.2;
            setTimeout(() => {
                playTone(freq, duration, audioContext);
            }, currentTime * 1000 + (index * 200));
        });
    }

    // Enhanced order status update with more detailed UI changes
    function updateOrderStatus(order) {
        // Update order status in any order lists or tracking pages
        const orderElements = document.querySelectorAll(`[data-order-id="${order.id}"]`);
        
        orderElements.forEach(element => {
            // Update status text with enhanced styling
            const statusElement = element.querySelector('.order-status, .status');
            if (statusElement) {
                statusElement.textContent = order.status;
                statusElement.className = `order-status badge ${getStatusBadgeClass(order.status)}`;
                
                // Add animation for status change
                statusElement.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    statusElement.style.transform = 'scale(1)';
                }, 200);
            }

            // Update delivery person info with enhanced details
            if (order.delivery_person) {
                const deliveryPersonElement = element.querySelector('.delivery-person');
                if (deliveryPersonElement) {
                    deliveryPersonElement.innerHTML = `
                        <strong>Delivery Person:</strong> ${order.delivery_person}
                        ${order.delivery_person_phone ? `<br><small>Phone: ${order.delivery_person_phone}</small>` : ''}
                    `;
                }
            }

            // Update estimated time with enhanced display
            if (order.estimated_delivery || order.estimated_time) {
                const etaElement = element.querySelector('.estimated-time, .eta');
                if (etaElement) {
                    const eta = order.estimated_delivery || order.estimated_time;
                    etaElement.innerHTML = `<i class="ri-time-line"></i> ETA: ${eta}`;
                }
            }

            // Update tracking message if available
            if (order.tracking_message) {
                const trackingElement = element.querySelector('.tracking-message');
                if (trackingElement) {
                    trackingElement.textContent = order.tracking_message;
                }
            }
        });

        // Enhanced order tracking updates
        updateOrderTracking(order);
        
        // Update progress indicators
        updateProgressTracking(order.status);
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
                        phoneElement.innerHTML = `📞 <a href="tel:${order.delivery_person_phone}">${order.delivery_person_phone}</a>`;
                    }
                }
            });
        }
    }

    // Show enhanced rating prompt
    function showRatingPrompt(orderId, restaurantName) {
        const ratingModal = document.getElementById('rating-modal');
        if (ratingModal) {
            ratingModal.dataset.orderId = orderId;
            ratingModal.querySelector('.restaurant-name').textContent = restaurantName;
            if (window.bootstrap) {
                const modal = new bootstrap.Modal(ratingModal);
                modal.show();
            }
        } else {
            // Fallback: show a simple rating prompt
            if (confirm(`How was your order from ${restaurantName}? Click OK to rate your experience.`)) {
                window.location.href = `/rate-order/${orderId}/`;
            }
        }
    }

    // Update cancelled order UI
    function updateCancelledOrderUI(order) {
        const orderElements = document.querySelectorAll(`[data-order-id="${order.id}"]`);
        orderElements.forEach(element => {
            element.style.opacity = '0.6';
            element.classList.add('cancelled-order');
            
            // Add refund information if available
            if (order.refund_amount) {
                const refundInfo = document.createElement('div');
                refundInfo.className = 'refund-info alert alert-info mt-2';
                refundInfo.innerHTML = `
                    <i class="ri-refund-line"></i> 
                    Refund of $${order.refund_amount} will be processed within ${order.refund_timeline || '3-5 business days'}
                `;
                element.appendChild(refundInfo);
            }
        });
    }

    // Enable order tracking features
    function enableOrderTracking(order) {
        if (order.can_track) {
            const trackingButtons = document.querySelectorAll('.track-order-btn');
            trackingButtons.forEach(btn => {
                btn.disabled = false;
                btn.textContent = 'Track Live';
                btn.classList.add('btn-primary');
            });
        }
    }

    // Get CSS class for status badges with enhanced styling
    function getStatusBadgeClass(status) {
        const statusClasses = {
            'Pending': 'bg-secondary',
            'Confirmed': 'bg-primary',
            'Preparing': 'bg-info',
            'Ready for Delivery': 'bg-warning text-dark',
            'Accepted': 'bg-success',
            'Out for delivery': 'bg-primary',
            'Delivered': 'bg-success',
            'Cancelled': 'bg-danger'
        };
        
        return statusClasses[status] || 'bg-secondary';
    }

    // Show rating modal (enhanced version)
    function showRatingModal(orderId, restaurantName = '') {
        const ratingModal = document.getElementById('rating-modal');
        if (ratingModal) {
            // Set order ID in modal
            ratingModal.dataset.orderId = orderId;
            if (restaurantName && ratingModal.querySelector('.restaurant-name')) {
                ratingModal.querySelector('.restaurant-name').textContent = restaurantName;
            }
            // Show modal using Bootstrap
            if (window.bootstrap) {
                const modal = new bootstrap.Modal(ratingModal);
                modal.show();
            }
        } else {
            // Fallback: redirect to rating page or show simple prompt
            if (restaurantName) {
                if (confirm(`How was your order from ${restaurantName}? Click OK to rate your experience.`)) {
                    window.location.href = `/rate-order/${orderId}/`;
                }
            } else {
                if (confirm('How was your order? Click OK to rate your experience.')) {
                    window.location.href = `/rate-order/${orderId}/`;
                }
            }
        }
    }

    // Update connection status indicator
    function updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connection-status');
        if (statusIndicator) {
            if (connected) {
                statusIndicator.innerHTML = '<span class="badge bg-success">Live Updates Active</span>';
            } else {
                statusIndicator.innerHTML = '<span class="badge bg-warning">Reconnecting...</span>';
            }
        }
    }

    // Enhanced utility functions for new notification types
    function updateDeliveryPersonInfo(order) {
        const deliveryInfoElements = document.querySelectorAll('.delivery-person-info, .driver-info');
        
        deliveryInfoElements.forEach(element => {
            if (order.delivery_person) {
                element.innerHTML = `
                    <div class="delivery-person-details">
                        <strong>${order.delivery_person}</strong>
                        ${order.delivery_person_phone ? `<br><small>📞 ${order.delivery_person_phone}</small>` : ''}
                        ${order.estimated_delivery ? `<br><small>🕒 ETA: ${order.estimated_delivery}</small>` : ''}
                    </div>
                `;
                element.style.display = 'block';
            }
        });
    }

    function updatePickupStatus(order) {
        const pickupElements = document.querySelectorAll('.pickup-status');
        pickupElements.forEach(element => {
            element.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-check-circle"></i>
                    Your order has been picked up and is on the way!
                </div>
            `;
        });
    }

    function enableOrderTracking(order) {
        const trackingElements = document.querySelectorAll('.order-tracking');
        trackingElements.forEach(element => {
            if (order.can_track) {
                element.style.display = 'block';
                element.innerHTML = `
                    <div class="tracking-active">
                        <h6>📍 Live Tracking Available</h6>
                        <p>${order.tracking_message || 'Your order is on the way!'}</p>
                    </div>
                `;
            }
        });
    }

    function updateCancelledOrderUI(order) {
        const orderElements = document.querySelectorAll(`[data-order-id="${order.id}"]`);
        
        orderElements.forEach(element => {
            // Add cancelled styling
            element.classList.add('order-cancelled');
            element.style.opacity = '0.7';
            
            // Update status
            const statusElement = element.querySelector('.order-status, .status');
            if (statusElement) {
                statusElement.className = 'order-status badge bg-danger';
                statusElement.textContent = 'Cancelled';
            }
            
            // Show refund information if available
            if (order.refund_amount) {
                const refundElement = document.createElement('div');
                refundElement.className = 'refund-info mt-2';
                refundElement.innerHTML = `
                    <small class="text-muted">
                        💰 Refund of ${order.refund_amount} will be processed within ${order.refund_timeline}
                    </small>
                `;
                element.appendChild(refundElement);
            }
        });
    }

    function showRatingPrompt(orderId, restaurantName) {
        // Only show if not already shown
        if (document.querySelector('.rating-prompt')) return;
        
        const ratingModal = document.createElement('div');
        ratingModal.className = 'rating-prompt modal fade show';
        ratingModal.style.display = 'block';
        ratingModal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Rate Your Experience</h5>
                        <button type="button" class="btn-close" onclick="this.closest('.rating-prompt').remove()"></button>
                    </div>
                    <div class="modal-body">
                        <p>How was your experience with ${restaurantName}?</p>
                        <div class="rating-stars mb-3">
                            ${[1,2,3,4,5].map(star => `
                                <span class="star" data-rating="${star}">⭐</span>
                            `).join('')}
                        </div>
                        <textarea class="form-control" placeholder="Leave a review (optional)"></textarea>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="this.closest('.rating-prompt').remove()">Maybe Later</button>
                        <button type="button" class="btn btn-primary" onclick="submitRating(${orderId})">Submit Rating</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(ratingModal);
        
        // Add click handlers for stars
        ratingModal.querySelectorAll('.star').forEach(star => {
            star.addEventListener('click', function() {
                const rating = this.dataset.rating;
                ratingModal.querySelectorAll('.star').forEach((s, index) => {
                    s.style.opacity = index < rating ? '1' : '0.3';
                });
            });
        });
    }

    // WebSocket event handlers
    socket.onopen = function(event) {
        console.log('Customer WebSocket connected');
        reconnectAttempts = 0;
        updateConnectionStatus(true);
        showNotification('Connected to live order updates', 'success', 3000);
    };

    socket.onmessage = function(event) {
        console.log('Customer WebSocket message received:', event.data);
        
        try {
            const data = JSON.parse(event.data);
            
            // Handle different message types
            switch(data.type) {
                case 'order_update':
                    handleOrderUpdate(data);
                    break;
                case 'delivery_update':
                    handleOrderUpdate(data);
                    break;
                case 'payment_update':
                    showNotification(data.message, 'info');
                    break;
                case 'general_notification':
                    showNotification(data.message, 'info');
                    break;
                default:
                    // Handle legacy format
                    if (data.message) {
                        showNotification(data.message, 'info');
                    }
                    if (data.order) {
                        updateOrderStatus(data.order);
                    }
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    };

    socket.onclose = function(event) {
        console.log('Customer WebSocket disconnected');
        updateConnectionStatus(false);
        
        // Attempt to reconnect without reloading the page
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            const timeout = Math.min(1000 * reconnectAttempts, 5000); // Exponential backoff
            
            showNotification(`Connection lost. Reconnecting in ${timeout/1000} seconds...`, 'warning', 3000);
            
            setTimeout(() => {
                console.log(`Attempting to reconnect... (Attempt ${reconnectAttempts})`);
                // Create new WebSocket connection instead of reloading page
                try {
                    const newSocket = new WebSocket(wsUrl);
                    
                    newSocket.onopen = function(event) {
                        console.log('Customer WebSocket reconnected successfully');
                        reconnectAttempts = 0;
                        updateConnectionStatus(true);
                        showNotification('Reconnected to live order updates', 'success', 3000);
                        
                        // Replace the old socket with the new one
                        socket.onopen = newSocket.onopen;
                        socket.onmessage = newSocket.onmessage;
                        socket.onclose = newSocket.onclose;
                        socket.onerror = newSocket.onerror;
                        socket = newSocket;
                    };
                    
                    newSocket.onmessage = socket.onmessage;
                    newSocket.onclose = socket.onclose;
                    newSocket.onerror = socket.onerror;
                    
                } catch (error) {
                    console.error('Failed to create new WebSocket connection:', error);
                    // Retry with exponential backoff
                    socket.onclose(event);
                }
            }, timeout);
        } else {
            showNotification('Connection lost. Please refresh the page manually to restore live updates.', 'warning', 15000);
        }
    };

    socket.onerror = function(error) {
        console.error('Customer WebSocket error:', error);
        updateConnectionStatus(false);
        showNotification('Connection error. Live updates may be unavailable.', 'warning', 5000);
    };

    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close();
        }
    });
});
