// login.js - Enhanced version
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const loginForm = document.getElementById('login-form');
    const nameInput = document.getElementById('name');
    const passwordInput = document.getElementById('password');
    const togglePassBtn = document.getElementById('toggle-pass');
    const formError = document.getElementById('form-error');
    const loginBtn = document.getElementById('login-btn');

    // Constants
    const LOGIN_ENDPOINT = '/api/login'; // Will be your Flask endpoint
    const MIN_PASSWORD_LENGTH = 4;

    // Toggle password visibility
    if (togglePassBtn && passwordInput) {
        togglePassBtn.addEventListener('click', function() {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            togglePassBtn.textContent = isPassword ? 'Hide' : 'Show';
            togglePassBtn.setAttribute('aria-label', 
                isPassword ? 'Hide password' : 'Show password');
        });
    }

    // Load saved name from localStorage if available
    const savedName = localStorage.getItem('vha_name');
    if (savedName && nameInput) {
        nameInput.value = savedName;
    }

    // Form validation
    function validateForm() {
        const name = nameInput.value.trim();
        const password = passwordInput.value.trim();
        let isValid = true;

        // Clear previous errors
        formError.style.display = 'none';
        formError.textContent = '';

        // Validate name
        if (!name) {
            showError('Please enter your full name.');
            isValid = false;
        } else if (name.length < 2) {
            showError('Name must be at least 2 characters.');
            isValid = false;
        }

        // Validate password
        if (!password) {
            showError('Please enter your password.');
            isValid = false;
        } else if (password.length < MIN_PASSWORD_LENGTH) {
            showError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters.`);
            isValid = false;
        }

        return isValid;
    }

    // Show error message
    function showError(message) {
        formError.textContent = message;
        formError.style.display = 'block';
        formError.setAttribute('aria-live', 'assertive');
    }

    // Handle form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!validateForm()) return;

            const name = nameInput.value.trim();
            const password = passwordInput.value.trim();

            // Save name to localStorage
            localStorage.setItem('vha_name', name);

            // Disable button during submission
            const originalText = loginBtn.textContent;
            loginBtn.disabled = true;
            loginBtn.textContent = 'Signing in...';

            try {
                // In development, you can simulate API response
                // Remove this in production
                if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                    await simulateLogin(name, password);
                    return;
                }

                const response = await fetch(LOGIN_ENDPOINT, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        name: name,
                        password: password
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.message || 'Login failed');
                }

                // Successful login - redirect to chatbot
                window.location.href = 'chatbot.html';
                
            } catch (error) {
                console.error('Login error:', error);
                showError(error.message || 'An error occurred during login. Please try again.');
            } finally {
                loginBtn.disabled = false;
                loginBtn.textContent = originalText;
            }
        });
    }

    // Development-only simulation
    async function simulateLogin(name, password) {
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Simple validation for demo purposes
        if (password.length < 6) {
            throw new Error('Password must be at least 6 characters');
        }
        
        // Simulate successful login
        console.log(`Simulated login for: ${name}`);
        window.location.href = 'home.html';
    }
});
