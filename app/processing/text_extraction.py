"""Background processing helpers for text extraction."""

# /story_app/app/processing/text_extraction.py

import io
import os
import logging
from typing import Optional

# File Parsing Library Imports
try:
    import fitz  # PyMuPDF
    PYMUPDF_INSTALLED = True
except ImportError:
    PYMUPDF_INSTALLED = False
    logging.getLogger(__name__).warning("PyMuPDF (fitz) not installed. PDF processing might be affected.")

try:
    from docx import Document as DocxDocument # python-docx
    DOCX_INSTALLED = True
except ImportError:
    DOCX_INSTALLED = False
    logging.getLogger(__name__).warning("python-docx not installed. DOCX processing might be affected.")

logger = logging.getLogger(__name__)

async def _process_bytes_for_text_extraction(
    file_content_bytes: bytes,
    original_filename_for_ext: str, 
    content_type_hint: Optional[str] = None
) -> Optional[str]:
    """
    Internal helper to extract text from byte content.
    """
    file_extension = os.path.splitext(original_filename_for_ext)[1].lower()
    
    effective_content_type = content_type_hint or ""
    is_pdf = file_extension == ".pdf" or "application/pdf" in effective_content_type
    is_docx = file_extension == ".docx" or "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in effective_content_type
    is_txt = file_extension == ".txt" or "text/plain" in effective_content_type

    try:
        if is_pdf:
            if not PYMUPDF_INSTALLED:
                logger.error(f"Cannot process PDF '{original_filename_for_ext}', PyMuPDF (fitz) is not installed.")
                return None
            logger.debug(f"[TextExtractorHelper] Processing PDF bytes for '{original_filename_for_ext}'...")
            with fitz.open(stream=file_content_bytes, filetype="pdf") as doc:
                full_text = "".join(page.get_text("text") for page in doc)
            logger.info(f"[TextExtractorHelper] Extracted PDF text (length: {len(full_text)}) from '{original_filename_for_ext}'.")
            return full_text
        elif is_docx:
            if not DOCX_INSTALLED:
                logger.error(f"Cannot process DOCX '{original_filename_for_ext}', python-docx is not installed.")
                return None
            logger.debug(f"[TextExtractorHelper] Processing DOCX bytes for '{original_filename_for_ext}'...")
            memory_stream = io.BytesIO(file_content_bytes)
            doc = DocxDocument(memory_stream)
            full_text = "\n".join(para.text for para in doc.paragraphs if para.text)
            logger.info(f"[TextExtractorHelper] Extracted DOCX text (length: {len(full_text)}) from '{original_filename_for_ext}'.")
            return full_text
        elif is_txt:
            logger.debug(f"[TextExtractorHelper] Processing TXT bytes for '{original_filename_for_ext}'...")
            try:
                full_text = file_content_bytes.decode('utf-8')
            except UnicodeDecodeError:
                logger.warning(f"[TextExtractorHelper] Failed to decode '{original_filename_for_ext}' as UTF-8, trying latin-1...")
                full_text = file_content_bytes.decode('latin-1', errors='ignore')
            logger.info(f"[TextExtractorHelper] Extracted TXT text (length: {len(full_text)}) from '{original_filename_for_ext}'.")
            return full_text
        else:
            logger.warning(f"[TextExtractorHelper] Unsupported file type/extension '{file_extension}' or content type '{content_type_hint}' for: {original_filename_for_ext}. Attempting plain text decode.")
            try:
                full_text = file_content_bytes.decode('utf-8', errors='ignore')
                logger.info(f"[TextExtractorHelper] Extracted text via fallback (length: {len(full_text)}) from '{original_filename_for_ext}'.")
                return full_text
            except Exception as e_decode_fallback:
                logger.error(f"[TextExtractorHelper] Error decoding '{original_filename_for_ext}' with fallback: {e_decode_fallback}")
                return None
    except Exception as e_process:
        logger.error(f"[TextExtractorHelper] Error processing bytes for '{original_filename_for_ext}': {e_process}", exc_info=True)
        return None

async def extract_text_from_blob(
    connection_string: Optional[str],
    account_name: Optional[str],
    container_name: str,
    blob_name: str
) -> Optional[str]:
    """
    Reads a document from local storage and extracts its text content.
    """
    from app.core.storage_deps import resolve_storage_path

    logger.info(f"[TextExtractorBlob] Attempting to read and extract text from storage path: {container_name}/{blob_name}")
    try:
        del connection_string
        del account_name
        file_path = resolve_storage_path(container_name, blob_name)
        if not file_path.exists():
            logger.error(f"[TextExtractorBlob] Storage path not found: {file_path}")
            return None
        file_content_bytes = file_path.read_bytes()
        logger.info(f"[TextExtractorBlob] Read {len(file_content_bytes)} bytes from '{file_path}'.")
        return await _process_bytes_for_text_extraction(file_content_bytes, blob_name)
    except Exception as e:
        logger.error(f"[TextExtractorBlob] Failed to extract text from storage path {blob_name}. Error: {e}", exc_info=True)
        return None

async def extract_text_from_file_path(
    file_path: str,
    original_filename: str, 
    content_type: Optional[str] = None 
) -> Optional[str]:
    """
    Reads a local file from the given path and extracts its text content.
    """
    logger.info(f"[TextExtractorPath] Extracting text from local file: '{file_path}', original: '{original_filename}', type: '{content_type}'")
    if not os.path.exists(file_path):
        logger.error(f"[TextExtractorPath] File not found at path: {file_path}")
        return None
    try:
        with open(file_path, "rb") as f:
            file_content_bytes = f.read()
        
        if not file_content_bytes:
            logger.warning(f"[TextExtractorPath] File at '{file_path}' is empty.")
            return ""

        # Use original_filename for extension, content_type as hint to internal helper
        return await _process_bytes_for_text_extraction(file_content_bytes, original_filename, content_type)

    except Exception as e:
        logger.error(f"[TextExtractorPath] Failed to extract text from file {file_path}. Error: {e}", exc_info=True)
        return None

