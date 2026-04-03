We will create the PG Database

Create a resource Group Called storywriterv2

Let's do everything in CanadaCemtral

![alt text](image.png)


DB created allow access from everywhere



Basics (Change)
Subscription
Azure subscription 1
Resource group
dev_story_writer
Server name
sw2db
Administrator login
adminsw2
Location
Canada Central
Availability zone
No preference
High availability
Not enabled
PostgreSQL version
16
Compute + storage
Burstable, B1ms, 1 vCores, 2 GiB RAM, 32 GiB storage, P4 (120 IOPS)
Backup retention period (in days)
12 day(s)
Storage autogrow
Not enabled
Geo-redundancy
Not enabled
Microsoft Entra administrators
esilver@argentquest.com
Admin Object/App ID:
1ebbcf5f-b29d-4fbc-b8ec-6046cbea5ea0
Networking (Change)
Connectivity method
Public access (allowed IP addresses) and Private endpoint
Allow public access to this resource through the internet using a public IP address
Yes
Allow public access from any Azure service within Azure to this server
No
Firewall rules

Will need to set the firewall rules as well to accept traffic from any 

Server Created

Use DBeaver to connecto the database


sw2db.postgres.database.azure.com
admin login is
adminsw2

new database called devstory2


Copied the Script

Ok Database wqs created

RAN the gen script files

-- Create the user
CREATE USER sw2app WITH PASSWORD '############';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE devstory2 TO sw2app;

-- Grant ownership of all schemas within the database to the user (optional)
ALTER SCHEMA public OWNER TO sw2app;

Moving over the .env


Missing fastapi.middleware.cors 


Restarted VS code and got past of the error

Trying to run the main.py



Something to do with the env

I removed the comment

BACKEND_CORS_ORIGINS=["http://localhost:8000", "http://127.0.0.1:8000"]



Exception has occurred: ValidationError
1 validation error for Settings
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='480 # e.g., 8 hours for local dev', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/int_parsing
  File "C:\Code2025\rag\app\core\config.py", line 95, in <module>
    settings = Settings()
               ^^^^^^^^^^
  File "C:\Code2025\rag\app\main.py", line 10, in <module>
    from core.config import settings
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='480 # e.g., 8 hours for local dev', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/int_parsing


    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 24 * 8, alias="AUTH_ACCESS_TOKEN_EXPIRE_MINUTES") # e.g., 8 days

    change it to     ACCESS_TOKEN_EXPIRE_MINUTES: 30

    did not worked

    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=20# e.g., 8 hours for local dev

    I had to remove the extra space



    I need to run from the root of the project and not app

    uvicorn app.main:app --reload

    from the root


    Next thing 

    Process SpawnProcess-1:
Traceback (most recent call last):
  File "c:\Code2025\rag\.venv\Lib\site-packages\pydantic\networks.py", line 946, in import_email_validator
    import email_validator
ModuleNotFoundError: No module named 'email_validator'

The above exception was the direct cause of the following exception:


Ok a lot of work wasa done to put alll ther folders in the right place
it also missed tine __init__.py files


New Issue 

The error message:

ImportError: cannot import name 'get_db_session' from 'app.db.database' (C:\Code2025\rag\app\db\database.py)
originates in C:\Code2025\rag\app\core\security.py on line 16, which is:

Python

from app.db.database import get_db_session # Assumes this provides an async session
The issue is that the function get_db_session is not defined in app/db/database.py. We defined it in /story_app/app/core/deps.py.

How to fix it:

You need to change the import statement in /story_app/app/core/security.py.

Open the file: C:\Code2025\rag\app\core\security.py
Find the incorrect import line (around line 16):
Python

from app.db.database import get_db_session # Assumes this provides an async session
Change it to correctly import from app.core.deps:
Python

from app.core.deps import get_db_session # Corrected import
Here is the corrected content for /story_app/app/core/security.py

-----------------


  File "c:\Code2025\rag\.venv\Lib\site-packages\fastapi\dependencies\utils.py", line 482, in analyze_param
    ensure_multipart_is_installed()
  File "c:\Code2025\rag\.venv\Lib\site-packages\fastapi\dependencies\utils.py", line 115, in ensure_multipart_is_installed
    raise RuntimeError(multipart_not_installed_error) from None
RuntimeError: Form data requires "python-multipart" to be installed.
You can install "python-multipart" with:

pip install python-multipart

Added to requirements.txt

---------------------------------

    from app.routers import (
  File "C:\Code2025\rag\app\routers\act.py", line 15, in <module>
    from app.models.act import Act
  File "C:\Code2025\rag\app\models\act.py", line 55
    updated_at: Mapped[DateTime] = mapped_column(DateTime(
                                                         ^
SyntaxError: '(' was never closed


The file was mpt complete

Got a new one from Geminie

----------------------------------------------

    from app.schemas import document as schema_document
  File "C:\Code2025\rag\app\schemas\document.py", line 10, in <module>
    from app.models.uploaded_document import DocumentStatus
  File "C:\Code2025\rag\app\models\uploaded_document.py", line 33, in <module>
    class UploadedDocument(Base):
  File "C:\Code2025\rag\app\models\uploaded_document.py", line 61, in UploadedDocument
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
                                                         ^^^^

                                                          # error_message: Stores details if the status is 'ERROR'. Can be null otherwise.
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


# /story_app/app/models/uploaded_document.py

from sqlalchemy import Integer, String, DateTime, ForeignKey, Text # Ensure Text is imported
from sqlalchemy import Enum as SQLAlchemyEnum # Renamed to avoid conflict with Python's enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING
import enum # Use standard Python enum for status values

# --- Core Application Imports ---
# Import the Base class from our database setup.
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .user import User # Import the User model for relationship type hinting

# --- Background: SQLAlchemy ORM Model ---
# This file defines the `UploadedDocument` model using SQLAlchemy's ORM.
# This Python class maps to the `uploaded_documents` table in the PostgreSQL database.
# Its purpose is to track the documents uploaded by users for the Context (Retrieval
# Augmented Generation) system. It stores metadata about the upload, its location
# in Azure Blob Storage, and its processing status for indexing into Azure AI Search.

# Define an Enum for the processing status values
class DocumentStatus(str, enum.Enum): # Inherit from str for easier DB mapping if not using native ENUM
    UPLOADED = "UPLOADED"           # Initial state after successful upload to blob storage
    PENDING = "PENDING_PROCESSING"  # Queued for background processing
    PROCESSING = "PROCESSING"       # Background task is actively processing (parsing, chunking, embedding)
    STORING_CONTEXT = "STORING_CONTEXT"           # Embeddings generated, now indexing into Azure AI Search
    COMPLETED = "COMPLETED"         # Successfully processed and indexed
    ERROR = "ERROR"                 # An error occurred during processing or indexing

class UploadedDocument(Base):
    """
    SQLAlchemy ORM Model representing a document uploaded by a user for Context.
    """
    __tablename__ = "uploaded_documents"

    # --- Table Columns ---

    # id: Primary key for the uploaded_documents table.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # filename: The original filename as uploaded by the user (e.g., "chapter_notes.pdf").
    filename: Mapped[str] = mapped_column(String(255), nullable=False)

    # blob_storage_path: The unique path or name of the file as stored in Azure Blob Storage.
    blob_storage_path: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # status: Tracks the current stage of the document in the Context processing pipeline.
    # Uses the DocumentStatus enum for controlled vocabulary. Indexed for filtering.
    status: Mapped[DocumentStatus] = mapped_column(
        SQLAlchemyEnum(DocumentStatus, name="document_status_enum", create_type=True, native_enum=True), # native_enum=True for PG
        nullable=False,
        default=DocumentStatus.UPLOADED,
        index=True
    )

    # error_message: Stores details if the status is 'ERROR'. Can be null otherwise.
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # uploaded_at: Timestamp when the document was initially uploaded.
    uploaded_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # processed_at: Timestamp when the document processing (including indexing) finished successfully.
    # Can be null if processing hasn't completed or if it resulted in an error.
    processed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # user_id: Foreign key linking this document to the 'id' column in the 'users' table.
    # Each uploaded document must belong to a user.
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # --- Relationships ---

    # owner: Defines the many-to-one relationship from UploadedDocument back to User.
    # - "User": The related model class name.
    # - back_populates="uploaded_documents": Links this relationship to the 'uploaded_documents'
    #   attribute defined in the User model, making it bidirectional. Allows accessing document.owner.
    owner: Mapped["User"] = relationship("User", back_populates="uploaded_documents")

    def __repr__(self):
        """String representation for debugging."""
        # Ensure status.value is used if status is an Enum instance
        status_value = self.status.value if isinstance(self.status, enum.Enum) else self.status
        return f"<UploadedDocument(id={self.id}, filename='{self.filename}', user_id={self.user_id}, status='{status_value}')>"


        Regernated the file
      

======================================

  File "C:\Python311\Lib\importlib\__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "C:\Code2025\rag\app\main.py", line 28, in <module>
    from app.routers import (
  File "C:\Code2025\rag\app\routers\ai_assisted_writing.py", line 12, in <module>
    from app.db.database import get_db_session
ImportError: cannot import name 'get_db_session' from 'app.db.database' (C:\Code2025\rag\app\db\database.py)


You're right, this is the same import issue we encountered earlier, just in a different file!

The error message:

ImportError: cannot import name 'get_db_session' from 'app.db.database' (C:\Code2025\rag\app\db\database.py)
originates in C:\Code2025\rag\app\routers\ai_assisted_writing.py on line 12, which is:

Python

from app.db.database import get_db_session
The function get_db_session is not defined in app/db/database.py. We defined it in /story_app/app/core/deps.py.

How to fix it:

You need to change the import statement in /story_app/app/routers/ai_assisted_writing.py.

Open the file: C:\Code2025\rag\app\routers\ai_assisted_writing.py
Find the incorrect import line (around line 12):
Python

from app.db.database import get_db_session
Change it to correctly import from app.core.deps:
Python

from app.core.deps import get_db_session # Corrected import
Let me provide the corrected content for /story_app/app/routers/ai_assisted_writing.py
File replaced

-------------------------------------

  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "C:\Code2025\rag\app\main.py", line 28, in <module>
    from app.routers import (
  File "C:\Code2025\rag\app\routers\ai_assisted_writing.py", line 23, in <module>
    from app.services.semantic_kernel_setup import (
  File "C:\Code2025\rag\app\services\semantic_kernel_setup.py", line 21, in <module>
    from .plugins.retrieval_plugin import RetrievalPlugin
ModuleNotFoundError: No module named 'app.services.plugins'

You're absolutely right to point this out! The error ModuleNotFoundError: No module named 'app.services.plugins' indicates a mismatch between how we're trying to import the RetrievalPlugin and where it's actually located or if the plugins directory is properly recognized as a package.

Looking back at our file structure plan and the content we generated:

We defined the RetrievalPlugin class inside /story_app/app/services/context_retrieval.py.
In /story_app/app/services/semantic_kernel_setup.py, the import statement is from .plugins.retrieval_plugin import RetrievalPlugin.
This import expects a subdirectory structure like app/services/plugins/retrieval_plugin.py.

We have two ways to fix this:

Adjust the Directory Structure: Create a subdirectory plugins inside app/services/, move context_retrieval.py into it, and rename it to retrieval_plugin.py. Then, make sure app/services/plugins/__init__.py exists (can be empty).
Adjust the Import Statement (Simpler): Change the import statement in semantic_kernel_setup.py to directly import from context_retrieval.py as it's a sibling module within the services package.
Let's go with Option 2 (Adjust the Import Statement) as it's simpler and aligns with the current flat structure within the services directory.

Replace semantic_kernal_setip.py


==================================

  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "C:\Code2025\rag\app\main.py", line 28, in <module>
    from app.routers import (
  File "C:\Code2025\rag\app\routers\views.py", line 52, in <module>
    ) -> Optional[User]:
         ^^^^^^^^
NameError: name 'Optional' is not defined


You've hit another common Python error! The NameError: name 'Optional' is not defined in /story_app/app/routers/views.py means that the Optional type hint was used without being imported from the typing module.

How to fix it:

Open the file: C:\Code2025\rag\app\routers\views.py
Add the import for Optional at the top of the file:
Python

from typing import Optional, List # Add Optional here if List is already imported, or



