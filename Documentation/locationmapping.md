# Design & Architecture Specification: Advanced World-Building System
**Project:** AI Storytelling Assistant
**Version:** 1.1
**Date:** {{ currentDate }}

## 1. Overview & Guiding Philosophy

This document outlines the design and technical specification for an advanced world-building system. The primary goal is to create a flexible tool that caters to two distinct user personas: the **Storyteller** and the **World-Builder (Dungeon Master)**.

The core philosophy is **optional complexity**. The system must be simple for users focused on narrative, while providing deep, granular tools for users who require detailed spatial and mechanical design.

## 2. Core Concepts & User Requirements

### 2.1. The Unified `Location` Entity

A `Location` is the fundamental building block of a world, representing anything from a continent to a small object.

*   **Storyteller Requirement:** Must be able to create a location with just a `Name`.
*   **DM Requirement:** Can optionally specify a location's scale, hierarchy, physical dimensions, and map coordinates.

### 2.2. Location Hierarchy (Containment)

This represents the "is inside of" relationship. A location can have **only one parent**, creating a strict tree structure.

*   **Storyteller Requirement:** Can optionally place a location inside another for basic organization.
*   **DM Requirement:** Can create deep, multi-level hierarchies (e.g., Room -> Building -> City).

### 2.3. Location Connectivity (Paths)

This represents the "is connected to" relationship, defining paths and adjacencies between any two locations, regardless of their hierarchy.

*   **Storyteller & DM Requirement (Core):** Must be able to create a link between two locations and provide a **`Description`** for that connection. This is the primary way to describe the edge (e.g., "a treacherous mountain pass," "a shimmering one-way portal," "a locked sewer grate").
*   **DM Requirement (Advanced/Optional):** Can specify if a connection is `one-way` or `two-way` and add private `DM Notes` (e.g., travel time, skill checks).

### 2.4. Mapping & Visualization

A visual representation of the world's locations and their relationships.

*   **Storyteller Requirement (Default View):** An abstract **Node Graph** that automatically arranges locations to clearly show their connections.
*   **DM Requirement (Advanced Mode):** The ability to toggle a **Grid View** and assign optional `(x, y, z)` coordinates to locations, which "snaps" them to the grid.

### 2.5. Element Placement (Instancing)

This defines the location of other world elements (`Characters`, `LoreItems`).

*   **Storyteller & DM Requirement (Core):** Can optionally place a Character or Lore Item at a specific `Location`.
*   **DM Requirement (Advanced/Optional):** Can add a descriptive `Placement Note` explaining *how* the element is situated (e.g., "The sword is embedded in a stone altar").

---

## 3. Technical Specification: Database Schema

### 3.1. `locations` Table
Augmented with nullable columns: `scale`, `parent_location_id`, `map_x`, `map_y`, `map_z`, `dimension_x`, `dimension_y`, `dimension_z`, `dimension_unit`.

### 3.2. `characters` & `lore_items` Tables
Augmented with nullable columns: `current_location_id` and `placement_note`.

### 3.3. `location_connections` Table (New Table)
This table defines the connection graph. The `description` field is the primary mechanism for describing the edge.

| Column Name | Data Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `from_location_id`| INTEGER | | **Required.** Foreign Key to `locations.id`. |
| `to_location_id` | INTEGER | | **Required.** Foreign Key to `locations.id`. |
| `description` | TEXT | NULL | **Required/Optional.** A user-facing description of the path or edge itself. |
| `is_bidirectional`| BOOLEAN | `True` | **Required.** Defines if the path is one-way or two-way. |
| `dm_notes` | TEXT | NULL | **Optional.** Private notes for the World-Builder. |

*(Primary Key will be `(from_location_id, to_location_id)`)*

### 3.4. `ENUM` Types
*   **`location_scale_enum`**: `(REGION, CITY, BUILDING, ROOM, AREA, OBJECT, OTHER)`

---

## 4. Technical Specification: UI/UX Implementation

### 4.1. Location, Character, & Lore Item Forms
*   Forms will be updated with new optional fields (e.g., `Scale`, `Parent Location`, `Coordinates`, `Dimensions`, `Current Location`). These advanced fields will be placed in collapsible "Advanced" sections to keep the primary view simple.

### 4.2. World Map View (`world_map_view.html`)
*   **Library:** The `Vis.js Network` library will be used.
*   **Rendering Logic:**
    *   Locations are rendered as nodes. Nodes with `x,y` coordinates are fixed; others are positioned by the physics engine.
    *   Connections from the `location_connections` table are rendered as edges.
*   **Interactivity & Describing the Edge:**
    *   An **"Add Connection"** button will open a modal. This modal will contain:
        1.  A "From Location" dropdown.
        2.  A "To Location" dropdown.
        3.  A **`Path Description`** text field (maps to the `description` column). This is where the user describes the edge.
        4.  A "Two-Way Path" checkbox (maps to `is_bidirectional`).
        5.  An optional "DM Notes" textarea.
    *   On the map, the `Path Description` will appear as a **label on the connecting line** between the two nodes.
    *   Clicking an existing edge will open the same modal, pre-filled with the connection's data, allowing the user to edit the description or other properties.

This revised plan explicitly elevates the **edge description** to a core, user-facing feature in both the data model and the user interface, directly addressing your excellent question.