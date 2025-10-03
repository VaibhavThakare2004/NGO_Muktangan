// Enhanced Thalassemia CBC Predictor JavaScript - Google Cloud Optimized
class CBCValidator {
    constructor() {
        this.form = document.getElementById('cbcForm');
        this.submitBtn = document.getElementById('submitBtn');
        this.successMessage = document.getElementById('successMessage');
        
        // ✅ UPDATE THIS LINE with your real deployed URL
        this.API_URL = 'https://speech-test-471607.uc.r.appspot.com/submit';
        
        this.validationRules = {
            // Personal Information - Required fields
            name: {
                pattern: /^[A-Za-z\s]{2,50}$/,
                message: "Name must contain 2-50 letters and spaces only",
                required: true
            },
            whatsapp: {
                pattern: /^\d{10}$/,
                message: "WhatsApp number must be exactly 10 digits",
                required: true
            },
            email: {
                pattern: /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i,
                message: "Please enter a valid email address",
                required: true
            },
            age: {
                min: 1,
                max: 120,
                message: "Age must be between 1 and 120 years",
                required: true
            },
            sex: {
                message: "Please select sex",
                required: true
            },
            address: {
                minLength: 10,
                message: "Address must be at least 10 characters long",
                required: true
            },
            caste: {
                minLength: 2,
                message: "Caste must be at least 2 characters long",
                required: true
            },
            religion: {
                minLength: 2,
                message: "Religion must be at least 2 characters long",
                required: true
            },
            
            // Medical History - Optional fields
            bloodWithin3Months: { required: false },
            bloodMoreThan2Times: { required: false },
            fatigue: { required: false },
            breathless: { required: false },
            illFrequently: { required: false },
            familyHistory: { required: false },
            
            // CBC Parameters - Required fields (no min/max limits)
            hb: {
                message: "Hemoglobin value is required",
                required: true
            },
            hct: {
                message: "Hematocrit value is required",
                required: false
            },
            rbc: {
                message: "RBC count is required",
                required: true
            },
            wbc: {
                message: "WBC count is required",
                required: false
            },
            platelet: {
                message: "Platelet count is required",
                required: false
            },
            mcv: {
                message: "MCV value is required",
                required: true
            },
            mch: {
                message: "MCH value is required",
                required: true
            },
            mchc: {
                message: "MCHC value is required",
                required: true
            },
            rdwcv: {
                message: "RDW-CV value is required",
                required: true
            },
            rdwsd: {
                message: "RDW-SD value is required",
                required: false
            },
            mpv: {
                message: "MPV value is required",
                required: false
            },
            pdw: {
                message: "PDW value is required",
                required: false
            },
            plcr: {
                message: "P-LCR value is required",
                required: false
            },
            pct: {
                message: "PCT value is required",
                required: false
            },
            plcc: {
                message: "P-LCC value is required",
                required: false
            },
            
            // Differential Count - Required fields
            neutrophils: {
                message: "Neutrophils percentage is required",
                required: false
            },
            eosinophils: {
                message: "Eosinophils percentage is required",
                required: false
            },
            basophils: {
                message: "Basophils percentage is required",
                required: false
            },
            lymphocytes: {
                message: "Lymphocytes percentage is required",
                required: false
            },
            monocytes: {
                message: "Monocytes percentage is required",
                required: false
            }
        };

        this.init();
    }

    init() {
        this.ensureFormVisibility();
        this.addEventListeners();
        this.addRealTimeValidation();
        this.addAccessibilityFeatures();
    }

    ensureFormVisibility() {
        const formContainer = document.querySelector('.form-container');
        if (formContainer) {
            formContainer.style.display = 'block';
            formContainer.style.opacity = '1';
        }
    }

    addEventListeners() {
        console.log('🔄 Adding event listeners...');
        console.log('Submit button:', this.submitBtn);
        
        // Button click handler (primary method)
        if (this.submitBtn) {
            this.submitBtn.addEventListener('click', (e) => {
                console.log('🔄 Button click handler triggered');
                e.preventDefault();
                e.stopPropagation();
                this.handleSubmit(e);
            });
            console.log('✅ Button click listener added');
        } else {
            console.error('❌ Submit button not found!');
        }
        
        // Form submit handler (backup prevention)
        this.form.addEventListener('submit', (e) => {
            console.log('🛡️ Form submit prevention triggered');
            e.preventDefault();
            e.stopPropagation();
            return false;
        }, true);
        
        // Add input event listeners for real-time validation
        Object.keys(this.validationRules).forEach(fieldName => {
            const field = this.form.elements[fieldName];
            if (field) {
                field.addEventListener('blur', () => this.validateField(fieldName));
                field.addEventListener('input', () => this.clearError(fieldName));
            }
        });
    }

    addRealTimeValidation() {
        // Add visual feedback for valid inputs
        const inputs = this.form.querySelectorAll('input[required], select[required], textarea[required]');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                if (input.value.trim()) {
                    input.classList.add('has-value');
                } else {
                    input.classList.remove('has-value');
                }
            });
        });
    }

    addAccessibilityFeatures() {
        // Add ARIA labels and descriptions
        Object.keys(this.validationRules).forEach(fieldName => {
            const field = this.form.elements[fieldName];
            const errorElement = document.getElementById(`${fieldName}Error`);
            
            if (field && errorElement) {
                field.setAttribute('aria-describedby', `${fieldName}Error`);
                errorElement.setAttribute('role', 'alert');
                errorElement.setAttribute('aria-live', 'polite');
            }
        });
    }

    validateField(fieldName) {
        const field = this.form.elements[fieldName];
        const rule = this.validationRules[fieldName];
        
        if (!field || !rule) return true;
        
        const value = field.value.trim();

        // Check if field is required
        if (rule.required && !value) {
            this.showError(fieldName, `${this.getFieldLabel(fieldName)} is required`);
            return false;
        }

        // If field is not required and empty, it's valid
        if (!rule.required && !value) {
            this.clearError(fieldName);
            return true;
        }

        // Validate pattern
        if (rule.pattern && !rule.pattern.test(value)) {
            this.showError(fieldName, rule.message);
            return false;
        }

        // Validate numeric ranges (only if min/max are defined)
        if (rule.min !== undefined || rule.max !== undefined) {
            const numValue = parseFloat(value);
            if (isNaN(numValue)) {
                this.showError(fieldName, rule.message);
                return false;
            }
            if (rule.min !== undefined && numValue < rule.min) {
                this.showError(fieldName, rule.message);
                return false;
            }
            if (rule.max !== undefined && numValue > rule.max) {
                this.showError(fieldName, rule.message);
                return false;
            }
        }

        // Validate minimum length
        if (rule.minLength && value.length < rule.minLength) {
            this.showError(fieldName, rule.message);
            return false;
        }

        // For numeric CBC fields, just check if it's a valid number
        if (['hb', 'hct', 'rbc', 'wbc', 'platelet', 'mcv', 'mch', 'mchc', 'rdwcv', 'rdwsd', 'mpv', 'pdw', 'plcr', 'pct', 'plcc', 'neutrophils', 'eosinophils', 'basophils', 'lymphocytes', 'monocytes'].includes(fieldName)) {
            const numValue = parseFloat(value);
            if (value && isNaN(numValue)) {
                this.showError(fieldName, 'Please enter a valid number');
                return false;
            }
        }

        this.clearError(fieldName);
        return true;
    }

    validateAllFields() {
        let isValid = true;
        Object.keys(this.validationRules).forEach(fieldName => {
            if (!this.validateField(fieldName)) {
                isValid = false;
            }
        });
        return isValid;
    }

    showError(fieldName, message) {
        const errorElement = document.getElementById(`${fieldName}Error`);
        const field = this.form.elements[fieldName];
        
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('show');
        }
        
        if (field) {
            field.classList.add('error');
            field.setAttribute('aria-invalid', 'true');
        }
    }

    clearError(fieldName) {
        const errorElement = document.getElementById(`${fieldName}Error`);
        const field = this.form.elements[fieldName];
        
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.classList.remove('show');
        }
        
        if (field) {
            field.classList.remove('error');
            field.setAttribute('aria-invalid', 'false');
        }
    }

    getFieldLabel(fieldName) {
        const field = this.form.elements[fieldName];
        const label = this.form.querySelector(`label[for="${fieldName}"]`);
        return label ? label.textContent.replace('*', '').trim() : fieldName;
    }

    // ✅ UPDATED: API-based form submission
    // ✅ UPDATED: Fixed loading state and submission flow
async handleSubmit(e) {
    console.log('🚀 handleSubmit called');
    e.preventDefault();

    // Clear all previous errors
    Object.keys(this.validationRules).forEach(fieldName => {
        this.clearError(fieldName);
    });

    // Validate all fields
    console.log('🔍 Validating all fields...');
    if (!this.validateAllFields()) {
        console.log('❌ Validation failed');
        this.focusFirstError();
        return;
    }
    console.log('✅ All fields validated successfully');

    // ✅ FIX: Show loading state FIRST
    console.log('🔄 Setting loading state...');
    this.setLoadingState(true);
    
    // ✅ FIX: Add a small delay to ensure loading animation is visible
    await new Promise(resolve => setTimeout(resolve, 100));

    try {
        console.log('🔄 Form validation passed, submitting to Google Cloud API...');
        
        // Get form data
        const formData = this.getFormData();
        
        // Send to Google Cloud API
        const response = await fetch(this.API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        // ✅ CHECK if response is HTML or JSON
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('text/html')) {
            // Handle HTML response (show thank you page)
            const htmlContent = await response.text();
            this.showThankYouPage(htmlContent);
        } else {
            // Handle JSON response (show success with data)
            const result = await response.json();
            this.showSuccess(result);
        }
        
    } catch (error) {
        console.error('❌ API Submission error:', error);
        const errorMessage = this.handleAPIError(error);
        this.showError('submission', errorMessage);
        this.setLoadingState(false);
    }
}
/// ✅ UPDATED: Method to show thank you page WITHOUT spinners
showThankYouPage(htmlContent) {
    // Display the backend's thankyou.html as a standalone page
    this.setLoadingState(false);
    try {
        document.open('text/html', 'replace');
        document.write(htmlContent);
        document.close();
        console.log('✅ Replaced document with thankyou page');
    } catch (e) {
        console.error('❌ Failed to replace document, falling back to inline render', e);
        // Fallback: inline render below header
        this.form.style.display = 'none';
        const container = document.createElement('div');
        container.innerHTML = htmlContent;
        this.form.parentNode.insertBefore(container, this.form.nextSibling);
    }
    localStorage.removeItem('cbcFormData');
}

showBasicSuccess() {
    this.setLoadingState(false);
    this.form.style.display = 'none';
    
    this.successMessage.innerHTML = `
        <div class="success-content">
            <div class="success-icon">✅</div>
            <h2>Submission Successful!</h2>
            <p>Your CBC parameters have been analyzed successfully.</p>
            <button onclick="location.reload()" class="btn-primary" style="margin-top: 20px;">
                Submit Another Test
            </button>
        </div>
    `;
    this.successMessage.classList.add('show');
}
setLoadingState(isLoading) {
    console.log('🔄 Setting loading state:', isLoading);
    if (isLoading) {
        this.submitBtn.classList.add('loading');
        this.submitBtn.disabled = true;
        // Use inline spinner icon + text only (no absolute overlay)
        this.submitBtn.innerHTML = `
            <i class=\"fas fa-spinner fa-spin\"></i>
            <span class=\"btn-text\">Sending...</span>
        `;
    } else {
        this.submitBtn.classList.remove('loading');
        this.submitBtn.disabled = false;
        this.submitBtn.innerHTML = `
            <i class="fas fa-flask"></i>
            <span class="btn-text">Analyze CBC Parameters</span>
            <div class="loading-spinner"></div>
        `;
    }
}

    // ✅ UPDATED: Success handler with API response data
    showSuccess(apiResponse) {
        // Hide form and show success message
        this.form.style.display = 'none';
        
        // Update success message with API response data
        let successHTML = `
            <div class="success-content">
                <div class="success-icon">✅</div>
                <h2>Submission Successful!</h2>
                <p class="success-message">Thank you for your submission. Here are your results:</p>
        `;
        
        // Add prediction result if available
        if (apiResponse.prediction) {
            const predictionClass = apiResponse.prediction.includes('Likely') ? 'prediction-warning' : 'prediction-success';
            successHTML += `
                <div class="prediction-result ${predictionClass}">
                    <h3>Prediction Result:</h3>
                    <p class="prediction-value"><strong>${apiResponse.prediction}</strong></p>
                </div>
            `;
        }
        
        // Add probability if available
        if (apiResponse.probability) {
            successHTML += `
                <div class="probability">
                    <h3>Analysis Details:</h3>
                    <p>${apiResponse.probability}</p>
                </div>
            `;
        }
        
        // Add status indicators
        successHTML += `
                <div class="status-indicators">
                    <div class="status-item ${apiResponse.email_sent ? 'status-success' : 'status-warning'}">
                        <span>📧 Email: ${apiResponse.email_sent ? 'Sent' : 'Failed'}</span>
                    </div>
                    <div class="status-item ${apiResponse.sheets_saved ? 'status-success' : 'status-warning'}">
                        <span>📊 Data Saved: ${apiResponse.sheets_saved ? 'Success' : 'Failed'}</span>
                    </div>
                </div>
        `;
        
        // Add next steps
        successHTML += `
                <div class="next-steps">
                    <h3>Next Steps:</h3>
                    <ul>
                        <li>📧 Check your email for detailed results</li>
                        <li>📊 Your data has been recorded in our system</li>
                        <li>👨‍⚕️ Consult with a healthcare professional for detailed analysis</li>
                        <li>📞 Contact us if you have any questions</li>
                    </ul>
                </div>
                
                <button onclick="location.reload()" class="btn-primary" style="margin-top: 20px;">
                    Submit Another Test
                </button>
            </div>
        `;
        
        this.successMessage.innerHTML = successHTML;
        this.successMessage.classList.add('show');
        
        // Scroll to success message
        this.successMessage.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });

        // Clear saved form data
        localStorage.removeItem('cbcFormData');
        
        console.log('✅ Form submitted successfully:', apiResponse);
    }

    resetForm() {
        this.form.reset();
        this.form.style.display = 'block';
        this.successMessage.classList.remove('show');
        
        // Clear all validation states
        Object.keys(this.validationRules).forEach(fieldName => {
            this.clearError(fieldName);
        });

        // Clear progress indicator
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = '0%';
        }

        // Scroll back to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    focusFirstError() {
        const firstError = this.form.querySelector('.error');
        if (firstError) {
            firstError.focus();
            firstError.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }
    }

    // Public method to get form data
    getFormData() {
        const formData = new FormData(this.form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            // Convert numeric fields to numbers
            if (['hb', 'hct', 'rbc', 'wbc', 'platelet', 'mcv', 'mch', 'mchc', 'rdwcv', 'rdwsd', 'mpv', 'pdw', 'plcr', 'pct', 'plcc', 'neutrophils', 'eosinophils', 'basophils', 'lymphocytes', 'monocytes', 'age'].includes(key)) {
                data[key] = value ? parseFloat(value) : null;
            } else {
                data[key] = value;
            }
        }
        
        return data;
    }
}

// Enhanced form interactions
class FormEnhancements {
    constructor() {
        this.init();
    }

    init() {
        this.addProgressIndicator();
        this.addKeyboardNavigation();
        this.addAutoSave();
    }

    addProgressIndicator() {
        const inputs = document.querySelectorAll('input[required], select[required], textarea[required]');
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        progressBar.innerHTML = '<div class="progress-fill"></div>';
        
        const formHeader = document.querySelector('.form-header');
        if (formHeader) {
            formHeader.appendChild(progressBar);
        }

        inputs.forEach(input => {
            input.addEventListener('input', () => {
                this.updateProgress();
            });
        });
    }

    updateProgress() {
        const inputs = document.querySelectorAll('input[required], select[required], textarea[required]');
        const filledInputs = Array.from(inputs).filter(input => input.value.trim());
        const progress = (filledInputs.length / inputs.length) * 100;
        
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }
    }

    addKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT')) {
                const formElements = Array.from(document.querySelectorAll('input, select, textarea'));
                const currentIndex = formElements.indexOf(e.target);
                const nextElement = formElements[currentIndex + 1];
                
                if (nextElement) {
                    nextElement.focus();
                    e.preventDefault();
                }
            }
        });
    }

    addAutoSave() {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                this.saveToLocalStorage();
            });
        });

        // Load saved data on page load
        this.loadFromLocalStorage();
    }

    saveToLocalStorage() {
        const formData = {};
        const inputs = document.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            formData[input.name] = input.value;
        });

        localStorage.setItem('cbcFormData', JSON.stringify(formData));
    }

    loadFromLocalStorage() {
        const savedData = localStorage.getItem('cbcFormData');
        if (savedData) {
            const formData = JSON.parse(savedData);
            
            Object.entries(formData).forEach(([name, value]) => {
                const input = document.querySelector(`input[name="${name}"], select[name="${name}"], textarea[name="${name}"]`);
                if (input && value) {
                    input.value = value;
                }
            });
            
            // Update progress after loading saved data
            this.updateProgress();
        }
    }
}


// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        console.log('🔄 Initializing CBC Validator...');
        const validator = new CBCValidator();
        
        // Double-check that form exists and event listener is attached
        const form = document.getElementById('cbcForm');
        if (!form) {
            console.error('❌ Form not found!');
            return;
        }
        
        console.log('✅ Form found, validator initialized');
        
        // Add additional form submit prevention as backup
        form.addEventListener('submit', (e) => {
            console.log('🛡️ Backup form submit handler triggered');
            e.preventDefault();
            e.stopPropagation();
        }, true);
        
        new FormEnhancements();
        
        // Add smooth scrolling for better UX
        document.documentElement.style.scrollBehavior = 'smooth';
        
        // Add loading animation
        document.body.classList.add('loaded');
        
        console.log('✅ Enhanced Thalassemia CBC Predictor initialized successfully');
    } catch (error) {
        console.error('❌ Initialization error:', error);
    }
    console.log('🚀 Ready for Google Cloud API integration');
});

// ✅ UPDATED: Better CSS for loading states
const additionalStyles = `
/* ✅ REMOVED: All spinner CSS */

.success-content {
    text-align: center;
    padding: 20px;
}

.success-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.prediction-result {
    padding: 15px;
    border-radius: 8px;
    margin: 15px 0;
}

.prediction-success {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
}

.prediction-warning {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
}

.status-indicators {
    display: flex;
    justify-content: center;
    gap: 15px;
    margin: 15px 0;
}

.status-item {
    padding: 8px 15px;
    border-radius: 20px;
    font-size: 0.9rem;
}

.status-success {
    background-color: #d4edda;
    color: #155724;
}

.status-warning {
    background-color: #f8d7da;
    color: #721c24;
}

.next-steps {
    text-align: left;
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin: 20px 0;
}

.next-steps ul {
    margin: 10px 0;
    padding-left: 20px;
}

.next-steps li {
    margin-bottom: 8px;
}

/* Error message styling */
.error-message {
    color: #dc3545;
    font-size: 0.875rem;
    margin-top: 0.25rem;
    display: none;
}

.error-message.show {
    display: block;
}

input.error, select.error, textarea.error {
    border-color: #dc3545 !important;
}
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);