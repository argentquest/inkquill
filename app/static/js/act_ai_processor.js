// /ai_rag_story_app/app/static/js/act_ai_processor.js
"use strict";

const ActAIProcessor = (() => {
    // Delimiters are no longer used for the main narrative stream with the two-call approach.
    // This function will now be primarily for parsing the metadata JSON for Acts.

    function processActMetadataJsonResponse(jsonString) {
        console.log("ActAIProcessor: Processing Act metadata JSON response. Input length:", jsonString ? jsonString.length : 'null');
        
        let parsedResponse = null;
        // Default values for Act metadata (adjust based on your generate_act_metadata.txt prompt)
        let suggestedActSummaryPoints = "N/A";
        let keyCharacterDevelopments = "N/A";
        let pacingAndFlowCommentary = "N/A";
        let aiGeneralCommentary = ""; // For the "Use as Next Instruction" button

        if (!jsonString || typeof jsonString !== 'string' || jsonString.trim() === "" || jsonString.trim().toLowerCase() === "null") {
            console.warn("ActAIProcessor: Received null, empty, non-string, or 'null' string input for Act metadata. Cannot parse JSON.");
            if (typeof showToast === 'function') showToast("AI Act metadata response was empty or invalid.", "warning");
            return { 
                suggestedActSummaryPoints, 
                keyCharacterDevelopments, 
                pacingAndFlowCommentary, 
                aiGeneralCommentary, 
                parseError: true 
            };
        }

        try {
            parsedResponse = JSON.parse(jsonString);
            console.log("ActAIProcessor: Act metadata JSON parsed successfully:", parsedResponse);
        } catch (error) {
            console.error("ActAIProcessor: Error parsing Act metadata JSON response from AI:", error.message);
            console.error("Problematic Act metadata JSON string was:", `>>>${jsonString}<<<`); 
            if (typeof showToast === 'function') showToast("Error understanding AI's structured Act metadata.", "error");
            return { 
                suggestedActSummaryPoints, 
                keyCharacterDevelopments, 
                pacingAndFlowCommentary, 
                aiGeneralCommentary, 
                parseError: true 
            };
        }

        if (!parsedResponse || typeof parsedResponse !== 'object') {
            console.warn("ActAIProcessor: Parsed Act metadata response is not a valid object. Value:", parsedResponse);
            if (typeof showToast === 'function') showToast("AI Act metadata response was invalid after parsing.", "warning");
            return { 
                suggestedActSummaryPoints, 
                keyCharacterDevelopments, 
                pacingAndFlowCommentary, 
                aiGeneralCommentary, 
                parseError: true 
            };
        }
        
        // Extract metadata fields based on enhanced `generate_act_metadata.txt` prompt
        let summaryPoints = parsedResponse.suggested_act_summary_points;
        if (Array.isArray(summaryPoints)) {
            suggestedActSummaryPoints = summaryPoints.join("\n• "); // Format as a list
            if (suggestedActSummaryPoints) suggestedActSummaryPoints = "• " + suggestedActSummaryPoints;
        } else if (typeof summaryPoints === 'string') {
            suggestedActSummaryPoints = summaryPoints;
        } else {
            suggestedActSummaryPoints = "N/A";
        }

        // Process character developments (now array of objects)
        let characterDevelopments = parsedResponse.key_character_developments_in_act;
        let characterDevelopmentsText = "N/A";
        if (Array.isArray(characterDevelopments) && characterDevelopments.length > 0) {
            characterDevelopmentsText = characterDevelopments.map(dev => 
                `${dev.character_name} (${dev.development_type}): ${dev.description}`
            ).join("\n• ");
            characterDevelopmentsText = "• " + characterDevelopmentsText;
        }

        // Process conflict analysis (object)
        let conflictAnalysis = parsedResponse.conflict_analysis;
        let conflictAnalysisText = "N/A";
        if (conflictAnalysis && typeof conflictAnalysis === 'object') {
            conflictAnalysisText = `Type: ${conflictAnalysis.primary_conflict_type || 'Unknown'}\n${conflictAnalysis.conflict_description || ''}\nStatus: ${conflictAnalysis.conflict_resolution_status || 'Unknown'}`;
        }

        // Process themes and motifs (array)
        let themesMotifs = parsedResponse.themes_and_motifs;
        let themesMotifsText = "N/A";
        if (Array.isArray(themesMotifs) && themesMotifs.length > 0) {
            themesMotifsText = "• " + themesMotifs.join("\n• ");
        }

        // Process setting utilization (object)
        let settingUtilization = parsedResponse.setting_utilization;
        let settingUtilizationText = "N/A";
        if (settingUtilization && typeof settingUtilization === 'object') {
            settingUtilizationText = `Effectiveness: ${settingUtilization.effectiveness_rating || 'N/A'}/5\n${settingUtilization.description || ''}\nAtmosphere: ${settingUtilization.atmosphere_created || ''}`;
        }

        // Process dialogue assessment (object)
        let dialogueAssessment = parsedResponse.dialogue_assessment;
        let dialogueAssessmentText = "N/A";
        if (dialogueAssessment && typeof dialogueAssessment === 'object') {
            if (dialogueAssessment.dialogue_present) {
                dialogueAssessmentText = `Quality: ${dialogueAssessment.quality_rating || 'N/A'}/5\nVoice Distinction: ${dialogueAssessment.character_voice_distinction || ''}\nPurpose: ${dialogueAssessment.dialogue_purpose || ''}`;
            } else {
                dialogueAssessmentText = "No dialogue present in this act";
            }
        }

        // Process tension and pacing (object)
        let tensionPacing = parsedResponse.tension_and_pacing;
        let tensionPacingText = "N/A";
        if (tensionPacing && typeof tensionPacing === 'object') {
            tensionPacingText = `Rhythm: ${tensionPacing.pacing_rhythm || 'Unknown'}\nTension: ${tensionPacing.tension_trajectory || 'Unknown'}\n${tensionPacing.pacing_commentary || ''}`;
        }

        // Process foreshadowing elements (array)
        let foreshadowing = parsedResponse.foreshadowing_elements;
        let foreshadowingText = "N/A";
        if (Array.isArray(foreshadowing) && foreshadowing.length > 0) {
            foreshadowingText = "• " + foreshadowing.join("\n• ");
        }

        // Process narrative strengths (array)
        let narrativeStrengths = parsedResponse.narrative_strengths;
        let narrativeStrengthsText = "N/A";
        if (Array.isArray(narrativeStrengths) && narrativeStrengths.length > 0) {
            narrativeStrengthsText = "• " + narrativeStrengths.join("\n• ");
        }

        // Process improvement suggestions (array)
        let improvementSuggestions = parsedResponse.improvement_suggestions;
        let improvementSuggestionsText = "N/A";
        if (Array.isArray(improvementSuggestions) && improvementSuggestions.length > 0) {
            improvementSuggestionsText = "• " + improvementSuggestions.join("\n• ");
        }

        return {
            suggestedActSummaryPoints: suggestedActSummaryPoints,
            keyCharacterDevelopments: characterDevelopmentsText,
            conflictAnalysis: conflictAnalysisText,
            themesMotifs: themesMotifsText,
            settingUtilization: settingUtilizationText,
            dialogueAssessment: dialogueAssessmentText,
            tensionPacing: tensionPacingText,
            foreshadowingElements: foreshadowingText,
            narrativeStrengths: narrativeStrengthsText,
            improvementSuggestions: improvementSuggestionsText,
            // Keep legacy fields for backward compatibility
            pacingAndFlowCommentary: tensionPacingText,
            aiGeneralCommentary: "", // No longer used in new format
            parseError: false
        };
    }

    // RAG and Full Prompt processing can be similar to Scene's if the data structure is the same
    function processRagContextMessage(ragData) {
        let summary = "No relevant background information found for Act.";
        let details = "No RAG context details available for this Act generation.";
        // ... (identical logic to SceneAIProcessor.processRagContextMessageForScene)
        if (ragData) {
            if (Array.isArray(ragData) && ragData.length > 0) {
                summary = ragData.map(doc => `Source: ${doc.source_filename || 'N/A'}\nSnippet: ${(doc.text || '').substring(0,100)}...`).join('\n---\n');
                try { details = JSON.stringify(ragData, null, 2); } 
                catch (e) { details = "Error formatting RAG details."; }
            } else if (typeof ragData === 'string' && ragData.trim() !== "") {
                summary = ragData.substring(0, 300) + (ragData.length > 300 ? "..." : "");
                details = ragData; 
            } else if (typeof ragData === 'object' && Object.keys(ragData).length > 0) {
                summary = `Received RAG data object (Act). See details tab.`; 
                try { details = JSON.stringify(ragData, null, 2); } 
                catch (e) { details = "Error formatting RAG object (Act)."; }
            } else if (typeof ragData === 'string' && ragData.trim() === "") {
                summary = "RAG system returned an empty string for Act.";
                details = "RAG system returned an empty string for Act.";
            }
        }
        return { summary, details };
    }

    function processFullPromptMessage(promptData) {
        let details = "Full Act prompt data not available or formatting error from server.";
        // ... (identical logic to SceneAIProcessor.processFullPromptMessageForScene)
        if (promptData && typeof promptData === 'string') {
            details = promptData; 
        } else if (promptData) {
            try { details = JSON.stringify(promptData, null, 2); } 
            catch (e) { details = "Error formatting full Act prompt data."; }
        }
        return { details };
    }

    return {
        // processStreamForDelimiters is removed
        processActMetadataJsonResponse: processActMetadataJsonResponse,
        processRagContextMessage: processRagContextMessage, // Reused
        processFullPromptMessage: processFullPromptMessage  // Reused
    };
})();