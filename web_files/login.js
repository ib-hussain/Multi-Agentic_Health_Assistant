document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const togglePassBtn = document.getElementById('toggle-pass');
    const passwordInput = document.getElementById('password');
    const errorDiv = document.getElementById('form-error');

    // Toggle password visibility
    togglePassBtn.addEventListener('click', function() {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            togglePassBtn.textContent = 'Hide';
        } else {
            passwordInput.type = 'password';
            togglePassBtn.textContent = 'Show';
        }
    });

    // Handle form submission
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const name = document.getElementById('name').value.trim();
        const password = passwordInput.value.trim();
        
        // Clear previous errors
        errorDiv.style.display = 'none';
        
        // Basic client-side validation
        if (!name || !password) {
            showError('Please fill in all fields');
            return;
        }
        
        // Disable button during request
        const submitBtn = document.getElementById('login-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Logging in...';
        
        // Send login request to server
        fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                password: password
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Login successful - redirect or store token
                console.log('Login successful, user ID:', data.user_id);
                window.location.href = 'chatbot.html'; // Redirect to dashboard
            } else {
                showError(data.message || 'Login failed');
            }
        })
        .catch(error => {
            showError(error.message || 'An error occurred during login');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Log In';
        });
    });
    
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
});