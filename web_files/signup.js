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

            // Time slots array (max 3)
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

            // Update available options for time selects
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

            // Add time slot
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

            // Update time slot
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

            // Form validation
            function validateForm() {
                const password = passwordInput.value;
                const confirmPassword = confirmPasswordInput.value;
                
                // Clear previous errors
                formError.style.display = 'none';
                formError.textContent = '';
                
                // Password validation
                if (password.length < 4 || password.length > 10) {
                    showError('Password must be between 4 and 10 characters.');
                    return false;
                }
                
                if (password !== confirmPassword) {
                    showError('Passwords do not match.');
                    return false;
                }
                
                // Time slots validation (at least one required)
                const hasTimeSlot = timeSlots.some(slot => slot !== null);
                if (!hasTimeSlot) {
                    showError('Please select at least one preferred workout time.');
                    return false;
                }
                
                return true;
            }

            // Show error message
            function showError(message) {
                formError.textContent = message;
                formError.style.display = 'block';
                formError.setAttribute('aria-live', 'assertive');
                
                // Scroll to error
                formError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }

            // Form submission
            signupForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
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
                    medical_conditions: document.getElementById('medical-conditions').value.trim() || null,
                    terms: document.getElementById('terms').checked
                };
                
                // Disable button during submission
                const submitBtn = signupForm.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                submitBtn.disabled = true;
                submitBtn.textContent = 'Creating account...';
                
                try {
                    // Simulate API response for demonstration
                    await simulateSignup(formData);
                    
                } catch (error) {
                    console.error('Signup error:', error);
                    showError(error.message || 'An error occurred during registration. Please try again.');
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            });

            // Development-only simulation
            async function simulateSignup(formData) {
                console.log('Simulated form submission:', formData);
                await new Promise(resolve => setTimeout(resolve, 1500));
                
                // Format time availability for display
                const timeSlots = formData.time_availability.map(slot => 
                    `${slot.start} - ${slot.end}`).join(', ');
                
                alert(`Account would be created with:\n\n` +
                      `Name: ${formData.name}\n` +
                      `Age: ${formData.age}\n` +
                      `Gender: ${formData.gender}\n` +
                      `Height: ${formData.height}m\n` +
                      `Weight: ${formData.weight}kg\n` +
                      `Fitness Goal: ${formData.fitness_goal}\n` +
                      `Diet Preference: ${formData.diet_pref}\n` +
                      `Workout Times: ${timeSlots}\n` +
                      `Goal Deadline: ${formData.goal_deadline} days`);
                
                // Simulate successful registration
                console.log('Registration successful!');
            }

            // Initialize first time slot event listeners
            document.querySelector('.time-hour').addEventListener('change', updateTimeSlot);
        });
    