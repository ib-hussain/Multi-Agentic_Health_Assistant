document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const signupForm = document.getElementById('signup-form');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const formError = document.getElementById('form-error');
    const timeSlotsContainer = document.querySelector('.time-slots-container');
    const addTimeBtn = document.getElementById('add-time-slot');
    const timeAvailabilityInput = document.getElementById('time-availability');
    const togglePassBtns = document.querySelectorAll('.toggle-pass');

    // Time slots management
    let timeSlots = [null, null, null];
    let activeSlots = 1;
    let usedTimes = new Set();
    // Toggle password visibility
    togglePassBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            this.textContent = isPassword ? 'Hide' : 'Show';
        });
    });

    // Time slots functions (updateTimeOptions, addTimeSlot, updateTimeSlot, removeTimeSlot)
    // ... [keep all your existing time slot management functions unchanged] ...
    function updateTimeOptions() {
                const timeSelects = document.querySelectorAll('.time-hour');
                timeSelects.forEach(select => {
                    const currentValue = select.value;
                    const options = select.querySelectorAll('option');
                    
                    options.forEach(option => {
                        if (option.value === '') return; // Skip placeholder
                        
                        if (usedTimes.has(option.value) && option.value !== currentValue) {
                            option.disabled = true;
                            option.style.color = '#ccc';
                        } else {
                            option.disabled = false;
                            option.style.color = '';
                        }
                    });
                });
    }
    addTimeBtn.addEventListener('click', function() {
                if (activeSlots >= 3) return;
                
                activeSlots++;
                const newIndex = activeSlots - 1;
                
                const timeGroup = document.createElement('div');
                timeGroup.className = 'time-slot-group';
                timeGroup.innerHTML = `
                    <select class="time-hour" data-index="${newIndex}">
                        <option value="" disabled selected>Select hour</option>
                        <option value="06">06:00</option>
                        <option value="07">07:00</option>
                        <option value="08">08:00</option>
                        <option value="09">09:00</option>
                        <option value="10">10:00</option>
                        <option value="11">11:00</option>
                        <option value="12">12:00</option>
                        <option value="13">13:00</option>
                        <option value="14">14:00</option>
                        <option value="15">15:00</option>
                        <option value="16">16:00</option>
                        <option value="17">17:00</option>
                        <option value="18">18:00</option>
                        <option value="19">19:00</option>
                        <option value="20">20:00</option>
                        <option value="21">21:00</option>
                        <option value="22">22:00</option>
                        <option value="23">23:00</option>
                    </select>
                    <span class="time-range-indicator">20 min session</span>
                    <button type="button" class="btn-remove-time" data-index="${newIndex}">×</button>
                `;
                
                timeSlotsContainer.insertBefore(timeGroup, addTimeBtn);
                
                // Add event listeners to new selects
                timeGroup.querySelector('.time-hour').addEventListener('change', updateTimeSlot);
                timeGroup.querySelector('.btn-remove-time').addEventListener('click', removeTimeSlot);
                
                // Update available options
                updateTimeOptions();
                
                // Disable add button if max slots reached
                if (activeSlots >= 3) {
                    addTimeBtn.style.display = 'none';
                }
    });
    function updateTimeSlot(e) {
                const index = parseInt(e.target.dataset.index);
                const hour = e.target.value;
                const previousHour = timeSlots[index] ? timeSlots[index].start.split(':')[0] : null;
                
                // Remove previous hour from used times
                if (previousHour) {
                    usedTimes.delete(previousHour);
                }
                
                if (hour) {
                    // Add new hour to used times
                    usedTimes.add(hour);
                    
                    // Store in array
                    timeSlots[index] = {
                        start: `${hour}:00`,
                        end: `${hour}:20` // Fixed 20 minute duration
                    };
                } else {
                    timeSlots[index] = null;
                }
                
                // Update available options for all selects
                updateTimeOptions();
                
                // Update hidden input
                updateTimeAvailability();
    }
    // Remove time slot
    function removeTimeSlot(e) {
                const index = parseInt(e.target.dataset.index);
                const group = e.target.closest('.time-slot-group');
                const select = group.querySelector('.time-hour');
                const hour = select.value;
                
                // Remove hour from used times
                if (hour) {
                    usedTimes.delete(hour);
                }
                
                // Remove from DOM
                group.remove();
                
                // Shift remaining slots
                for (let i = index + 1; i < timeSlots.length; i++) {
                    if (timeSlots[i]) {
                        const nextGroup = document.querySelector(`.time-slot-group select[data-index="${i}"]`)?.closest('.time-slot-group');
                        if (nextGroup) {
                            nextGroup.querySelectorAll('select').forEach(select => {
                                select.dataset.index = i - 1;
                            });
                            if (nextGroup.querySelector('.btn-remove-time')) {
                                nextGroup.querySelector('.btn-remove-time').dataset.index = i - 1;
                            }
                        }
                        
                        timeSlots[i - 1] = timeSlots[i];
                        timeSlots[i] = null;
                    }
                }
                
                activeSlots--;
                addTimeBtn.style.display = 'block';
                updateTimeOptions();
                updateTimeAvailability();
    }
    // Update hidden input with time availability
    function updateTimeAvailability() {
        const validSlots = timeSlots.filter(slot => slot !== null);
        timeAvailabilityInput.value = JSON.stringify(validSlots);
    }
    // Enhanced form validation
    function validateForm() {
        // Get all form values
        const formValues = {
            name: document.getElementById('full-name').value.trim(),
            password: passwordInput.value,
            confirmPassword: confirmPasswordInput.value,
            age: document.getElementById('age').value,
            gender: document.getElementById('gender').value,
            height: document.getElementById('height').value,
            weight: document.getElementById('weight').value,
            fitnessGoal: document.getElementById('fitness-goal').value.trim(),
            hasTimeSlot: timeSlots.some(slot => slot !== null)
        };

        // Clear previous errors
        formError.style.display = 'none';
        formError.textContent = '';
        formError.innerHTML = ''; // Clear any HTML content

        // Validate each field
        const errors = [];

        // Required fields validation
        if (!formValues.name) errors.push('Full name is required');
        if (!formValues.password) errors.push('Password is required');
        if (!formValues.age) errors.push('Age is required');
        if (!formValues.gender) errors.push('Gender is required');
        if (!formValues.height) errors.push('Height is required');
        if (!formValues.weight) errors.push('Weight is required');
        if (!formValues.hasTimeSlot) errors.push('At least one workout time is required');

        // Numeric validation
        if (formValues.age && isNaN(formValues.age)) errors.push('Age must be a valid number');
        if (formValues.height && isNaN(formValues.height)) errors.push('Height must be a valid number');
        if (formValues.weight && isNaN(formValues.weight)) errors.push('Weight must be a valid number');

        // Password validation
        if (formValues.password) {
            if (formValues.password.length < 4 || formValues.password.length > 10) {
                errors.push('Password must be between 4 and 10 characters');
            }
            if (!/[A-Z]/.test(formValues.password)) {
                errors.push('Password must contain at least one uppercase letter');
            }
            if (!/[0-9]/.test(formValues.password)) {
                errors.push('Password must contain at least one number');
            }
        }

        // Password match validation
        if (formValues.password && formValues.password !== formValues.confirmPassword) {
            errors.push('Passwords do not match');
        }

        // Display errors if any
        if (errors.length > 0) {
            const errorList = errors.map(error => `<li>${error}</li>`).join('');
            formError.innerHTML = `<ul style="margin:0;padding-left:20px;">${errorList}</ul>`;
            formError.style.display = 'block';
            
            // Scroll to error message
            formError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return false;
        }

        return true;
    }
    // Enhanced form submission
    signupForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate form before submission
        if (!validateForm()) return;
        
        // Prepare form data
        const formData = {
            name: document.getElementById('full-name').value.trim(),
            password: passwordInput.value,
            age: parseFloat(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            height: parseFloat(document.getElementById('height').value),
            weight: parseFloat(document.getElementById('weight').value),
            fitness_goal: document.getElementById('fitness-goal').value.trim(),
            diet_pref: document.getElementById('diet-pref').value,
            time_availability: JSON.parse(timeAvailabilityInput.value),
            goal_deadline: parseInt(document.getElementById('goal-deadline').value),
            mental_health: document.getElementById('mental-health').value.trim() || null,
            medical_conditions: document.getElementById('medical-conditions').value.trim() || null
        };
        
        // Disable button during submission
        const submitBtn = signupForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating account...';
        
        try {
            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                // Handle server-side validation errors
                if (data.errors) {
                    const errorList = data.errors.map(error => `<li>${error}</li>`).join('');
                    formError.innerHTML = `<ul style="margin:0;padding-left:20px;">${errorList}</ul>`;
                    formError.style.display = 'block';
                    formError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    throw new Error(data.message || 'Registration failed');
                }
                return;
            }
            
            if (data.success) {
                // Registration successful - redirect to login with success message
                sessionStorage.setItem('registrationSuccess', 'true');
                window.location.href = 'login.html';
            }
            
        } catch (error) {
            console.error('Signup error:', error);
            formError.textContent = error.message || 'An error occurred during registration. Please try again.';
            formError.style.display = 'block';
            formError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });

    // Initialize first time slot event listeners
    document.querySelector('.time-hour')?.addEventListener('change', updateTimeSlot);
});