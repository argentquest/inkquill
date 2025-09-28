/**
 * Interview Component - Handles the welcome interview modal
 * Manages question flow, user responses, and submission
 */

class InterviewComponent {
    constructor(interviewId = 'new_user_onboarding') {
        this.interviewId = interviewId;
        this.questions = [];
        this.responses = {};
        this.currentQuestionIndex = 0;
        this.isLoading = false;
        this.isSubmitting = false;
        this.metadata = {
            start_time: null,
            end_time: null,
            user_agent: navigator.userAgent
        };
        
        // Bind methods
        this.loadQuestions = this.loadQuestions.bind(this);
        this.nextQuestion = this.nextQuestion.bind(this);
        this.previousQuestion = this.previousQuestion.bind(this);
        this.skipQuestion = this.skipQuestion.bind(this);
        this.submitInterview = this.submitInterview.bind(this);
    }

    /**
     * Initialize the interview component
     */
    async init() {
        console.log('Interview Component: Initializing...');
        this.metadata.start_time = new Date().toISOString();
        await this.loadQuestions();
    }

    /**
     * Load interview questions from API
     */
    async loadQuestions() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingState();

        try {
            console.log(`Interview Component: Loading questions for ID: ${this.interviewId}`);
            const response = await fetch(`/api/v1/interview/questions/${this.interviewId}`);
            
            console.log(`Interview Component: API response status: ${response.status}`);
            console.log(`Interview Component: API response headers:`, response.headers);
            
            if (!response.ok) {
                // Try to get error details from response body
                let errorDetails = '';
                try {
                    const errorData = await response.json();
                    errorDetails = errorData.detail || errorData.message || JSON.stringify(errorData);
                    console.log('Interview Component: Error response body:', errorData);
                } catch (e) {
                    console.log('Interview Component: Could not parse error response as JSON');
                    try {
                        errorDetails = await response.text();
                        console.log('Interview Component: Error response text:', errorDetails);
                    } catch (e2) {
                        console.log('Interview Component: Could not read error response text');
                    }
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}. Details: ${errorDetails}`);
            }

            const data = await response.json();
            console.log('Interview Component: Raw API response data:', data);
            
            this.questions = data.questions || [];
            console.log(`Interview Component: Parsed questions array:`, this.questions);
            
            if (this.questions.length === 0) {
                throw new Error('No questions found in interview');
            }

            console.log(`Interview Component: Successfully loaded ${this.questions.length} questions`);
            console.log(`Interview Component: First question:`, this.questions[0]);

            // Initialize responses object
            this.initializeResponses();
            
            // Show first question
            this.showInterviewContent();
            this.setupNavigationListeners();
            this.renderCurrentQuestion();
            this.updateProgress();
            this.updateNavigation();

            console.log(`Interview Component: Interview initialization completed`);

        } catch (error) {
            console.error('Interview Component: Error loading questions:', error);
            this.showErrorState(error.message);
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Initialize empty responses for all questions
     */
    initializeResponses() {
        this.responses = {};
        this.questions.forEach(question => {
            this.responses[question.id] = {
                question_id: question.id,
                answered_at: null,
                skipped: false
            };

            // Initialize based on question type
            if (question.ui_type === 'text_input') {
                this.responses[question.id].text_value = '';
            } else {
                this.responses[question.id].selected_values = [];
            }
        });
    }

    /**
     * Render the current question
     */
    renderCurrentQuestion() {
        if (this.currentQuestionIndex >= this.questions.length) return;

        const question = this.questions[this.currentQuestionIndex];
        const container = document.getElementById('question-container');
        
        container.innerHTML = this.generateQuestionHTML(question);
        
        // Add event listeners for option cards
        this.setupEventListeners(question);
        
        // Restore previous answers if any
        this.restoreQuestionState(question);
        
        console.log(`Interview Component: Rendered question ${this.currentQuestionIndex + 1}: ${question.id}`);
    }

    /**
     * Setup navigation button event listeners (called once during initialization)
     */
    setupNavigationListeners() {
        const prevButton = document.getElementById('prev-button');
        const nextButton = document.getElementById('next-button');
        const skipButton = document.getElementById('skip-button');
        const submitButton = document.getElementById('submit-button');
        const closeButton = document.getElementById('close-button');

        if (prevButton) {
            prevButton.addEventListener('click', () => {
                console.log('Previous button clicked');
                this.previousQuestion();
            });
        }

        if (nextButton) {
            nextButton.addEventListener('click', () => {
                console.log('Next button clicked');
                this.nextQuestion();
            });
        }

        if (skipButton) {
            skipButton.addEventListener('click', () => {
                console.log('Skip button clicked');
                this.skipQuestion();
            });
        }

        if (submitButton) {
            submitButton.addEventListener('click', () => {
                console.log('Submit button clicked');
                this.submitInterview();
            });
        }

        if (closeButton) {
            closeButton.addEventListener('click', () => {
                console.log('Close button clicked');
                this.closeInterview();
            });
        }

        console.log('Navigation listeners setup completed');
    }

    /**
     * Setup event listeners for the current question
     */
    setupEventListeners(question) {
        // Handle option card clicks for choice questions
        if (question.ui_type === 'multiple_choice' || question.ui_type === 'single_choice') {
            const optionCards = document.querySelectorAll('.option-card');
            optionCards.forEach(card => {
                card.addEventListener('click', (e) => {
                    const questionId = card.dataset.questionId;
                    const optionValue = card.dataset.optionValue;
                    const isSingleChoice = card.dataset.isSingleChoice === 'true';
                    this.selectOption(questionId, optionValue, isSingleChoice, card);
                });
            });
        }
        
        // Handle text input for text questions
        if (question.ui_type === 'text_input') {
            const textarea = document.getElementById(`text-input-${question.id}`);
            if (textarea) {
                textarea.addEventListener('input', (e) => {
                    this.handleTextInput(question.id);
                });
            }
        }
    }

    /**
     * Generate HTML for a question based on its type
     */
    generateQuestionHTML(question) {
        let html = `
            <div class="question-content" style="height: 100%; display: flex; flex-direction: column;">
                <div class="question-header" style="flex-shrink: 0; text-align: center; margin-bottom: 2.5rem;">
                    <h2 class="question-title" style="font-size: 1.4rem; font-weight: 600; color: #1e293b; margin-bottom: 0.75rem; line-height: 1.3;">${question.question}</h2>
                    ${question.subtitle ? `<p class="question-subtitle" style="font-size: 1.1rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 500;">${question.subtitle}</p>` : ''}
                    ${question.purpose ? `
                        <div class="question-purpose" style="margin-top: 1rem; width: 100%;">
                            <p style="font-size: 0.95rem; color: #94a3b8; line-height: 1.2; width: 100%; margin: 0; background: #f8fafc; padding: 0.75rem 1.25rem; border-radius: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${question.purpose}</p>
                        </div>
                    ` : ''}
                </div>
                <div class="question-body" style="flex: 1; display: flex; flex-direction: column;">
        `;

        if (question.ui_type === 'multiple_choice' || question.ui_type === 'single_choice') {
            html += this.generateChoiceOptionsHTML(question);
        } else if (question.ui_type === 'text_input') {
            html += this.generateTextInputHTML(question);
        }

        html += `
                </div>
            </div>
        `;

        return html;
    }

    /**
     * Generate HTML for choice-based questions (single/multiple choice)
     */
    generateChoiceOptionsHTML(question) {
        const isLargeCards = question.display_type === 'large_button_cards_with_icons';
        const gridClass = isLargeCards ? 'button-cards-large' : 'button-cards';

        let html = `<div class="option-grid ${gridClass}">`;

        question.options.forEach(option => {
            const cardClass = isLargeCards ? 'option-card large-card' : 'option-card';
            // Check for description in either 'description' or 'tooltip' field
            const descriptionText = option.description || option.tooltip || '';
            const hasDescription = descriptionText.trim().length > 0;
            
            html += `
                <div class="${cardClass}" 
                     data-question-id="${question.id}"
                     data-option-value="${option.value}"
                     data-is-single-choice="${question.ui_type === 'single_choice'}"
                     style="cursor: pointer;">
                    ${option.icon ? `<div class="option-icon"><i class="${option.icon}"></i></div>` : ''}
                    <div class="option-label">${option.label}</div>
                    ${hasDescription ? `<div class="option-description">${descriptionText}</div>` : ''}
                </div>
            `;
        });

        html += '</div>';
        return html;
    }

    /**
     * Generate HTML for text input questions
     */
    generateTextInputHTML(question) {
        const maxLength = question.max_length || 500;
        const rows = question.rows || 4;

        return `
            <div class="text-input-container">
                <div class="mb-3">
                    <textarea class="form-control" 
                              id="text-input-${question.id}"
                              data-question-id="${question.id}"
                              placeholder="${question.placeholder || ''}"
                              maxlength="${maxLength}"
                              rows="${rows}"></textarea>
                    <div class="char-count text-muted small">
                        <span id="char-count-${question.id}">0</span> / ${maxLength}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Handle option selection for choice questions
     */
    selectOption(questionId, optionValue, isSingleChoice, cardElement) {
        console.log(`Interview Component: selectOption called with questionId=${questionId}, optionValue=${optionValue}, isSingleChoice=${isSingleChoice}`);
        
        const response = this.responses[questionId];
        console.log(`Interview Component: Current response before update:`, response);
        
        if (isSingleChoice) {
            // Single choice: replace selection
            response.selected_values = [optionValue];
            response.answered_at = new Date().toISOString();
            response.skipped = false;
            
            // Update UI - clear all selections then select this one
            document.querySelectorAll(`[data-question-id="${questionId}"]`).forEach(card => {
                card.classList.remove('selected');
            });
            cardElement.classList.add('selected');
            
        } else {
            // Multiple choice: toggle selection
            const index = response.selected_values.indexOf(optionValue);
            
            if (index > -1) {
                // Remove selection
                response.selected_values.splice(index, 1);
                cardElement.classList.remove('selected');
                console.log(`Interview Component: Removed selection, new array:`, response.selected_values);
            } else {
                // Add selection
                response.selected_values.push(optionValue);
                cardElement.classList.add('selected');
                console.log(`Interview Component: Added selection, new array:`, response.selected_values);
            }
            
            response.answered_at = new Date().toISOString();
            response.skipped = false;
        }

        console.log(`Interview Component: Final response after update:`, response);
        console.log(`Interview Component: About to call updateNavigation()`);
        this.updateNavigation();
    }

    /**
     * Handle text input changes
     */
    handleTextInput(questionId) {
        const textarea = document.getElementById(`text-input-${questionId}`);
        const charCount = document.getElementById(`char-count-${questionId}`);
        
        if (textarea && charCount) {
            const length = textarea.value.length;
            charCount.textContent = length;
            
            // Update response
            this.responses[questionId].text_value = textarea.value;
            this.responses[questionId].answered_at = new Date().toISOString();
            this.responses[questionId].skipped = false;
            
            this.updateNavigation();
        }
    }

    /**
     * Restore question state from previous answers
     */
    restoreQuestionState(question) {
        const response = this.responses[question.id];
        
        if (question.ui_type === 'text_input') {
            const textarea = document.getElementById(`text-input-${question.id}`);
            if (textarea && response.text_value) {
                textarea.value = response.text_value;
                this.handleTextInput(question.id);
            }
        } else if (response.selected_values && response.selected_values.length > 0) {
            response.selected_values.forEach(value => {
                const card = document.querySelector(`[data-question-id="${question.id}"][data-option-value="${value}"]`);
                if (card) {
                    card.classList.add('selected');
                }
            });
        }
    }

    /**
     * Move to next question or show summary page
     */
    nextQuestion() {
        if (this.currentQuestionIndex < this.questions.length - 1) {
            this.currentQuestionIndex++;
            this.renderCurrentQuestion();
            this.updateProgress();
            this.updateNavigation();
        } else if (this.currentQuestionIndex === this.questions.length - 1) {
            // Move to summary page
            this.currentQuestionIndex = this.questions.length;
            this.showSummaryPage();
            this.updateProgress();
            this.updateNavigation();
        }
    }

    /**
     * Move to previous question
     */
    previousQuestion() {
        if (this.currentQuestionIndex === this.questions.length) {
            // Going back from summary page to last question
            this.currentQuestionIndex = this.questions.length - 1;
            this.renderCurrentQuestion();
            this.updateProgress();
            this.updateNavigation();
        } else if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.renderCurrentQuestion();
            this.updateProgress();
            this.updateNavigation();
        }
    }

    /**
     * Skip current question
     */
    skipQuestion() {
        const question = this.questions[this.currentQuestionIndex];
        if (!question.required) {
            this.responses[question.id].skipped = true;
            this.responses[question.id].answered_at = new Date().toISOString();
            
            if (this.currentQuestionIndex < this.questions.length - 1) {
                this.nextQuestion();
            } else {
                this.updateNavigation();
            }
        }
    }

    /**
     * Check if current question is answered
     */
    isCurrentQuestionAnswered() {
        const question = this.questions[this.currentQuestionIndex];
        const response = this.responses[question.id];
        
        console.log(`Interview Component: isCurrentQuestionAnswered() checking question ${question.id}`);
        console.log(`  Response:`, response);
        console.log(`  Response skipped:`, response.skipped);
        
        if (response.skipped) {
            console.log(`  Question was skipped, returning true`);
            return true;
        }
        
        if (question.ui_type === 'text_input') {
            const hasText = response.text_value.trim().length > 0;
            const result = question.required ? hasText : true;
            console.log(`  Text input question - hasText: ${hasText}, required: ${question.required}, result: ${result}`);
            return result;
        } else {
            const minSelections = question.min_selections || (question.required ? 1 : 0);
            const result = response.selected_values.length >= minSelections;
            console.log(`  Choice question - selected_values.length: ${response.selected_values.length}, minSelections: ${minSelections}, result: ${result}`);
            return result;
        }
    }

    /**
     * Update progress indicator
     */
    updateProgress() {
        const totalQuestions = this.questions.length;
        const currentStep = this.currentQuestionIndex + 1;
        const isOnSummaryPage = this.currentQuestionIndex === this.questions.length;
        const progressPercent = isOnSummaryPage ? 100 : (currentStep / totalQuestions) * 100;
        
        // Update progress bar
        const progressBar = document.getElementById('progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progressPercent}%`;
        }
        
        // Update progress text
        const progressText = document.getElementById('progress-text');
        if (progressText) {
            if (isOnSummaryPage) {
                progressText.textContent = `Review Your Answers`;
            } else {
                progressText.textContent = `Question ${currentStep} of ${totalQuestions}`;
            }
        }
        
    }

    /**
     * Show summary page with all questions and answers using the answer JSON
     */
    showSummaryPage() {
        console.log('Showing summary page...');
        
        const container = document.getElementById('question-container');
        if (!container) return;
        
        // Get the complete response JSON (same format that will be submitted)
        const responseData = {
            interview_id: this.interviewId,
            responses: this.responses,
            navigation: this.navigation,
            metadata: this.metadata
        };
        
        console.log('Response data for summary:', responseData);
        
        // Build summary HTML
        let summaryHTML = `
            <div class="summary-page">
                <h4 class="mb-4">
                    <i class="fas fa-clipboard-check me-2 text-success"></i>
                    Review Your Responses
                </h4>
                <p class="text-muted mb-4">Please review your answers before submitting. You can go back to make changes if needed.</p>
                
                <div class="row">
                    <div class="col-12">
        `;
        
        // Display each question and answer using the responses JSON
        this.questions.forEach((question, index) => {
            const response = responseData.responses[question.id];
            if (!response) return;
            
            summaryHTML += `
                <div class="summary-item mb-4 p-3 border rounded bg-light">
                    <h6 class="text-primary mb-2">
                        <i class="fas fa-question-circle me-1"></i>
                        Question ${index + 1}: ${question.question}
                    </h6>
            `;
            
            if (response.skipped) {
                summaryHTML += `<p class="text-muted"><em>Skipped</em></p>`;
            } else if (question.ui_type === 'text_input') {
                const answer = response.text_value || 'No answer provided';
                summaryHTML += `<p class="mb-0"><strong>Answer:</strong> ${answer}</p>`;
            } else {
                // Multiple choice or single choice
                if (response.selected_values && response.selected_values.length > 0) {
                    const selectedLabels = response.selected_values.map(value => {
                        const option = question.options.find(opt => opt.value === value);
                        return option ? option.label : value;
                    });
                    summaryHTML += `<p class="mb-0"><strong>Selected:</strong> ${selectedLabels.join(', ')}</p>`;
                } else {
                    summaryHTML += `<p class="text-muted mb-0"><em>No selection made</em></p>`;
                }
            }
            
            summaryHTML += `</div>`;
        });
        
        summaryHTML += `
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = summaryHTML;
    }

    /**
     * Update navigation buttons
     */
    updateNavigation() {
        const isOnSummaryPage = this.currentQuestionIndex === this.questions.length;
        const question = isOnSummaryPage ? null : this.questions[this.currentQuestionIndex];
        const isAnswered = isOnSummaryPage ? true : this.isCurrentQuestionAnswered();
        const isFirstQuestion = this.currentQuestionIndex === 0;
        const isLastQuestion = this.currentQuestionIndex === this.questions.length - 1;
        
        console.log(`Interview Component: updateNavigation() called`);
        console.log(`  Current question:`, question);
        console.log(`  Question required:`, question?.required);
        console.log(`  Is answered:`, isAnswered);
        console.log(`  Is first question:`, isFirstQuestion);
        console.log(`  Is last question:`, isLastQuestion);
        console.log(`  Is on summary page:`, isOnSummaryPage);
        
        // Previous button
        const prevButton = document.getElementById('prev-button');
        if (prevButton) {
            prevButton.disabled = isFirstQuestion;
            console.log(`  Previous button disabled:`, prevButton.disabled);
        }
        
        // Skip button
        const skipButton = document.getElementById('skip-button');
        if (skipButton) {
            if (question && !question.required) {
                skipButton.classList.remove('d-none');
                skipButton.textContent = question.skip_button_text || 'Skip for now';
            } else {
                skipButton.classList.add('d-none');
            }
            console.log(`  Skip button hidden:`, skipButton.classList.contains('d-none'));
        }
        
        // Next/Submit buttons
        const nextButton = document.getElementById('next-button');
        const submitButton = document.getElementById('submit-button');
        
        if (isOnSummaryPage) {
            // On summary page - show only submit button
            if (nextButton) nextButton.classList.add('d-none');
            if (submitButton) {
                submitButton.classList.remove('d-none');
                submitButton.disabled = false; // Always enabled on summary page
                submitButton.innerHTML = '<i class="fas fa-check"></i> Submit Interview';
                console.log(`  Submit button enabled on summary page`);
            }
            // Hide skip button on summary page
            if (skipButton) skipButton.classList.add('d-none');
        } else if (isLastQuestion) {
            // On last question - show "Review Answers" button instead of submit
            if (nextButton) {
                nextButton.classList.remove('d-none');
                nextButton.disabled = !isAnswered && (question?.required || false);
                nextButton.innerHTML = '<i class="fas fa-clipboard-check me-1"></i> Review Answers';
                console.log(`  Review button disabled:`, nextButton.disabled);
            }
            if (submitButton) submitButton.classList.add('d-none');
        } else {
            // Regular questions - show next button
            if (nextButton) {
                nextButton.classList.remove('d-none');
                nextButton.innerHTML = 'Next <i class="fas fa-arrow-right"></i>';
                const shouldDisable = !isAnswered && (question?.required || false);
                nextButton.disabled = shouldDisable;
                console.log(`  Next button disabled:`, nextButton.disabled, `(shouldDisable: ${shouldDisable}, !isAnswered: ${!isAnswered}, question.required: ${question?.required})`);
            }
            if (submitButton) submitButton.classList.add('d-none');
        }
    }

    /**
     * Submit the completed interview
     */
    async submitInterview() {
        if (this.isSubmitting) return;
        
        this.isSubmitting = true;
        this.metadata.end_time = new Date().toISOString();
        
        const submitButton = document.getElementById('submit-button');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="spinner-border spinner-border-sm me-2"></i>Submitting...';
        }

        try {
            // Calculate metadata
            const startTime = new Date(this.metadata.start_time);
            const endTime = new Date(this.metadata.end_time);
            const totalTimeSeconds = Math.round((endTime - startTime) / 1000);
            const questionsSkipped = Object.values(this.responses).filter(r => r.skipped).length;
            
            // Determine navigation based on responses
            const navigation = this.calculateNavigation();
            
            // Clean up responses - ensure answered_at is never null
            const cleanedResponses = {};
            Object.keys(this.responses).forEach(key => {
                const response = { ...this.responses[key] };
                if (response.answered_at === null) {
                    response.answered_at = '';
                }
                cleanedResponses[key] = response;
            });
            
            const submission = {
                interview_id: this.interviewId,
                responses: cleanedResponses,
                navigation: navigation,
                metadata: {
                    ...this.metadata,
                    total_time_seconds: totalTimeSeconds,
                    questions_skipped: questionsSkipped,
                    completion_rate: ((this.questions.length - questionsSkipped) / this.questions.length) * 100
                }
            };

            console.log('Interview Component: Submitting interview:', submission);

            // Add timeout to prevent hanging
            const controller = new AbortController();
            const timeoutId = setTimeout(() => {
                controller.abort();
                console.error('Interview Component: Request timed out after 30 seconds');
            }, 30000);

            const response = await fetch('/api/v1/interview/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(submission),
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            console.log('Interview Component: Received response:', response.status, response.statusText);

            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                    console.error('Interview Component: Error response data:', errorData);
                } catch (e) {
                    console.error('Interview Component: Could not parse error response');
                    errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
                }
                throw new Error(errorData.detail || 'Failed to submit interview');
            }

            const result = await response.json();
            console.log('Interview Component: Interview submitted successfully:', result);

            // Close modal and trigger completion event
            this.handleSuccessfulSubmission(result.interview_id, navigation);

        } catch (error) {
            console.error('Interview Component: Error submitting interview:', error);
            
            // Check if this is a timeout or network error
            if (error.name === 'AbortError') {
                console.warn('Interview Component: Request timed out, showing thank you message anyway');
                // Show thank you message even on timeout
                this.handleSuccessfulSubmission('timeout', this.calculateNavigation());
            } else {
                this.handleSubmissionError(error.message);
            }
        } finally {
            this.isSubmitting = false;
        }
    }

    /**
     * Calculate navigation destination based on responses
     */
    calculateNavigation() {
        const nextStepResponse = this.responses.next_step;
        const brainstormResponse = this.responses.brainstorming_popup;
        
        let finalDestination = '/ui/'; // Default - homepage
        let fromQuestion5 = '/ui/';
        let showBrainstormPopup = false;
        
        // Determine destination from Question 5
        if (nextStepResponse && nextStepResponse.selected_values.length > 0) {
            const choice = nextStepResponse.selected_values[0];
            switch (choice) {
                case 'quick_story':
                    fromQuestion5 = '/ui/stories/new/basic';
                    break;
                case 'world_first':
                    fromQuestion5 = '/ui/worlds/new';
                    break;
                case 'homepage':
                    fromQuestion5 = '/ui/';
                    break;
            }
        }
        
        // Check if user wants brainstorming (Question 6 overrides Question 5)
        if (brainstormResponse && brainstormResponse.selected_values.includes('yes_brainstorm')) {
            finalDestination = '/ui/'; // Redirect to homepage instead of non-existent brainstorm page
            showBrainstormPopup = true;
        } else {
            finalDestination = fromQuestion5;
        }
        
        return {
            final_destination: finalDestination,
            from_question_5: fromQuestion5,
            show_brainstorm_popup: showBrainstormPopup,
            brainstorm_route: showBrainstormPopup ? '/ui/' : null
        };
    }

    /**
     * Handle successful submission
     */
    handleSuccessfulSubmission(interviewId, navigation) {
        // Show thank you message in the modal
        this.showThankYouMessage(navigation);
        
        // Trigger custom event for the calling application
        // Use the original interview type ID (this.interviewId) instead of the response ID
        const completionEvent = new CustomEvent('interviewCompleted', {
            detail: {
                interviewId: this.interviewId,  // Use original interview type ID like 'story_brainstorm'
                responseId: interviewId,        // Include the actual response ID for reference
                navigation: navigation,
                completed: true
            }
        });
        document.dispatchEvent(completionEvent);
        
        // Store navigation for later use
        this.completionNavigation = navigation;
    }
    
    /**
     * Close interview modal (called by Close button)
     */
    closeInterview() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('interviewModal'));
        if (modal) {
            modal.hide();
        }
        
        // The calling page is responsible for handling what happens after interview completion
        // The interview component only collects answers
    }
    
    /**
     * Show thank you message after successful submission
     */
    showThankYouMessage(navigation) {
        const container = document.getElementById('question-container');
        
        let destinationText = 'the homepage';
        if (navigation.final_destination === '/ui/stories/new/basic') {
            destinationText = 'story creation';
        } else if (navigation.final_destination === '/ui/worlds/new') {
            destinationText = 'world building';
        } else if (navigation.final_destination === '/ui/' && navigation.show_brainstorm_popup) {
            destinationText = 'the homepage where you can explore brainstorming options';
        } else if (navigation.final_destination === '/ui/') {
            destinationText = 'the homepage';
        }
        
        container.innerHTML = `
            <div class="card-body text-center py-5">
                <div class="mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-circle-check" width="64" height="64" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round" style="color: var(--tblr-success);">
                        <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                        <circle cx="12" cy="12" r="9"/>
                        <path d="M9 12l2 2l4 -4"/>
                    </svg>
                </div>
                <h3 class="text-success mb-3">Thank You!</h3>
                <p class="text-muted mb-4">
                    Your interview has been completed successfully. We've saved your preferences and will use them to personalize your experience.
                </p>
                <div class="alert alert-info">
                    <div class="d-flex">
                        <div>
                            <svg xmlns="http://www.w3.org/2000/svg" class="icon alert-icon" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
                                <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                                <circle cx="12" cy="12" r="9"/>
                                <line x1="12" y1="8" x2="12" y2="12"/>
                                <line x1="12" y1="16" x2="12.01" y2="16"/>
                            </svg>
                        </div>
                        <div>
                            <h4 class="alert-title">What's Next?</h4>
                            <div class="text-muted">We're redirecting you to ${destinationText} in a moment...</div>
                        </div>
                    </div>
                </div>
                <div class="progress progress-sm mt-3">
                    <div class="progress-bar progress-bar-indeterminate bg-success"></div>
                </div>
            </div>
        `;
        
        // Hide navigation buttons and show close button
        const prevButton = document.getElementById('prev-button');
        const nextButton = document.getElementById('next-button');
        const skipButton = document.getElementById('skip-button');
        const submitButton = document.getElementById('submit-button');
        const closeButton = document.getElementById('close-button');
        
        if (prevButton) {
            prevButton.style.display = 'none';
            prevButton.classList.add('d-none');
        }
        if (nextButton) {
            nextButton.style.display = 'none';
            nextButton.classList.add('d-none');
        }
        if (skipButton) {
            skipButton.style.display = 'none';
            skipButton.classList.add('d-none');
        }
        if (submitButton) {
            submitButton.style.display = 'none';
            submitButton.classList.add('d-none');
        }
        if (closeButton) {
            closeButton.style.display = 'inline-flex';
            closeButton.classList.remove('d-none');
        }
        
        // Hide progress bar
        const progressContainer = document.querySelector('.modal-footer .d-flex.align-items-center.flex-grow-1');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    }

    /**
     * Handle submission error
     */
    handleSubmissionError(errorMessage) {
        const submitButton = document.getElementById('submit-button');
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-check"></i> Complete Interview';
        }
        
        this.showToast('Submission Error', errorMessage, 'error');
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        document.getElementById('interview-loading').classList.remove('d-none');
        document.getElementById('interview-error').classList.add('d-none');
        document.getElementById('interview-content').classList.add('d-none');
    }

    /**
     * Show error state
     */
    showErrorState(message) {
        document.getElementById('interview-error-message').textContent = message;
        document.getElementById('interview-loading').classList.add('d-none');
        document.getElementById('interview-error').classList.remove('d-none');
        document.getElementById('interview-content').classList.add('d-none');
    }

    /**
     * Show interview content
     */
    showInterviewContent() {
        document.getElementById('interview-loading').classList.add('d-none');
        document.getElementById('interview-error').classList.add('d-none');
        document.getElementById('interview-content').classList.remove('d-none');
    }

    /**
     * Show toast notification
     */
    showToast(title, message, type = 'info') {
        // Use existing toast system or create a simple alert
        if (typeof showToast === 'function') {
            showToast(title, message, type);
        } else {
            const alertClass = type === 'success' ? 'alert-success' : type === 'error' ? 'alert-danger' : 'alert-info';
            const toastHtml = `
                <div class="toast align-items-center ${alertClass} border-0" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
                    <div class="d-flex">
                        <div class="toast-body">
                            <strong>${title}</strong><br>${message}
                        </div>
                        <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', toastHtml);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                const toasts = document.querySelectorAll('.toast');
                if (toasts.length > 0) {
                    toasts[toasts.length - 1].remove();
                }
            }, 5000);
        }
    }
}

// Create global instance
window.InterviewComponent = new InterviewComponent();

// Global functions for onclick handlers
window.InterviewComponent.selectOption = window.InterviewComponent.selectOption.bind(window.InterviewComponent);
window.InterviewComponent.handleTextInput = window.InterviewComponent.handleTextInput.bind(window.InterviewComponent);
window.InterviewComponent.nextQuestion = window.InterviewComponent.nextQuestion.bind(window.InterviewComponent);
window.InterviewComponent.previousQuestion = window.InterviewComponent.previousQuestion.bind(window.InterviewComponent);
window.InterviewComponent.skipQuestion = window.InterviewComponent.skipQuestion.bind(window.InterviewComponent);
window.InterviewComponent.submitInterview = window.InterviewComponent.submitInterview.bind(window.InterviewComponent);
window.InterviewComponent.loadQuestions = window.InterviewComponent.loadQuestions.bind(window.InterviewComponent);