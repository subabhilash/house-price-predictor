// Custom JavaScript for House Price Predictor

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation feedback
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Loading states for buttons
    const loadingButtons = document.querySelectorAll('.btn-loading');
    loadingButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
            this.disabled = true;
            
            // Re-enable after 3 seconds (fallback)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 3000);
        });
    });

    // Price formatting
    const priceInputs = document.querySelectorAll('.price-input');
    priceInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            let value = this.value.replace(/[^\d]/g, '');
            if (value) {
                this.value = parseInt(value).toLocaleString();
            }
        });
    });

    // Tooltip initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// AJAX prediction function (for future use)
function predictPrice(formData) {
    return fetch('/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data.predicted_price;
        } else {
            throw new Error(data.error);
        }
    });
}

// Update price display with animation
function updatePriceDisplay(price) {
    const priceElement = document.getElementById('predicted-price');
    if (priceElement) {
        priceElement.style.opacity = '0';
        setTimeout(() => {
            priceElement.textContent = '$' + price.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            priceElement.style.opacity = '1';
        }, 300);
    }
}
