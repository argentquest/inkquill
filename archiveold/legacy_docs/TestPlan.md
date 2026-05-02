# AI Storytelling Assistant - QA Test & Validation Plan

**Document Version:** 1.2
**Date:** {{ currentDate }}
**Objective:** To provide a comprehensive set of test cases for validating the functionality, usability, and security of the AI Storytelling Assistant application on desktop browsers.

### **Revision History**

| Version | Date          | Author(s)         | Summary of Changes                                                              |
| :------ | :------------ | :---------------- | :------------------------------------------------------------------------------ |
| 1.0     | {{ date - 2 }}    | AI Assistant      | Initial generation of the full test plan.                                       |
| 1.1     | {{ date - 1 }}    | AI Assistant      | Refined scope based on user feedback: desktop-only focus, no performance tests, toast notifications as primary feedback. |
| 1.2     | {{ currentDate }} | AI Assistant      | Added Revision History table and a `Result (Pass/Fail/Skip)` column to all test case tables for execution tracking. |

### **Testing Scope & Environment**

*   **Environment:** Staging/QA environment mirroring production configuration.
*   **Target Platform:** Desktop Browsers.
*   **Supported Browsers:** Latest versions of Chrome, Firefox, and Edge.
*   **User Roles:** Standard Authenticated User. Admin functionality is out of scope.
*   **Performance Testing:** Out of scope for this plan.
*   **Feedback Mechanism:** Success and error messages should primarily be delivered via on-screen toast notifications.

---

### **1. Authentication & User Management**

| Test Case ID | Feature | Test Scenario | Test Steps | Expected Result | Result (Pass/Fail/Skip) |
| :--- | :--- | :--- | :--- | :--- |:--- |
| **AUTH-01** | Registration | Successful registration with valid data | 1. Navigate to `/ui/register`.<br>2. Fill in a unique username, valid password, and confirm password.<br>3. Click "Register". | A success toast appears indicating the account is pending approval. The user is redirected to the login page. | |
| **AUTH-02** | Registration | Attempt registration with an existing username | 1. Navigate to `/ui/register`.<br>2. Use a username that is already in the database.<br>3. Click "Register". | An error message "Username already registered" is displayed on the form. No new user is created. | |
| **AUTH-03** | Registration | Password mismatch | 1. Navigate to `/ui/register`.<br>2. Fill in valid data, but make "Password" and "Confirm Password" different.<br>3. Click "Register". | A client-side error message "Passwords do not match" is displayed on the form. | |
| **AUTH-04** | Login | Successful login with valid credentials | 1. Navigate to `/ui/login`.<br>2. Enter the username and password for an active user.<br>3. Click "Login". | The user is redirected to the `/ui/stories` page. An `access_token` cookie is set in the browser. | |
| **AUTH-05** | Login | Failed login with incorrect password | 1. Navigate to `/ui/login`.<br>2. Enter a valid username and an incorrect password.<br>3. Click "Login". | An error message "Incorrect username or password" is displayed. The user remains on the login page. | |
| **AUTH-06** | Login | Failed login for an inactive user | 1. Manually set a user's `is_active` flag to `false` in the database.<br>2. Attempt to log in with that user's credentials. | An error message "Inactive user account" is displayed. Login is blocked. | |
| **AUTH-07** | Logout | User successfully logs out | 1. Log in as any user.<br>2. From the sidebar, click the user menu, then "Logout". | The `access_token` cookie is cleared from the browser. The user is redirected to the home page (`/ui/`). | |
| **AUTH-08** | Session | Accessing a protected page while logged out | 1. Ensure you are logged out.<br>2. Attempt to navigate directly to `/ui/stories`. | The user is redirected to the `/ui/login` page. | |

---

### **2. World Management (CRUD)**

| Test Case ID | Feature | Test Scenario | Test Steps | Expected Result | Result (Pass/Fail/Skip) |
| :--- | :--- | :--- | :--- | :--- |:--- |
| **WRD-01** | Create World | User creates a new world successfully | 1. Navigate to `/ui/worlds`.<br>2. Click "Create World" -> "Create New World".<br>3. Enter a name and description.<br>4. Click "Create World". | User is redirected to the new world's detail page (`/ui/worlds/{id}`). A success toast is shown. | |
| **WRD-02** | Read World | View the list of all created worlds | 1. Create several worlds.<br>2. Navigate to `/ui/worlds`. | All created worlds are listed correctly with their names and descriptions. | |
| **WRD-03** | Update World | User edits an existing world's details | 1. From a world's detail page, click "Edit Details".<br>2. Change the name and description.<br>3. Click "Save Changes". | User is redirected back to the world's detail page, which now shows the updated information. A success toast is shown. | |
| **WRD-04** | Delete World | User deletes a world with no stories | 1. Create a new world.<br>2. From the worlds list, click the "Delete" button for that world.<br>3. Confirm the deletion. | The world is removed from the list. A success toast appears. | |
| **WRD-05** | Delete World | User attempts to delete a world that has stories | 1. Create a world and a story within it.<br>2. From the worlds list, click "Delete" for that world.<br>3. Confirm deletion. | An error toast appears stating the world cannot be deleted because it's associated with stories. The world is not deleted. | |

---

### **3. World Element Management (Characters, Locations, Lore)**

*(This section is a template for Characters, Locations, and Lore Items)*

| Test Case ID | Feature | Test Scenario | Test Steps | Expected Result | Result (Pass/Fail/Skip) |
| :--- | :--- | :--- | :--- | :--- |:--- |
| **ELEM-01** | Create Element | User creates a new element (e.g., Character) in a world | 1. Navigate to a world's detail page.<br>2. Click "Add New Character".<br>3. Fill in the required fields.<br>4. Click "Create Character". | The user is redirected to the element's edit page. A success toast is shown. | |
| **ELEM-02** | Update Element | User edits an existing element | 1. From the element list, click "Edit".<br>2. Change several fields.<br>3. Click "Save Changes". | The form saves, and a success toast appears. The Context content display shows "Loading..." and updates after a few seconds. | |
| **ELEM-03** | Delete Element | User deletes an element | 1. From the element list, click "Delete".<br>2. Confirm the deletion. | The element is removed from the list. A success toast appears. | |

---

### **4. Story & Act Management (CRUD & Linking)**

| Test Case ID | Feature | Test Scenario | Test Steps | Expected Result | Result (Pass/Fail/Skip) |
| :--- | :--- | :--- | :--- | :--- |:--- |
| **STY-01** | Create Story | User creates a story and links it to a world | 1. Navigate to `/ui/stories/new`.<br>2. Select a world from the dropdown.<br>3. Enter a title.<br>4. Click "Create Story". | The user is redirected to the new story's detail page (`/ui/stories/{id}`). | |
| **ACT-01** | Link/Unlink | Link and unlink world elements to a story | 1. On a story detail page, click "Link Character".<br>2. Select a character and add a role. Click "Link".<br>3. Verify the character appears in the list.<br>4. Click the "Unlink" (trash icon) button for that character. | The character appears in the list with its role after linking. It is removed from the list after unlinking. A success toast appears for each action. | |
| **ACT-02** | Generate Scenes | User generates scenes from Act content | 1. Navigate to a Story Detail page.<br>2. Find an Act card with content.<br>3. Click "Generate Scenes". | A success toast "Scene generation started!" appears. After a few seconds, the scene list under the act populates with new scene cards. | |

---

### **5. AI-Assisted Writing: Act & Scene Editors**

| Test Case ID | Feature | Test Scenario | Test Steps | Expected Result | Result (Pass/Fail/Skip) |
| :--- | :--- | :--- | :--- | :--- |:--- |
| **AI-EDIT-01**| Connection | WebSocket connects successfully | 1. Navigate to an Act or Scene Editor page.<br>2. Observe the UI/toast notifications. | A "AI Assistant connected" toast message appears. The "Generate" button is enabled. | |
| **AI-EDIT-02**| Generation | Append text to an empty editor | 1. In an editor, ensure the main content is empty.<br>2. In the AI Assistant, type "Start the story..."<br>3. Click "Generate". | The AI streams text into the preview box. After it finishes, click "Incorporate". The generated text is added to the main editor. | |
| **AI-EDIT-03**| Generation | Rewrite highlighted text | 1. In the editor, write "The cat sat."<br>2. Highlight that sentence.<br>3. In the AI Assistant, select "Rewrite" mode and type "Make this more poetic."<br>4. Click "Generate", then "Incorporate". | The original sentence is replaced by a more poetic version from the AI. | |
| **AI-EDIT-04**| UI State | Controls disable/enable during generation | 1. Click "Generate".<br>2. Immediately try to click "Generate", "Incorporate", and "Clear". | The "Generate" button is disabled. "Incorporate" and "Clear" are disabled until the stream finishes. They enable correctly after completion. | |
| **AI-EDIT-05**| Context Context | Context context is displayed | 1. Upload a document with specific lore.<br>2. Go to an editor for a story in the same world.<br>3. Type an instruction referencing the lore.<br>4. Click "Generate". | The Context Details tab is populated with the relevant snippet from the document before the AI begins writing. | |

---

### **6. AI Review & Analysis**

| Test Case ID | Feature | Test Scenario | Test Steps | Expected Result | Result (Pass/Fail/Skip) |
| :--- | :--- | :--- | :--- | :--- |:--- |
| **AI-REV-01** | Full Review | Generate a review for a well-formed act | 1. Navigate to the "Review with AI" page for an act with substantial content.<br>2. Click "Get AI Review". | A success toast appears. The "Suggestions" and "Metrics" tabs are populated with relevant, structured feedback. | |
| **AI-REV-02** | Apply Suggestion | User applies a text replacement suggestion | 1. Generate a review.<br>2. Find a suggestion with a "Proposed Solution" and an "Apply" button.<br>3. Click "Apply". | The text in the main editor is updated to match the proposed solution. The "Apply" button becomes "Applied" and is disabled. A success toast appears. | |
| **AI-REV-03** | Error Handling | AI returns invalid data | 1. (Requires mocking) Simulate an API response that is not valid JSON.<br>2. Click "Get AI Review". | An error toast appears: "Error understanding AI's structured Act metadata." The UI does not crash. | |
| **AI-REV-04** | Timeout | AI call takes too long | 1. (Requires mocking) Simulate a long-running API call.<br>2. Click "Get AI Review". | The UI remains responsive. After a reasonable timeout, an error toast should appear indicating the request timed out. | |

---

### **7. Context System & Document Management**

| Test Case ID | Feature | Test Scenario | Test Steps | Expected Result | Result (Pass/Fail/Skip) |
| :--- | :--- | :--- | :--- | :--- |:--- |
| **Context-01** | Upload | User uploads a valid document | 1. Navigate to `/ui/documents`.<br>2. Select a valid PDF, TXT, or DOCX file.<br>3. Click "Upload". | A success toast "Document submitted successfully!" appears. The page reloads, and the new document is in the list with a "Pending" or "Processing" status. | |
| **Context-02** | Upload | User attempts to upload an invalid file type | 1. On the document manager, select a `.jpg` or `.zip` file.<br>2. Attempt to upload. | The server returns a `400 Bad Request` error, and an error toast is displayed. | |
| **Context-03** | Deletion | User deletes a document record | 1. From the document list, click "Delete" on a document.<br>2. Confirm the deletion. | The row is removed from the table. A success toast appears. | |

---

### **8. Advanced Import Features**

| Test Case ID | Feature | Test Scenario | Test Steps | Expected Result | Result (Pass/Fail/Skip) |
| :--- | :--- | :--- | :--- | :--- |:--- |
| **IMP-01** | Import by Title | User imports a world from a known book title | 1. Navigate to "My Worlds" -> "Create World" -> "Import from Book".<br>2. Enter "Alice's Adventures in Wonderland".<br>3. Click "Generate & Import". | A job status area appears and updates. On completion, a link to the new world appears. A success toast is shown. | |
| **IMP-02** | Import from Doc| User creates a world from a document | 1. Navigate to "My Worlds" -> "Create World" -> "Create from Document".<br>2. Enter a name and upload a document.<br>3. Click "Analyze & Create". | A job status area appears and updates. On completion, a link to the new world appears. A success toast is shown. | |

---

### **9. Authorization & Security**

| Test Case ID | Feature | Test Scenario | Test Steps | Expected Result | Result (Pass/Fail/Skip) |
| :--- | :--- | :--- | :--- | :--- |:--- |
| **SEC-01** | Cross-User Access| User A attempts to view User B's story via URL | 1. Log in as User A, note a story ID.<br>2. Log out and log in as User B.<br>3. Attempt to navigate directly to User A's story URL (`/ui/stories/{id}`). | A "Not Found" or "Forbidden" error page is displayed. The content is not shown. | |
| **SEC-02** | XSS Prevention | User enters script tags into a form field | 1. Create a new story.<br>2. For the title, enter `<script>alert('xss')</script>`.<br>3. Save the story. | The title is displayed on the story list page as the literal text `<script>alert('xss')</script>`. No JavaScript alert is triggered. | |

---

### **10. General UI/UX**

| Test Case ID | Feature | Test Scenario | Test Steps | Expected Result | Result (Pass/Fail/Skip) |
| :--- | :--- | :--- | :--- | :--- |:--- |
| **UI-01** | Navigation | Sidebar navigation works as expected | 1. Click the hamburger menu to open the sidebar.<br>2. Click a navigation link (e.g., "My Worlds").<br>3. Click the overlay to close the sidebar. | The sidebar opens, navigation works, and clicking the overlay closes it. State is consistent. | |
| **UI-02** | Tooltips | Verify tooltips on buttons | 1. Hover the mouse over various buttons with tooltips (e.g., Save, Delete, Publish). | A helpful tooltip appears describing the button's action. | |
| **UI-03** | Breadcrumbs | Verify breadcrumb navigation | 1. Navigate from "My Stories" -> a specific story -> an act editor.<br>2. Click the links in the breadcrumb trail. | Each link in the breadcrumb trail correctly navigates back to the corresponding parent page. | |
