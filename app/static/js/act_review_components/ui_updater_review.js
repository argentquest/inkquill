// /ai_rag_story_app/app/static/js/act_review_components/ui_updater_review.js
"use strict";

const UIUpdater_Review = (() => {
    // Element IDs (ensure these match your HTML)
    const suggestionsContainerId = 'ai-review-suggestions-container';
    const metricsContainerId = 'ai-review-metrics-container';
    const initialSuggestionsPlaceholderId = 'initial-suggestions-placeholder';
    const initialMetricsPlaceholderId = 'initial-metrics-placeholder';
    const rawAIOutputDisplayId = 'raw-ai-output-display-review';
    const aiPromptDisplayId = 'ai-prompt-display-review';

    // Correct escapeHtml function
    function escapeHtml(unsafe) {
        if (unsafe === null || typeof unsafe === 'undefined') return '';
        return String(unsafe)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function updateRawAIOutput(text, isPrettyJSON = false) {
        const element = document.getElementById(rawAIOutputDisplayId);
        if (element) {
            if (isPrettyJSON && text) {
                try {
                    const parsed = JSON.parse(text);
                    element.textContent = JSON.stringify(parsed, null, 2);
                } catch (e) {
                    console.warn("UIUpdater_Review: Failed to pretty-print JSON for raw output, displaying as raw text.", e);
                    element.textContent = text;
                }
            } else {
                element.textContent = text || "No raw AI output to display.";
            }
        } else {
            console.warn("UIUpdater_Review: Raw AI output display element not found.");
        }
    }

    function updateAIPromptDisplay(text) {
        const element = document.getElementById(aiPromptDisplayId);
        if (element) {
            element.textContent = text || "Prompt arguments will appear here.";
        } else {
            console.warn("UIUpdater_Review: AI prompt display element not found.");
        }
    }

    function clearAllPlaceholders() {
        const suggestionsPlaceholder = document.getElementById(initialSuggestionsPlaceholderId);
        const metricsPlaceholder = document.getElementById(initialMetricsPlaceholderId);
        if (suggestionsPlaceholder) suggestionsPlaceholder.style.display = 'none';
        if (metricsPlaceholder) metricsPlaceholder.style.display = 'none';
    }

    function showPlaceholder(type, message = "") {
        let elId, defaultMessage;
        if (type === 'suggestions') {
            elId = initialSuggestionsPlaceholderId;
            defaultMessage = "No textual suggestions provided by the AI.";
        } else if (type === 'metrics') {
            elId = initialMetricsPlaceholderId;
            defaultMessage = "No metrics data provided by the AI.";
        } else {
            return; 
        }
        const el = document.getElementById(elId);
        if (el) {
            el.textContent = message || defaultMessage;
            el.style.display = 'block';
        }
    }

    function renderSuggestions(suggestionsList) {
        const container = document.getElementById(suggestionsContainerId);
        if (!container) {
            console.warn("UIUpdater_Review: Suggestions container not found.");
            return;
        }
        container.innerHTML = "";

        const placeholder = document.getElementById(initialSuggestionsPlaceholderId);

        if (!suggestionsList || suggestionsList.length === 0) {
            if (placeholder) {
                placeholder.textContent = "No suggestions provided by the AI.";
                placeholder.style.display = 'block';
            } else {
                container.innerHTML = '<p class="text-muted p-3">No suggestions provided by the AI.</p>';
            }
            return;
        }
        if (placeholder) placeholder.style.display = 'none';

        const ul = document.createElement('ul');
        ul.className = 'list-group list-group-flush mt-2';
        suggestionsList.forEach((suggestion) => {
            const li = document.createElement('li');
            li.className = 'list-group-item suggestion-item-clickable';
            li.style.cursor = 'pointer';
            li.dataset.contextStart = suggestion.context_start_snippet || "";
            li.dataset.contextEnd = suggestion.context_end_snippet || "";

            let severityClass = 'text-secondary';
            let severityText = escapeHtml(suggestion.severity || 'N/A');
            if (suggestion.severity && typeof suggestion.severity === 'string') {
                switch (suggestion.severity.toLowerCase()) {
                    case 'high': severityClass = 'text-danger fw-bold'; break;
                    case 'medium': severityClass = 'text-warning'; break;
                    case 'low': severityClass = 'text-info'; break;
                }
            }
            const category = escapeHtml(suggestion.category || 'Suggestion');
            const suggestionText = escapeHtml(suggestion.suggestion_text || '');
            
            // Generate unique ID for this suggestion
            const suggestionId = suggestion.id || `suggestion_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            
            const proposedSolution = suggestion.proposed_solution ? `
                <div class="mt-2 p-2 bg-success-subtle border border-success rounded-1">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <small class="text-success fw-bold d-block mb-1">💡 Proposed Solution:</small>
                            <span class="text-dark">${escapeHtml(suggestion.proposed_solution)}</span>
                        </div>
                        <button class="btn btn-outline-success btn-sm ms-2 apply-suggestion-btn" 
                                data-suggestion-id="${escapeHtml(suggestionId)}"
                                data-context-start="${escapeHtml(suggestion.context_start_snippet || '')}"
                                data-context-end="${escapeHtml(suggestion.context_end_snippet || '')}"
                                data-proposed-solution="${escapeHtml(suggestion.proposed_solution)}"
                                title="Apply this suggestion to the text">
                            <i class="fas fa-magic me-1"></i>Apply
                        </button>
                    </div>
                </div>` : '';
            
            const explanation = suggestion.explanation ? `<small class="text-muted d-block mt-1"><em>Explanation: ${escapeHtml(suggestion.explanation)}</em></small>` : '';
            
            let contextSnippetHtml = '';
            if (suggestion.context_start_snippet || suggestion.context_end_snippet) {
                const start = escapeHtml(suggestion.context_start_snippet || '');
                const end = escapeHtml(suggestion.context_end_snippet || '');
                contextSnippetHtml = `
                    <div class="mt-2 p-2 bg-light border rounded-1" style="font-size: 0.8em; font-family: var(--bs-font-monospace);">
                        <small class="text-muted d-block mb-1">📍 Current Text:</small>
                        <span class="text-primary">${start}</span>
                        ${(start && end) ? '<span class="text-muted"> ... </span>' : ''}
                        <span class="text-primary">${end}</span>
                    </div>`;
            }
            
            li.innerHTML = `
                <div class="d-flex w-100 justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${category}</h6>
                        <p class="mb-1 text-dark">${suggestionText}</p>
                    </div>
                    <small class="${severityClass} ms-2">${severityText}</small>
                </div>
                ${proposedSolution}
                ${explanation}
                ${contextSnippetHtml}`;
            ul.appendChild(li);
        });
        container.appendChild(ul);
    }

    const metricDisplayOrder = [
        "originality_of_concept", "engagement_readability", "character_depth_in_act",
        "plot_coherence_pacing_in_act", "descriptive_language", "emotional_resonance_of_act",
        "dialogue_quality", "grammar_technical_accuracy", "reading_level_appropriateness",
        "world_building_consistency", "tension_conflict_development",
        "overall_storytelling_effectiveness_of_act"
    ];

    function renderMetrics(metrics) {
        const container = document.getElementById(metricsContainerId);
        console.log("UIUpdater_Review: renderMetrics CALLED. Received metrics:", JSON.stringify(metrics, null, 2)); // LOG 1

        if (!container) {
            console.warn("UIUpdater_Review: Metrics container (#ai-review-metrics-container) NOT FOUND."); // LOG 2
            return;
        }
        container.innerHTML = "";
        
        const initialMetricsPlaceholder = document.getElementById(initialMetricsPlaceholderId);

        if (!metrics || Object.keys(metrics).length === 0) {
            console.log("UIUpdater_Review: No valid metrics data received or metrics object is empty."); // LOG 3
            if (initialMetricsPlaceholder) {
                initialMetricsPlaceholder.textContent = "No metrics data provided by AI or data is empty.";
                initialMetricsPlaceholder.style.display = 'block';
            } else {
                container.innerHTML = '<p class="text-muted p-3">No metrics data provided by AI or data is empty.</p>';
            }
            return;
        }
        
        if (initialMetricsPlaceholder) {
            console.log("UIUpdater_Review: Hiding initial metrics placeholder."); // LOG 4
            initialMetricsPlaceholder.style.display = 'none';
        }
        
        const dl = document.createElement('dl');
        dl.className = 'row';
        let hasMetricsRendered = false;

        metricDisplayOrder.forEach(key => {
            console.log(`UIUpdater_Review: Processing metric key: '${key}'`); // LOG 5
            if (metrics[key] && typeof metrics[key] === 'object') {
                console.log(`UIUpdater_Review: Data for '${key}':`, metrics[key]); // LOG 6
                hasMetricsRendered = true;
                const metric = metrics[key];
                const dt = document.createElement('dt');
                dt.className = 'col-sm-5 text-muted small';
                dt.textContent = escapeHtml(key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())) + ":";
                
                const dd = document.createElement('dd');
                dd.className = 'col-sm-7 small';
                
                const ratingSpan = document.createElement('span');
                ratingSpan.className = 'fw-bold';
                ratingSpan.textContent = `${escapeHtml(String(metric.rating !== undefined ? metric.rating : 'N/A'))}/5`;
                
                const justificationSpan = document.createElement('span');
                justificationSpan.className = 'ms-2 fst-italic';
                justificationSpan.textContent = `- ${escapeHtml(metric.justification || 'No justification.')}`;
                
                dd.appendChild(ratingSpan);
                dd.appendChild(justificationSpan);
                dl.appendChild(dt);
                dl.appendChild(dd);
            } else {
                console.warn(`UIUpdater_Review: Metric key '${key}' not found in metrics object or not an object. Value:`, metrics[key]); // LOG 7
            }
        });

        if (hasMetricsRendered) {
            console.log("UIUpdater_Review: Appending metrics <dl> to container."); // LOG 8
            container.appendChild(dl);
        } else {
            console.warn("UIUpdater_Review: No metrics were rendered, showing placeholder."); // LOG 9
            if (initialMetricsPlaceholder) {
                initialMetricsPlaceholder.textContent = "Metrics data received but no valid entries found to display.";
                initialMetricsPlaceholder.style.display = 'block';
            } else {
                container.innerHTML = '<p class="text-muted p-3">Metrics data received but was empty or in an unexpected format.</p>';
            }
        }
    }

    return {
        updateRawAIOutput,
        updateAIPromptDisplay,
        renderSuggestions,
        renderMetrics,
        clearAllPlaceholders,
        showPlaceholder
    };
})();