// /story_app/app/static/js/utils.js
"use strict";

/**
 * A collection of globally accessible utility functions.
 * This file should be included in base.html before other scripts that use these functions.
 */

/**
 * Escapes potentially unsafe HTML characters to prevent XSS when inserting text content into the DOM.
 * @param {any} unsafe - The input value to escape. If not a string, it will be converted.
 * @returns {string} The escaped string, safe for insertion as text content.
 */
function escapeHtml(unsafe) {
    if (unsafe === null || typeof unsafe === 'undefined') {
        return '';
    }
    return String(unsafe)
         .replace(/&/g, "&")
         .replace(/</g, "<")
         .replace(/>/g, ">")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#39;");
}
