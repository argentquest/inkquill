# Data Flow Diagrams

This document provides detailed data flow diagrams (DFDs) for key workflows in the AI Storytelling Assistant application. Diagrams are rendered using [Mermaid syntax](https://mermaid.js.org/).

**Note:** To view these diagrams, you will need a Markdown viewer that supports Mermaid rendering (e.g., GitHub, GitLab, VS Code, or an online Mermaid Live Editor). Copy the Mermaid code blocks into a viewer to see the diagram.

---

## 1. User Registration & Login Flow

```mermaid
graph TD
    subgraph Frontend (Browser UI)
        A[User Input: Register/Login Form] --> B(Send Credentials / Request Login)
        D(Receive Auth Success / Cookie) --> E[User Accesses Protected UI]
    end

    subgraph Backend (FastAPI Application)
        B --> F{Auth Router: /auth/register or /auth/login}
        F --> G(Security Module: Hash Password / Create JWT)
        F --> H(User CRUD: Create/Get User)
        G --> I(Set HttpOnly Cookie: access_token)
        H --> J[PostgreSQL: Query/Save User]
        I --> D
    end

    J --- PostgreSQL

    subgraph Dependency Injection Flow
        E --> K(get_current_active_user Dependency)
        K --> L(get_db_session Dependency)
        L --> M[DB Session from Database Module]
        K --> G_prime(Security Module: Decode JWT from Cookie)
        K --> H_prime(User CRUD: Get User by ID/Username)
        M --- PostgreSQL
        H_prime --> J
    end

graph TD
    subgraph Frontend (Browser UI)
        A[User: Upload Document] --> B(Send File & Metadata)
        C(Receive Processing Accepted)
    end

    subgraph Backend (FastAPI Application)
        B --> D{Document Upload Router: /documents/upload}
        D --> E(Read File Content into Memory)
        E --> F(Create UploadedDocument Record in DB: UPLOADED Status)
        F --> G[PostgreSQL: Save UploadedDocument Metadata]
        D --> H(Schedule Background Task: process_uploaded_document_task)
        G --- PostgreSQL
        H --> I(Background Task Worker)
    end

    subgraph Background Processing (process_uploaded_document_task)
        I --> J(Fetch UploadedDocument Record)
        J --> K[PostgreSQL: Get Doc Metadata]
        J --> L(Update Doc Status: PROCESSING_TEXT)
        L --> K

        L --> M(Upload File Content to Azure Blob Storage)
        M --> N(Update Doc Status: PROCESSING_TEXT)
        N --> K
        M --- AzureBlobStorage[Azure Blob Storage]

        N --> O(Extract Text: PDF/DOCX/TXT Helpers)
        O --> P(Update Doc Status: CHUNKING)
        P --> K

        P --> Q(Chunk Text: Fixed Size w/ Overlap)
        Q --> R(Update Doc Status: PREPARING_CONTEXT)
        R --> K

        R --> S(Generate Embeddings: Embedding Service)
        S --> T[Azure OpenAI Service: Embeddings Model]
        S --> U(Update Doc Status: STORING_CONTEXT)
        U --> K
        T --- AzureOpenAI[Azure OpenAI Service]

        U --> V(Prepare Docs for AI Search)
        V --> W(Upload Docs to Azure AI Search)
        W --> X[Azure AI Search: Index]
        W --> Y(Update Doc Status: COMPLETED)
        Y --> K
        X --- AzureAISearch[Azure AI Search]

        Y --> Z(Handle Errors: Set Doc Status to ERROR)
        Z --> K
    end

graph TD
    subgraph Frontend (Browser UI)
        A[User: Input Instruction & Current Content] --> B(Open WebSocket)
        B --> C(Send Auth Ticket & Context)
        C --> D(Send Instruction/Content Message)
        E(Receive Streamed Chunks / Final JSON) --> F[Display AI Output & Controls]
        G(User: Incorporate / Clear / Save) --> H(HTTP Request: Save Content)
    end

    subgraph Backend (FastAPI Application)
        B --> I{WebSocket Router: /ws/.../generate}
        I --> J(get_current_user_from_ws_ticket)
        J --> K(Authentication Service: Validate JWT)
        K --> L[PostgreSQL: Get User]

        I --> M(Fetch Story/Act/Scene Context)
        M --> N[PostgreSQL: Get Context]

        M --> O(Context Retrieval: Semantic Kernel Plugin)
        O --> P(Generate Query Embedding)
        P --> Q[Azure OpenAI Service: Embeddings Model]
        P --> R(Query Azure AI Search with Filter)
        R --> S[Azure AI Search: Index]
        Q --- AzureOpenAI
        S --- AzureAISearch

        O --> T(Prepare LLM Prompt: System + Context + Context + Instruction)
        T --> U(Invoke Semantic Kernel: Generate Content)
        U --> V[Azure OpenAI Service: Chat Model]
        U --> W(Stream/Accumulate Response Chunks)
        V --- AzureOpenAI

        W --> E
        H --> X{Act/Scene Router: PUT /acts/{id} or /scenes/{id}}
        X --> Y(Update Content in DB)
        Y --> Z[PostgreSQL: Save Content]
    end
