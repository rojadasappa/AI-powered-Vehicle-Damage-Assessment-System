// Main JavaScript for Vehicle Damage Assessment System

// Global variables
let currentUser = null;
let damageReports = [];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadUserData();
});

// Initialize application
function initializeApp() {
    // Check if user is authenticated
    checkAuthentication();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
    
    // Setup form validation
    setupFormValidation();
}

// Setup event listeners
function setupEventListeners() {
    // Global click handlers
    document.addEventListener('click', handleGlobalClick);
    
    // Form submission handlers
    document.addEventListener('submit', handleFormSubmit);
    
    // File upload handlers
    document.addEventListener('change', handleFileUpload);
    
    // Drag and drop handlers
    setupDragAndDrop();
}

// Check user authentication status
function checkAuthentication() {
    // This would typically check for a JWT token or session
    const authToken = localStorage.getItem('authToken');
    if (authToken) {
        currentUser = JSON.parse(localStorage.getItem('userData') || '{}');
        updateUIForAuthenticatedUser();
    }
}

// Update UI for authenticated user
function updateUIForAuthenticatedUser() {
    const loginLinks = document.querySelectorAll('.login-link');
    const registerLinks = document.querySelectorAll('.register-link');
    const userMenu = document.querySelector('.user-menu');
    
    loginLinks.forEach(link => link.style.display = 'none');
    registerLinks.forEach(link => link.style.display = 'none');
    if (userMenu) userMenu.style.display = 'block';
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize modals
function initializeModals() {
    const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    modalTriggerList.map(function (modalTriggerEl) {
        return new bootstrap.Modal(modalTriggerEl);
    });
}

// Setup form validation
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Handle global click events
function handleGlobalClick(event) {
    const target = event.target;
    
    // Handle dropdown toggles
    if (target.matches('[data-bs-toggle="dropdown"]')) {
        event.preventDefault();
        toggleDropdown(target);
    }
    
    // Handle modal triggers
    if (target.matches('[data-bs-toggle="modal"]')) {
        event.preventDefault();
        openModal(target.dataset.bsTarget);
    }
    
    // Handle file upload buttons
    if (target.matches('.file-upload-btn')) {
        event.preventDefault();
        triggerFileUpload(target);
    }
}

// Handle form submissions
function handleFormSubmit(event) {
    const form = event.target;
    
    if (form.classList.contains('ajax-form')) {
        event.preventDefault();
        submitFormAjax(form);
    }
}

// Handle file uploads
function handleFileUpload(event) {
    const input = event.target;
    
    if (input.type === 'file' && input.multiple) {
        handleMultipleFileUpload(input);
    } else if (input.type === 'file') {
        handleSingleFileUpload(input);
    }
}

// Setup drag and drop functionality
function setupDragAndDrop() {
    const dropZones = document.querySelectorAll('.drop-zone');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('dragleave', handleDragLeave);
        zone.addEventListener('drop', handleDrop);
    });
}

// Handle drag over
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

// Handle drag leave
function handleDragLeave(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
}

// Handle drop
function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    handleMultipleFileUpload({ files: files });
}

// Handle multiple file upload
function handleMultipleFileUpload(input) {
    const files = input.files || input;
    const maxFiles = parseInt(input.dataset.maxFiles) || 10;
    const maxSize = parseInt(input.dataset.maxSize) || 16 * 1024 * 1024; // 16MB
    
    if (files.length > maxFiles) {
        showAlert(`Maximum ${maxFiles} files allowed`, 'warning');
        return;
    }
    
    Array.from(files).forEach(file => {
        if (file.size > maxSize) {
            showAlert(`File ${file.name} is too large. Maximum size is ${formatFileSize(maxSize)}.`, 'warning');
            return;
        }
        
        if (!file.type.startsWith('image/')) {
            showAlert(`File ${file.name} is not an image.`, 'warning');
            return;
        }
    });
    
    updateFilePreview(files, input);
}

// Handle single file upload
function handleSingleFileUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        showAlert('Please select an image file.', 'warning');
        input.value = '';
        return;
    }
    
    updateFilePreview([file], input);
}

// Update file preview
function updateFilePreview(files, input) {
    const previewContainer = input.parentElement.querySelector('.file-preview') || 
                           input.closest('.upload-area').querySelector('.file-preview');
    
    if (!previewContainer) return;
    
    previewContainer.innerHTML = '';
    
    Array.from(files).forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const previewItem = createFilePreviewItem(file, e.target.result, index);
            previewContainer.appendChild(previewItem);
        };
        reader.readAsDataURL(file);
    });
}

// Create file preview item
function createFilePreviewItem(file, dataUrl, index) {
    const div = document.createElement('div');
    div.className = 'file-preview-item col-md-3 col-6 mb-3';
    div.innerHTML = `
        <div class="card">
            <img src="${dataUrl}" class="card-img-top" alt="Preview" style="height: 150px; object-fit: cover;">
            <div class="card-body p-2">
                <h6 class="card-title text-truncate" title="${file.name}">${file.name}</h6>
                <p class="card-text small text-muted">${formatFileSize(file.size)}</p>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFilePreview(this, ${index})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;
    return div;
}

// Remove file preview
function removeFilePreview(button, index) {
    const previewItem = button.closest('.file-preview-item');
    previewItem.remove();
    
    // Update file input
    const fileInput = button.closest('.upload-area').querySelector('input[type="file"]');
    if (fileInput) {
        // Create new FileList without the removed file
        const dt = new DataTransfer();
        const files = Array.from(fileInput.files);
        files.splice(index, 1);
        files.forEach(file => dt.items.add(file));
        fileInput.files = dt.files;
    }
}

// Submit form via AJAX
function submitFormAjax(form) {
    const formData = new FormData(form);
    const url = form.action || window.location.href;
    const method = form.method || 'POST';
    
    showLoading(true);
    
    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success) {
            showAlert(data.message || 'Success!', 'success');
            if (data.redirect) {
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1000);
            }
        } else {
            showAlert(data.error || 'An error occurred', 'danger');
        }
    })
    .catch(error => {
        showLoading(false);
        showAlert('Network error. Please try again.', 'danger');
        console.error('Error:', error);
    });
}

// Show loading state
function showLoading(show) {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(element => {
        element.style.display = show ? 'block' : 'none';
    });
    
    if (show) {
        document.body.style.cursor = 'wait';
    } else {
        document.body.style.cursor = 'default';
    }
}

// Show alert message
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.querySelector('.alert-container') || createAlertContainer();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto remove after duration
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, duration);
}

// Create alert container
function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alert-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Toggle dropdown
function toggleDropdown(trigger) {
    const dropdown = document.querySelector(trigger.dataset.bsTarget);
    if (dropdown) {
        const bsDropdown = new bootstrap.Dropdown(trigger);
        bsDropdown.toggle();
    }
}

// Open modal
function openModal(modalId) {
    const modal = document.querySelector(modalId);
    if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
}

// Trigger file upload
function triggerFileUpload(button) {
    const input = button.parentElement.querySelector('input[type="file"]');
    if (input) {
        input.click();
    }
}

// Load user data
function loadUserData() {
    if (currentUser) {
        // Load user's damage reports
        loadDamageReports();
    }
}

// Load damage reports
function loadDamageReports() {
    fetch('/api/reports')
        .then(response => response.json())
        .then(data => {
            damageReports = data.reports || [];
            updateReportsUI();
        })
        .catch(error => {
            console.error('Error loading reports:', error);
        });
}

// Update reports UI
function updateReportsUI() {
    const reportsContainer = document.querySelector('.reports-container');
    if (!reportsContainer) return;
    
    reportsContainer.innerHTML = '';
    
    damageReports.forEach(report => {
        const reportElement = createReportElement(report);
        reportsContainer.appendChild(reportElement);
    });
}

// Create report element
function createReportElement(report) {
    const div = document.createElement('div');
    div.className = 'col-md-6 col-lg-4 mb-3';
    div.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h6 class="card-title">${report.vehicle_type} - ${report.damage_type}</h6>
                <p class="card-text">
                    <span class="badge bg-${getSeverityColor(report.severity)}">${report.severity}</span>
                    <span class="text-muted">${formatDate(report.created_at)}</span>
                </p>
                <p class="card-text">
                    <strong>Cost:</strong> $${report.estimated_cost.toFixed(2)}
                </p>
                <a href="/damage/results/${report.id}" class="btn btn-sm btn-primary">View Details</a>
            </div>
        </div>
    `;
    return div;
}

// Get severity color
function getSeverityColor(severity) {
    const colors = {
        'Minor': 'success',
        'Moderate': 'warning',
        'Severe': 'danger',
        'Critical': 'dark'
    };
    return colors[severity] || 'secondary';
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Camera functionality
function startCamera() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                const video = document.getElementById('cameraVideo');
                if (video) {
                    video.srcObject = stream;
                    video.play();
                }
            })
            .catch(function(error) {
                console.error('Error accessing camera:', error);
                showAlert('Camera access denied or not available', 'warning');
            });
    } else {
        showAlert('Camera not supported on this device', 'warning');
    }
}

// Capture photo from camera
function capturePhoto() {
    const video = document.getElementById('cameraVideo');
    const canvas = document.getElementById('cameraCanvas');
    
    if (video && canvas) {
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob(function(blob) {
            const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
            handleSingleFileUpload({ files: [file] });
        }, 'image/jpeg', 0.8);
    }
}

// Stop camera
function stopCamera() {
    const video = document.getElementById('cameraVideo');
    if (video && video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export functions for global use
window.showAlert = showAlert;
window.formatFileSize = formatFileSize;
window.startCamera = startCamera;
window.capturePhoto = capturePhoto;
window.stopCamera = stopCamera;
