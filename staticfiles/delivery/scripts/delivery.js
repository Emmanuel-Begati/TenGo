document.addEventListener('DOMContentLoaded', function() {
    const socket = new WebSocket((window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws/delivery/');
    const pendingDeliveriesTableBody = document.querySelector('#pending-deliveries-table tbody');
    let currentForm = null;

    const alerts = document.querySelectorAll('.accepted--alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove(); 
            }, 300); // Timeout to allow fade transition to complete
        }, 5000); // 5 seconds timeout
    });

    function updatePendingDeliveriesTable(order) {
        let existingRow = document.querySelector(`#pending-deliveries-table tbody tr#order-${order.id}`);
        if (existingRow) {
            existingRow.querySelector('td:nth-child(2)').innerText = order.restaurant_name;
            existingRow.querySelector('td:nth-child(3)').innerText = order.customer_name;
            existingRow.querySelector('td:nth-child(4)').innerText = order.customer_address;
        } else {
            const newRow = document.createElement('tr');
            newRow.setAttribute('id', `order-${order.id}`);
            newRow.innerHTML = `
                <td>${order.id}</td>
                <td>${order.restaurant_name}</td>
                <td>${order.customer_name}</td>
                <td>${order.customer_address}</td>
                <td>
                    <form method="POST" action="/delivery/accept/${order.id}/">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${document.querySelector('[name=csrfmiddlewaretoken]').value}">
                        <button type="submit" class="btn btn-success">Accept</button>
                    </form>
                </td>
            `;
            pendingDeliveriesTableBody.appendChild(newRow);
        }
    }

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.message) {
            const notificationsDiv = document.getElementById('notifications');
            const notification = document.createElement('div');
            notification.className = 'alert alert-info';
            notification.innerText = data.message;
            notificationsDiv.appendChild(notification);

            // Set timeout for the notification to disappear after 5 seconds
            setTimeout(() => {
                notification.remove();
            }, 5000);
        }
        if (data.order) {
            const order = data.order;
            updatePendingDeliveriesTable(order);
        }
    };

    socket.onclose = function(e) {
        console.error('WebSocket closed unexpectedly');
    };

    document.addEventListener('change', function(event) {
        if (event.target.matches('.status-form select[name="status"]')) {
            event.preventDefault();
            const form = event.target.closest('.status-form');
            const orderId = form.getAttribute('data-order-id');
            const status = event.target.value;
            if (status === "Out for delivery" || status === "Delivered") {
                currentForm = form;
                showOtpModal(orderId, status);
                // Store the modal state in localStorage
                localStorage.setItem('modalActive', 'true');
                localStorage.setItem('currentFormId', form.getAttribute('data-order-id'));
            }
        }
    });

    function showOtpModal(orderId, status) {
        document.getElementById('order_id').value = orderId;
        document.getElementById('status').value = status;
        document.getElementById('otpForm').action = `/delivery/update/${orderId}/`;
        var modal = new bootstrap.Modal(document.getElementById('myModal'));
        modal.show();

        document.getElementById('myModal').addEventListener('hidden.bs.modal', function () {
            if (!document.getElementById('otpForm').dataset.otpValid) {
                currentForm.querySelector('select[name="status"]').value = "";
            }
            // Clear the modal state from localStorage
            localStorage.removeItem('modalActive');
            localStorage.removeItem('currentFormId');
        }, { once: true });
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

    // Check localStorage on page load to reset status if modal was active
    if (localStorage.getItem('modalActive') === 'true') {
        const formId = localStorage.getItem('currentFormId');
        const form = document.querySelector(`.status-form[data-order-id="${formId}"]`);
        if (form) {
            form.querySelector('select[name="status"]').value = "";
        }
        // Clear the modal state from localStorage
        localStorage.removeItem('modalActive');
        localStorage.removeItem('currentFormId');
    }
});