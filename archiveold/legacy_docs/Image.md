Image Generation Feature - Remaining Work Breakdown
Phase 1: Extend Functionality to Location
Update Database Model (app/models/location.py):
Add current_image_id: Mapped[Optional[int]] as a nullable foreign key to generated_images.id.
Add images: Mapped[List["GeneratedImage"]] one-to-many relationship with the correct primaryjoin condition (element_type=='location').
Add current_image: Mapped[Optional["GeneratedImage"]] one-to-one relationship.
Update Pydantic Schema (app/schemas/location.py):
Add image_url: Optional[str] = None to the LocationRead schema.
Update API Router (app/routers/location.py):
Modify list_locations_in_world to loop through results, create LocationRead objects, and populate the image_url field for each location by calling the _check_and_get_image_url helper.
Modify get_single_location to also populate the image_url field.
Add a new endpoint GET /{location_id}/images to list all GeneratedImage records for a location.
Add a new endpoint POST /{location_id}/set-current-image/{image_id} to update the current_image_id on a location.
**Update UI Template (app/templates/pages/location_form.html):**Excellent
Add the "Appearance & Image Generation" section to the sidebar, mirroring the one in character_form.html.. Now that the Character image generation flow is complete and stable, let
Ensure all id attributes and data-element-type attributes are set correctly for location (e.g., data-element-type="location").
Add's create a detailed work breakdown to implement the same functionality for Locations and Scenes.
This plan will the <script src=".../image_generator.js"></script> tag.
**Update JavaScript mirror the successful pattern we established for Characters, ensuring consistency and reusing as much code as possible.
Work (app/static/js/image_generator.js):
*   [ ] The existing script Breakdown: Complete Image Generation Enhancements**
Use code with caution.
Objective: To extend the existing AI image generation and version management capabilities to is already generic and should work without changes, as it readsdata-element-typeanddata-element-id` from the button. This needs to be tested.
**Phase 2: Extend Functionality to LoreItem**LocationsandScenes`.
Phase 1: Location Image Generation (Mirroring Characters)
**1. Update Database
This phase mirrors Phase 1 exactly.
Update Database Model (app/models/lore_item.py):
Add current_image_id foreign key.
Model (app/models/location.py) - ALREADY DONE**
Task: Add current_image_id foreign key and relationships to GeneratedImage.
Status: ✅ Complete. Add images and current_image relationships with the correct primaryjoin (element_type=='lore_item').
Update Pydantic Schema (app/schemas/lore_item.py):
Add image_url: Optional[str] = None to the `LoreItem We did this when we updated all the models.
**2. Update Pydantic Schemas (app/schemas/location.Read schema.
Update API Router (app/routers/lore_item.py):
Modify list_lore_items_in_world and get_single_lore_item to populate the image_url.
Add GET /{lore_item_id}/imagespy`)**
Task: Add a new optional field image_url: Optional[str] = None to the LocationRead and LocationInStoryRead schemas.
Status: To Do. This endpoint.
Add POST /{lore_item_id}/set-current-image/{image_id} endpoint.
Update UI Template (app/templates/pages/lore_item_form.html):
Add the "Appearance & Image Generation" section to the sidebar.
Ensure id and data- attributes are set correctly for lore_item.
Include the `image_generator allows the API to include the dynamically generated image URL in responses.
3. Update API Router (app/routers/location.py)
Task 1: Modify the list_locations_in_world endpoint.
Inject the blob_service_client.
Loop through the results, convert each Location model to a LocationRead schema, and populate the image_url field using the _check_and_get_image_url helper.
Task 2: Modify the get_single_location endpoint..js` script.
Phase 3: Implement Scene Illustration
This phase is slightly different as it involves the dynamic prompt builder.
Update Database Model (app/models/scene.py):
Add current_image_id foreign key (can be named current_illustration_id for flavor
Inject the blob_service_client.
Populate the image_url field on the returned LocationRead object.
Task 3: Create a new endpoint `GET).
Add images and current_image relationships with primaryjoin (element_type=='scene').
Update Pydantic Schema (app/schemas/scene.py):
Add image_url: Optional[str] = None to the SceneRead schema.
Update API Router (app/routers/scene.py):
Modify list_scenes_for /locations/{location_id}/images to list all GeneratedImage records for a location. This will call a new CRUD function.
Task 4: Create a new endpoint POST /locations/{location_id}/set-current-image/{image_id} to set the active image for a location.
Status: To Do.
4. Update CRUD Module (app/crud/location.py)
Task: Review the update_location function. Ensure it correctly handles updates to image_prompt_definition and image_blob_act and get_single_scene to populate the image_url.
Add GET /{scene_id}/images endpoint.
Add POST /{scene_id}/set-current-image/{image_id} endpoint.
Update UI Template (app/templates/pages/scene_editor_ui.html):
Add a new tab to the AI pane: "Illustration Studio".
Inside this tab, add the UI elements: "Image Style" dropdown, the large prompt textarea, the "Generate_path`.
Status: No significant changes likely needed, but a review is good practice.
5. Update UI Template (app/templates/pages/location_form.html)
Task: Add the "Appearance & Image Generation" sidebar section.
Copy the entire <div class="sidebar-section"> for Scene Illustration" button, the image display area, and the gallery container.
Ensure all id and data- attributes are set for scene.
Create New JavaScript (app/static/js/scene_image_generator.js or similar):
Write a new JS module specifically for the scene editor.
[ image generation from character_form.html.
Change all data-element-type attributes from "character" to "location".
Change all data-element-id attributes to use location.id.
Include the image_generator.js script in the scripts block.
Status: To Do.
6. Update UI List Template (app/templates/pages/location_list_for_world.html)
Task: Modify the card layout to display the generated image.
Copy the {% if location.image_url %} block structure from character_list_for_world.html.
Use ] On tab activation, this script will need to make API calls to fetch the image_prompt_definition for location.image_url as the src for the <img> tag.
Provide a placeholder icon (e.g., fas fa-map-marked-alt) if image_url is not present.
Status: To Do.
Phase 2: Scene Image Illustration
** all characters and the location linked to the scene.
* [ ] Implement the "intelligent prompt builder" logic to construct the draft prompt and pre-fill the textarea.
* [ ] The "Generate" button handler will read from this textarea and the style dropdown, and then call the /api/v1/generate-image/ endpoint (same as1. Update Database Model (app/models/scene.py) - ALREADY DONE**
Task: Add current_image_id (as current_illustration_id) and relationships.
Status: ✅ Complete.
2. Update Pydantic Schemas (app/schemas/scene.py)
the others).
Implement the gallery loading and "Set as Current" functionality, similar to the character version.
Phase 4: Final Database Migration
Generate Migration: Once all model changes from Phases 1-3 are complete, run:
alembic revision --autogenerate -m "Add image generation support for locations, lore, and scenes"
Use code with caution.
Bash
Apply Migration:
alembic upgrade head
Use code with caution.
Bash
This detailed breakdown covers every remaining code change required to fully implement your image generation vision across the entire application.