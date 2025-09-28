// /ai_rag_story_app/app/static/js/scene_ai_processor.js
"use strict";

const SceneAIProcessor = (() => {
    // Delimiters are no longer needed here as narrative is streamed as plain text.
    // This function will now primarily parse the metadata JSON.

    function processFullJsonResponse(jsonString) { // This function now processes the METADATA JSON
        console.log("SceneAIProcessor: Processing metadata JSON response. Input length:", jsonString ? jsonString.length : 'null');
        
        let parsedResponse = null;
        // Narrative is handled separately by the orchestrator via direct text streaming.
        // We only extract metadata here.
        let suggestedMood = "N/A";
        let suggestedCharacters = "N/A";
        let suggestedPlotPoints = "N/A";
        let aiCommentary = "";

        if (!jsonString || typeof jsonString !== 'string' || jsonString.trim() === "" || jsonString.trim().toLowerCase() === "null") {
            console.warn("SceneAIProcessor: Received null, empty, non-string, or 'null' string input for metadata. Cannot parse JSON.");
            if (typeof showToast === 'function') showToast("AI metadata response was empty or invalid.", "warning");
            return { suggestedMood, suggestedCharacters, suggestedPlotPoints, aiCommentary, parseError: true };
        }

        try {
            parsedResponse = JSON.parse(jsonString);
            console.log("SceneAIProcessor: Metadata JSON parsed successfully:", parsedResponse);
        } catch (error) {
            console.error("SceneAIProcessor: Error parsing metadata JSON response from AI:", error.message);
            console.error("Problematic metadata JSON string was:", `>>>${jsonString}<<<`); 
            if (typeof showToast === 'function') showToast("Error understanding AI's structured metadata response.", "error");
            return { suggestedMood, suggestedCharacters, suggestedPlotPoints, aiCommentary, parseError: true };
        }

        if (!parsedResponse || typeof parsedResponse !== 'object') {
            console.warn("SceneAIProcessor: Parsed metadata response is not a valid object. Value:", parsedResponse);
            if (typeof showToast === 'function') showToast("AI metadata response was invalid after parsing.", "warning");
            return { suggestedMood, suggestedCharacters, suggestedPlotPoints, aiCommentary, parseError: true };
        }
        
        // Extract metadata fields based on enhanced scene metadata prompt
        suggestedMood = parsedResponse.suggested_mood || "N/A";
        
        // Process characters present (now array of objects)
        let charactersPresent = parsedResponse.suggested_characters_present;
        let charactersPresentText = "N/A";
        if (Array.isArray(charactersPresent) && charactersPresent.length > 0) {
            charactersPresentText = charactersPresent.map(char => 
                `${char.character_name} (${char.role_in_scene}): ${char.character_arc_moment || 'No development'}`
            ).join("\n• ");
            charactersPresentText = "• " + charactersPresentText;
        } else if (typeof charactersPresent === 'string') {
            charactersPresentText = charactersPresent; // Legacy format
        }
        
        let plotPoints = parsedResponse.suggested_plot_points;
        if (Array.isArray(plotPoints)) {
            suggestedPlotPoints = "• " + plotPoints.join("\n• "); 
        } else if (typeof plotPoints === 'string') {
            suggestedPlotPoints = plotPoints;
        } else {
            suggestedPlotPoints = "N/A";
        }

        // Process location/setting analysis (object)
        let locationSetting = parsedResponse.location_setting_analysis;
        let locationSettingText = "N/A";
        if (locationSetting && typeof locationSetting === 'object') {
            locationSettingText = `Location: ${locationSetting.primary_location || 'Unspecified'}\nInfluence: ${locationSetting.setting_influence || ''}\nAtmosphere: ${locationSetting.atmosphere_created || ''}\nEffectiveness: ${locationSetting.setting_effectiveness || 'N/A'}/5`;
        }

        // Process conflict analysis (object)
        let conflictAnalysis = parsedResponse.conflict_analysis;
        let conflictAnalysisText = "N/A";
        if (conflictAnalysis && typeof conflictAnalysis === 'object') {
            conflictAnalysisText = `Present: ${conflictAnalysis.conflict_present ? 'Yes' : 'No'}\nType: ${conflictAnalysis.conflict_type || 'Unknown'}\n${conflictAnalysis.conflict_description || ''}\nStatus: ${conflictAnalysis.resolution_status || 'Unknown'}`;
        }

        // Process dialogue assessment (object)
        let dialogueAssessment = parsedResponse.dialogue_assessment;
        let dialogueAssessmentText = "N/A";
        if (dialogueAssessment && typeof dialogueAssessment === 'object') {
            if (dialogueAssessment.dialogue_present) {
                dialogueAssessmentText = `Effectiveness: ${dialogueAssessment.dialogue_effectiveness || 'N/A'}/5\nVoice Distinction: ${dialogueAssessment.character_voice_distinction || ''}\nPurpose: ${dialogueAssessment.dialogue_purpose || ''}`;
            } else {
                dialogueAssessmentText = "No dialogue present in this scene";
            }
        }

        // Process pacing and tension (object)
        let pacingTension = parsedResponse.pacing_and_tension;
        let pacingTensionText = "N/A";
        if (pacingTension && typeof pacingTension === 'object') {
            pacingTensionText = `Pacing: ${pacingTension.scene_pacing || 'Unknown'}\nTension: ${pacingTension.tension_level || 'Unknown'}\nEffectiveness: ${pacingTension.pacing_effectiveness || 'N/A'}/5\nMomentum: ${pacingTension.momentum_contribution || ''}`;
        }

        // Process sensory engagement (object)
        let sensoryEngagement = parsedResponse.sensory_engagement;
        let sensoryEngagementText = "N/A";
        if (sensoryEngagement && typeof sensoryEngagement === 'object') {
            const senses = sensoryEngagement.senses_engaged || [];
            sensoryEngagementText = `Details Present: ${sensoryEngagement.sensory_details_present ? 'Yes' : 'No'}\nSenses: ${Array.isArray(senses) ? senses.join(', ') : 'None'}\nImmersion: ${sensoryEngagement.immersion_level || 'N/A'}/5\n${sensoryEngagement.sensory_effectiveness || ''}`;
        }

        // Process scene purpose and function (object)
        let scenePurpose = parsedResponse.scene_purpose_function;
        let scenePurposeText = "N/A";
        if (scenePurpose && typeof scenePurpose === 'object') {
            scenePurposeText = `Purpose: ${scenePurpose.primary_purpose || 'Unknown'}\nStory Advancement: ${scenePurpose.story_advancement || ''}\nEmotional Impact: ${scenePurpose.emotional_impact || ''}\nNecessity: ${scenePurpose.scene_necessity || 'N/A'}/5`;
        }

        // Process transition quality (object)
        let transitionQuality = parsedResponse.transition_quality;
        let transitionQualityText = "N/A";
        if (transitionQuality && typeof transitionQuality === 'object') {
            transitionQualityText = `Opens Well: ${transitionQuality.opens_effectively ? 'Yes' : 'No'}\nCloses Well: ${transitionQuality.closes_effectively ? 'Yes' : 'No'}\nConnection to Previous: ${transitionQuality.connection_to_previous || ''}\nSetup for Next: ${transitionQuality.setup_for_next || ''}`;
        }

        // Process scene strengths (array)
        let sceneStrengths = parsedResponse.scene_strengths;
        let sceneStrengthsText = "N/A";
        if (Array.isArray(sceneStrengths) && sceneStrengths.length > 0) {
            sceneStrengthsText = "• " + sceneStrengths.join("\n• ");
        }

        // Process improvement suggestions (array)
        let improvementSuggestions = parsedResponse.improvement_suggestions;
        let improvementSuggestionsText = "N/A";
        if (Array.isArray(improvementSuggestions) && improvementSuggestions.length > 0) {
            improvementSuggestionsText = "• " + improvementSuggestions.join("\n• ");
        }

        aiCommentary = ""; // No longer used in new format
        
        return {
            // Legacy fields for backward compatibility
            suggestedMood: suggestedMood,
            suggestedCharacters: charactersPresentText,
            suggestedPlotPoints: suggestedPlotPoints,
            aiCommentary: aiCommentary,
            // New comprehensive fields
            locationSettingAnalysis: locationSettingText,
            conflictAnalysis: conflictAnalysisText,
            dialogueAssessment: dialogueAssessmentText,
            pacingTension: pacingTensionText,
            sensoryEngagement: sensoryEngagementText,
            scenePurpose: scenePurposeText,
            transitionQuality: transitionQualityText,
            sceneStrengths: sceneStrengthsText,
            improvementSuggestions: improvementSuggestionsText,
            parseError: false
        };
    }

    function processRagContextMessageForScene(ragData) {
        let summary = "No relevant background information found.";
        let details = "No RAG context details available for this generation.";

        if (ragData) { 
            if (Array.isArray(ragData) && ragData.length > 0) {
                summary = ragData.map(doc => `Source: ${doc.source_filename || 'N/A'}\nSnippet: ${(doc.text || '').substring(0,100)}...`).join('\n---\n');
                try {
                    details = JSON.stringify(ragData, null, 2);
                } catch (e) {
                    console.error("SceneAIProcessor: Error stringifying RAG details array:", e);
                    details = "Error formatting RAG details for display. Raw data received from server.";
                }
            } else if (typeof ragData === 'string' && ragData.trim() !== "") {
                summary = ragData.substring(0, 300) + (ragData.length > 300 ? "..." : "");
                details = ragData; 
            } else if (typeof ragData === 'object' && Object.keys(ragData).length > 0) {
                summary = `Received RAG data object. See details tab for full content.`; 
                try {
                    details = JSON.stringify(ragData, null, 2);
                } catch (e) {
                    console.error("SceneAIProcessor: Error stringifying RAG details object:", e);
                    details = "Error formatting RAG details object for display.";
                }
            } else if (typeof ragData === 'string' && ragData.trim() === "") {
                summary = "RAG system returned an empty string.";
                details = "RAG system returned an empty string.";
            }
        }
        return { summary, details };
    }

    function processFullPromptMessageForScene(promptData) {
        let details = "Full prompt data not available or formatting error from server.";
        if (promptData && typeof promptData === 'string') {
            details = promptData; 
        } else if (promptData) {
            try {
                details = JSON.stringify(promptData, null, 2);
            } catch (e) {
                console.error("SceneAIProcessor: Error stringifying full prompt data for scene:", e);
                details = "Error formatting full prompt data for scene. Raw data might be an object.";
            }
        }
        return { details };
    }

    return {
        processFullJsonResponse: processFullJsonResponse, // This now focuses on metadata JSON
        processRagContextMessage: processRagContextMessageForScene, 
        processFullPromptMessage: processFullPromptMessageForScene 
    };
})();