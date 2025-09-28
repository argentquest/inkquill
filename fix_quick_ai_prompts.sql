-- Fix the new QUICK_AI prompts to include proper {text} and {context_summary} placeholders

UPDATE prompts SET prompt_content = 'Transform any passive voice constructions in the following text to active voice. Make the writing more direct and engaging while preserving the original meaning and tone:

{text}

Context: {context_summary}' WHERE title = 'Convert to Active Voice' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Enhance the following text by adding vivid sensory details (sight, sound, smell, taste, touch) to make the scene more immersive and engaging for readers:

{text}

Context: {context_summary}' WHERE title = 'Add Sensory Details' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Create a concise 2-3 sentence summary of the following text that captures the main events, character developments, or key points:

{text}

Context: {context_summary}' WHERE title = 'Create Chapter Summary' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Improve the flow between sentences and paragraphs in the following text by adding better transitions and connecting phrases. Make the text read more smoothly:

{text}

Context: {context_summary}' WHERE title = 'Improve Flow and Transitions' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Rewrite the following text from a first-person perspective, changing pronouns and adjusting the narrative voice while maintaining the story content:

{text}

Context: {context_summary}' WHERE title = 'Convert to First Person' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Rewrite the following text from a third-person perspective, changing pronouns and adjusting the narrative voice while maintaining the story content:

{text}

Context: {context_summary}' WHERE title = 'Convert to Third Person' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Subtly add hints or foreshadowing elements to the following text that suggest future events or developments in the story without being too obvious:

{text}

Context: {context_summary}' WHERE title = 'Add Foreshadowing' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Adjust the pacing of the following text - speed up slow sections and slow down rushed parts to create better narrative rhythm and reader engagement:

{text}

Context: {context_summary}' WHERE title = 'Improve Pacing' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Increase the dramatic tension in the following text by adding or emphasizing conflict, stakes, or uncertainty to make it more engaging:

{text}

Context: {context_summary}' WHERE title = 'Add Tension and Conflict' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Transform the ending of the following text into a compelling hook or cliffhanger that will make readers want to continue to the next section:

{text}

Context: {context_summary}' WHERE title = 'Create Hook or Cliffhanger' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Enhance the character voice in the following text to make it more distinctive, consistent, and true to the character''s personality and background:

{text}

Context: {context_summary}' WHERE title = 'Strengthen Character Voice' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Add subtle subtext to dialogue and interactions in the following text - what characters really mean beneath what they''re saying on the surface:

{text}

Context: {context_summary}' WHERE title = 'Add Subtext' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Update outdated or archaic language in the following text to make it more accessible to modern readers while preserving the intended tone and meaning:

{text}

Context: {context_summary}' WHERE title = 'Modernize Language' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Improve the readability of the following text by adding appropriate paragraph breaks and reformatting for better visual flow and reading experience:

{text}

Context: {context_summary}' WHERE title = 'Add Paragraph Breaks' AND prompt_type = 'QUICK_AI';

UPDATE prompts SET prompt_content = 'Eliminate repetitive phrases, redundant information, and unnecessary words from the following text while preserving all essential meaning and impact:

{text}

Context: {context_summary}' WHERE title = 'Remove Redundancy' AND prompt_type = 'QUICK_AI';