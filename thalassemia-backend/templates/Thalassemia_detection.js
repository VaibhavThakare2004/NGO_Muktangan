// Enhanced Thalassemia CBC Predictor JavaScript
class CBCValidator {
    constructor() {
        this.form = document.getElementById('cbcForm');
        this.submitBtn = document.getElementById('submitBtn');
        this.successMessage = document.getElementById('successMessage');
        
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
                required: true
            },
            rbc: {
                message: "RBC count is required",
                required: true
            },
            wbc: {
                message: "WBC count is required",
                required: true
            },
            platelet: {
                message: "Platelet count is required",
                required: true
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
                required: true
            },
            mpv: {
                message: "MPV value is required",
                required: true
            },
            pdw: {
                message: "PDW value is required",
                required: true
            },
            plcr: {
                message: "P-LCR value is required",
                required: true
            },
            pct: {
                message: "PCT value is required",
                required: true
            },
            plcc: {
                message: "P-LCC value is required",
                required: true
            },
            
            // Differential Count - Required fields
            neutrophils: {
                message: "Neutrophils percentage is required",
                required: true
            },
            eosinophils: {
                message: "Eosinophils percentage is required",
                required: true
            },
            basophils: {
                message: "Basophils percentage is required",
                required: true
            },
            lymphocytes: {
                message: "Lymphocytes percentage is required",
                required: true
            },
            monocytes: {
                message: "Monocytes percentage is required",
                required: true
            }
        };

        this.init();
    }

    init() {
        this.addEventListeners();
        this.addRealTimeValidation();
        this.addAccessibilityFeatures();
    }

    addEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
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

    async handleSubmit(e) {
        e.preventDefault();

        // Clear all previous errors
        Object.keys(this.validationRules).forEach(fieldName => {
            this.clearError(fieldName);
        });

        // Validate all fields
        if (!this.validateAllFields()) {
            this.focusFirstError();
            return;
        }

        // Show loading state
        this.setLoadingState(true);

        try {
            console.log('🔄 Form validation passed, submitting to FastAPI...');
            
            // ✅ SIMPLE SOLUTION: Let FastAPI handle everything
            // This will submit to /submit route which handles BOTH email + Google Sheets
            this.form.submit(); // This triggers normal form submission to FastAPI
            
        } catch (error) {
            console.error('❌ Submission error:', error);
            this.showError('submission', 'Failed to submit form. Please try again.');
            this.setLoadingState(false);
        }
        // Note: We don't need finally block here because page will reload after form submission
    }

    setLoadingState(isLoading) {
        if (isLoading) {
            this.submitBtn.classList.add('loading');
            this.submitBtn.disabled = true;
            this.submitBtn.innerHTML = 'Sending...';
        } else {
            this.submitBtn.classList.remove('loading');
            this.submitBtn.disabled = false;
            this.submitBtn.innerHTML = 'Submit Form';
        }
    }

    showSuccess() {
        // Hide form and show success message
        this.form.style.display = 'none';
        this.successMessage.classList.add('show');
        
        // Scroll to success message
        this.successMessage.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });

        // Reset form after delay
        setTimeout(() => {
            this.resetForm();
        }, 5000);
    }

    resetForm() {
        this.form.reset();
        this.form.style.display = 'block';
        this.successMessage.classList.remove('show');
        
        // Clear all validation states
        Object.keys(this.validationRules).forEach(fieldName => {
            this.clearError(fieldName);
        });

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
            data[key] = value;
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
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CBCValidator();
    new FormEnhancements();
    
    // Add smooth scrolling for better UX
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add loading animation
    document.body.classList.add('loaded');
    
    console.log('Enhanced Thalassemia CBC Predictor initialized successfully');
});