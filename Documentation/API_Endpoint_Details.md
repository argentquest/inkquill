# API Endpoint Detailed Design

This document provides in-depth information about key API endpoints within the application, outlining their purpose, expected behavior, and internal dependencies.

**Note:** For full schema definitions, please refer to the OpenAPI documentation available at `/docs` when the application is running, and the Pydantic schema files in `app/schemas/`.

---

## 1. Asynchronous Job Endpoints

These endpoints initiate long-running background tasks and provide a mechanism for tracking their progress. The frontend is expected to use the returned `job_id` to poll the status endpoint.

### `POST /api/v1/documents/upload`

*   **Description:** Accepts a user's document (PDF, TXT, DOCX) for RAG processing. It creates database records for the document and a new tracking job, then schedules a background task for the ingestion pipeline (text extraction, chunking, embedding, and indexing).
*   **Request Method:** `POST`
*   **Request Body:** `multipart/form-data`
    *   `file` (`UploadFile`): The document file.
    *   `world_id` (`Optional[int]`, Form Field): The ID of an existing World to associate this document with.
*   **Response Body:** `JobSubmissionResponse` schema (`application/json`)
    *   `message` (`str`): A confirmation message.
    *   `job_id` (`str`): A unique ID for the background job that can be used for polling.
*   **Success Status:** `202 Accepted`
*   **Authentication:** Required.

### `POST /api/v1/worlds/import-from-book-title`

*   **Description:** Initiates a background job to generate a new World from a book title using an LLM. The job will create the world, extract characters, locations, and lore, and then trigger RAG indexing for each new element.
*   **Request Method:** `POST`
*   **Request Body:** `BookTitleImportRequest` schema (`application/json`)
    *   `book_title` (`str`): The title of the book to import.
*   **Response Body:** `JobSubmissionResponse` schema (`application/json`)
*   **Success Status:** `202 Accepted`
*   **Authentication:** Required.

### `POST /api/v1/worlds/import/create-from-document`

*   **Description:** Initiates a background job to create a new World by analyzing a user-uploaded document. The job will create the world with the given name, extract characters, locations, and lore from the document text, and trigger RAG indexing for each new element.
*   **Request Method:** `POST`
*   **Request Body:** `multipart/form-data`
    *   `world_name` (`str`, Form Field): The name for the new world to be created.
    *   `file` (`UploadFile`): The document to analyze.
*   **Response Body:** `JobSubmissionResponse` schema (`application/json`)
*   **Success Status:** `202 Accepted`
*   **Authentication:** Required.

### `GET /api/v1/worlds/import/job-status/{job_id}`

*   **Description:** Allows the frontend to poll for the status of a long-running background job initiated by one of the endpoints above.
*   **Request Method:** `GET`
*   **Path Parameters:**
    *   `job_id` (`str`): The unique ID of the job, returned from the initial POST request.
*   **Response Body:** `JobStatusRead` schema (`application/json`)
*   **Success Status:** `200 OK`
*   **Error Statuses:** `404 Not Found` if the job ID doesn't exist or doesn't belong to the user.
*   **Authentication:** Required.

---

## 2. World Management Endpoints

### `POST /api/v1/worlds/`

*   **Description:** Creates a new, empty fictional World owned by the authenticated user.
*   **Request Body:** `WorldCreate` schema (`application/json`)
*   **Response Body:** `WorldRead` schema (HTTP 201)
*   **Success Status:** `201 Created`
*   **Authentication:** Required.

### `DELETE /api/v1/worlds/{world_id}`

*   **Description:** Deletes a specific World owned by the user. The application logic first checks if the World is associated with any Stories. If so, it returns a `409 Conflict` error to prevent accidental data loss. If not, it proceeds with the deletion, which cascades to all `Character`, `Location`, and `LoreItem` records within that World.
*   **Request Method:** `DELETE`
*   **Success Status:** `204 No Content`
*   **Error Statuses:** `409 Conflict` if stories are linked.
*   **Authentication:** Required.
*   **Authorization:** User must own the `world_id`.

---

## 3. WebSocket Authentication

### `GET /api/v1/auth/ws-ticket`

*   **Description:** Provides a short-lived (e.g., 5 minutes) JSON Web Token (JWT) used to authenticate a WebSocket connection. The client must request this ticket via a standard authenticated HTTP call and then pass the ticket as a query parameter when opening the WebSocket URL.
*   **Request Method:** `GET`
*   **Response Body:** `WSTicketResponse` schema (`application/json`)
*   **Success Status:** `200 OK`
*   **Authentication:** Required (via standard HTTP-only cookie).