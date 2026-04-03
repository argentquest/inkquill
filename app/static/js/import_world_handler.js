// /story_app/app/static/js/import_world_handler.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("ImportWorldHandler: DOMContentLoaded.");

    const importForm = document.getElementById('import-book-form');
    const bookTitleInput = document.getElementById('book_title_import');
    const generateButton = document.getElementById('generate-import-world-button');
    const statusArea = document.getElementById('import-status-area');
    const importedWorldLinkArea = document.getElementById('imported-world-link-area');
    const viewImportedWorldLink = document.getElementById('view-imported-world-link');

    const API_BASE_URL = "/api/v1"; // Ensure this is correct

    if (!importForm || !bookTitleInput || !generateButton || !statusArea || !importedWorldLinkArea || !viewImportedWorldLink) {
        console.error("ImportWorldHandler: One or more critical page elements are missing. Functionality disabled.");
        if (generateButton) generateButton.disabled = true;
        return;
    }

    importForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        console.log("ImportWorldHandler: Form submitted.");

        const bookTitle = bookTitleInput.value.trim();
        if (!bookTitle) {
            if (typeof showToast === 'function') showToast("Please enter a book title.", "warning");
            else alert("Please enter a book title.");
            bookTitleInput.focus();
            return;
        }

        // Update UI for processing state
        generateButton.disabled = true;
        generateButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating & Importing...`;
        statusArea.6A.5.5 0 0 0 12.5 6H12a.5.5 0 0 0-.5.5V8.21a.5.5 0 1 0 1 .007V6.5h.5a.5.5 0 0 0 .354-.854M4.5 6A.5.5 0 0 0 4 6.5V8.21a.5.5 0 1 0 1 .007V6.5H4.5zM2.446 9.854A.5.5 0 0 0 2.5 10H4a.5.5 0 0 0 .5-.5V8.79a.5.5 0 1 0-1-.007V9.5h-.5a.5.5 0 0 0-.354.146M13.561 9.146A.5.5 0 0 0 13.5 9H12a.5.5 0 0 0-.5.5V10.21a.5.5 0 1 0 1 .007V9.5h.5a.5.5 0 0 0 .354-.146"/></svg>
                            Generate & Import World
                        </button>
                    </div>
                </form>

                <div id="import-status-area" class="import-status-area">
                    {# Status messages will appear here via JS #}
                    <p id="import-status-message-text"></p>
                    <a href="#" id="view-imported-world-link" class="btn btn-success btn-sm mt-2" style="display:none;">View Imported World</a>
                </div>

            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
    {{ super() }}
    <script src="{{ url_for('static', path='/js/world_importer_form_handler.js') }}"></script> {# New JS file to be created #}
{% endblock %}
