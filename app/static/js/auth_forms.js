// /ai_rag_story_app/app/static/js/auth_forms.js

/**
 * auth_forms.js
 * --------------
 * Handles client-side logic for user registration and login forms.
 * Uses showToast() for notifications instead of alert().
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {

    const API_BASE_URL = "/api/v1"; 

    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const loginErrorDisplay = document.getElementById('login-error-message'); 
    const registerErrorDisplay = document.getElementById('register-error-message'); 

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault(); 

            if (loginErrorDisplay) {
                loginErrorDisplay.textContent = ''; 
                loginErrorDisplay.style.display = 'none'; 
            }
            const loginButton = loginForm.querySelector('button[type="submit"]');
            const originalButtonText = loginButton ? loginButton.innerHTML : "Login"; 
            if (loginButton) {
                loginButton.disabled = true;
                loginButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Logging in...`;
            }

            const formData = new FormData(loginForm);
            
            // --- FIX: Use the form's action attribute as the single source of truth for the URL ---
            const loginApiUrl = loginForm.action;
            // --- END FIX ---

            try {
                const response = await fetch(loginApiUrl, {
                    method: 'POST',
                    body: new URLSearchParams(formData), 
                    credentials: 'include' 
                });

                if (response.ok) {
                    console.log("Login successful.");
                    
                    // Check if there's a next step parameter for redirect after login
                    const urlParams = new URLSearchParams(window.location.search);
                    const nextStep = urlParams.get('next');
                    
                    if (nextStep === 'step2') {
                        window.location.href = '/ui/?step=2';
                    } else if (nextStep === 'step3') {
                        window.location.href = '/ui/?step=3';
                    } else {
                        window.location.href = '/ui/stories';
                    }
                } else {
                    const errorData = await response.json().catch(() => ({ detail: `Login failed (Status: ${response.status})` }));
                    let errorMessage = errorData?.detail || `Login failed. Please check your credentials.`;
                    
                    if (errorData?.detail && errorData.detail.toLowerCase().includes("inactive user")) {
                        errorMessage = "Your account is not yet active. In test mode, accounts should be activated immediately. Please try again or contact support.";
                    }
                    console.error("Login failed:", errorMessage);
                    if (loginErrorDisplay) { 
                        loginErrorDisplay.textContent = errorMessage;
                        loginErrorDisplay.style.display = 'block';
                    } else {
                        showToast(errorMessage, "error"); 
                    }
                }
            } catch (error) {
                console.error('Login request error:', error);
                const networkErrorMsg = 'An error occurred during login. Please check your connection and try again.';
                if (loginErrorDisplay) {
                    loginErrorDisplay.textContent = networkErrorMsg;
                    loginErrorDisplay.style.display = 'block';
                } else {
                    showToast(networkErrorMsg, "error");
                }
            } finally {
                 if (loginButton) {
                    loginButton.disabled = false;
                    loginButton.innerHTML = originalButtonText; 
                 }
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            if (registerErrorDisplay) {
                registerErrorDisplay.textContent = '';
                registerErrorDisplay.style.display = 'none'; 
            }
            const registerButton = registerForm.querySelector('button[type="submit"]');
            const originalButtonText = registerButton ? registerButton.innerHTML : "Register";
            if (registerButton) {
                registerButton.disabled = true;
                registerButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registering...`;
            }

            const formData = new FormData(registerForm);
            const data = Object.fromEntries(formData.entries());

            // Validate password match
            if (data.password !== data.password_confirm) {
                const errorMsg = "Passwords do not match.";
                if (registerErrorDisplay) { 
                    registerErrorDisplay.textContent = errorMsg;
                    registerErrorDisplay.style.display = 'block';
                } else {
                    showToast(errorMsg, "error");
                }
                if (registerButton) {
                    registerButton.disabled = false;
                    registerButton.innerHTML = originalButtonText;
                }
                return;
            }

            // Validate Terms of Service acceptance
            if (!data.terms_accepted) {
                const errorMsg = "You must agree to the Terms of Service to create an account.";
                if (registerErrorDisplay) { 
                    registerErrorDisplay.textContent = errorMsg;
                    registerErrorDisplay.style.display = 'block';
                } else {
                    showToast(errorMsg, "error");
                }
                if (registerButton) {
                    registerButton.disabled = false;
                    registerButton.innerHTML = originalButtonText;
                }
                return;
            }

            const registrationData = {
                username: data.username,
                email: data.email || null, 
                display_name: data.display_name || null,
                password: data.password,
                terms_accepted: true // Always true at this point due to validation above
            };

            const registerApiUrl = `${API_BASE_URL}/auth/register`; 

            try {
                const response = await fetch(registerApiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', },
                    body: JSON.stringify(registrationData),
                    credentials: 'include'
                });

                if (response.status === 201) { 
                    console.log("Registration successful, account active immediately.");
                    
                    // Track registration with Terms of Service acceptance
                    if (window.trackAuthEvent) {
                        window.trackAuthEvent('registration_completed', 'with_terms_acceptance');
                    }
                    
                    showToast("Registration successful! Your account is ready to use. You can login now and start creating stories!", "success", 8000);
                    
                    setTimeout(() => {
                        // Check if there's a next step parameter for redirect after registration
                        const urlParams = new URLSearchParams(window.location.search);
                        const nextStep = urlParams.get('next');
                        
                        if (nextStep === 'step2') {
                            window.location.href = '/ui/login?next=step2';
                        } else if (nextStep === 'step3') {
                            window.location.href = '/ui/login?next=step3';
                        } else {
                            window.location.href = '/ui/login';
                        }
                    }, 2000);
                } else {
                    const errorData = await response.json().catch(() => ({ detail: `Registration failed (Status: ${response.status})` }));
                    const errorMessage = errorData?.detail || `Registration failed. Please try again.`;
                    console.error("Registration failed:", errorMessage);
                    if (registerErrorDisplay) { 
                        registerErrorDisplay.textContent = errorMessage;
                        registerErrorDisplay.style.display = 'block';
                    } else {
                        showToast(errorMessage, "error");
                    }
                }
            } catch (error) {
                console.error('Registration request error:', error);
                const networkErrorMsg = 'An error occurred during registration. Please check connection.';
                 if (registerErrorDisplay) {
                    registerErrorDisplay.textContent = networkErrorMsg;
                    registerErrorDisplay.style.display = 'block';
                } else {
                    showToast(networkErrorMsg, "error");
                }
            } finally {
                 if (registerButton) {
                    registerButton.disabled = false;
                    registerButton.innerHTML = originalButtonText;
                 }
            }
        });
    }
    console.log("Auth forms JS initialized with toast notifications and inline error display preference.");
});