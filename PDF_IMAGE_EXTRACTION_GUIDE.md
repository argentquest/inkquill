# PDF Image Extraction Guide

This guide outlines how to extract images from PDF files and store them as documents in the RAG system.

## Overview

The system can automatically extract images from uploaded PDF files using PyMuPDF (fitz) and store them as separate document records in the database. This enables images to be searchable and usable within the storytelling application.

## Prerequisites

- PyMuPDF (fitz) - Already included in dependencies
- PIL (Pillow) - For image processing
- Existing document upload system

## Implementation Steps

### 1. Basic Image Extraction Function

```python
import fitz  # PyMuPDF
import io
import os
from PIL import Image
from datetime import datetime

def extract_images_from_pdf(pdf_path, output_dir):
    """Extract all images from a PDF file"""
    doc = fitz.open(pdf_path)
    image_list = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list_on_page = page.get_images()
        
        for img_index, img in enumerate(image_list_on_page):
            # Get image data
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            
            if pix.n - pix.alpha < 4:  # GRAY or RGB
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # Save image
                filename = f"page_{page_num+1}_img_{img_index+1}.png"
                image_path = os.path.join(output_dir, filename)
                image.save(image_path)
                
                image_list.append({
                    "page": page_num + 1,
                    "index": img_index + 1,
                    "filename": filename,
                    "path": image_path,
                    "size": image.size
                })
            
            pix = None  # Free memory
    
    doc.close()
    return image_list
```

### 2. Database Integration

```python
async def extract_and_store_pdf_images(
    pdf_file_path: str,
    document_id: int,
    user_id: int,
    db: AsyncSession
):
    """Extract images from PDF and store them as documents"""
    
    doc = fitz.open(pdf_file_path)
    extracted_images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                if pix.n - pix.alpha < 4:  # Valid image format
                    # Generate unique filename
                    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                    filename = f"extracted_img_{document_id}_{page_num+1}_{img_index+1}_{timestamp}.png"
                    
                    # Save to storage (adjust path as needed)
                    storage_path = os.path.join("uploads/extracted_images", filename)
                    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
                    
                    # Convert and save
                    img_data = pix.tobytes("png")
                    with open(storage_path, "wb") as f:
                        f.write(img_data)
                    
                    # Get image dimensions
                    image = Image.open(io.BytesIO(img_data))
                    width, height = image.size
                    
                    # Create database record
                    extracted_image = UploadedDocument(
                        filename=filename,
                        original_filename=f"Page {page_num+1} Image {img_index+1}",
                        file_path=storage_path,
                        file_size=len(img_data),
                        mime_type="image/png",
                        user_id=user_id,
                        document_type="EXTRACTED_IMAGE",
                        metadata_json={
                            "source_document_id": document_id,
                            "page_number": page_num + 1,
                            "image_index": img_index + 1,
                            "dimensions": {"width": width, "height": height},
                            "extraction_method": "pymupdf"
                        }
                    )
                    
                    db.add(extracted_image)
                    extracted_images.append(extracted_image)
                
                pix = None  # Free memory
                
            except Exception as e:
                print(f"Error extracting image {img_index} from page {page_num}: {e}")
                continue
    
    doc.close()
    await db.commit()
    return extracted_images
```

### 3. Service Integration

```python
# In your document processing service
async def process_pdf_with_image_extraction(
    file_path: str,
    user_id: int,
    db: AsyncSession,
    extract_images: bool = True
):
    """Process PDF and optionally extract images"""
    
    # Your existing PDF text extraction logic
    text_content = extract_text_from_pdf(file_path)
    
    # Create main document record
    main_document = UploadedDocument(
        # ... your existing fields
    )
    db.add(main_document)
    await db.flush()  # Get the ID
    
    extracted_images = []
    if extract_images:
        # Extract and store images
        extracted_images = await extract_and_store_pdf_images(
            file_path, 
            main_document.id, 
            user_id, 
            db
        )
    
    return {
        "document": main_document,
        "extracted_images": extracted_images,
        "text_content": text_content
    }
```

### 4. API Endpoint

```python
@router.post("/documents/{document_id}/extract-images")
async def extract_images_from_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Extract images from an already uploaded PDF document"""
    
    # Get the document
    document = await db.get(UploadedDocument, document_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.mime_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files supported")
    
    # Extract images
    extracted_images = await extract_and_store_pdf_images(
        document.file_path,
        document_id,
        current_user.id,
        db
    )
    
    return {
        "message": f"Extracted {len(extracted_images)} images",
        "images": [
            {
                "id": img.id,
                "filename": img.filename,
                "page": img.metadata_json.get("page_number"),
                "dimensions": img.metadata_json.get("dimensions")
            }
            for img in extracted_images
        ]
    }
```

### 5. Frontend Integration

```javascript
// Add option to extract images during upload
const extractImages = async (documentId) => {
    const response = await fetch(`/api/documents/${documentId}/extract-images`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to extract images');
    }
    
    const result = await response.json();
    console.log(`Extracted ${result.images.length} images`);
    return result.images;
};

// Usage in upload component
const handleFileUpload = async (file) => {
    // Upload PDF
    const document = await uploadDocument(file);
    
    // Extract images if it's a PDF
    if (file.type === 'application/pdf') {
        const images = await extractImages(document.id);
        console.log('Extracted images:', images);
    }
};
```

## Database Schema Considerations

### UploadedDocument Model Updates

Ensure your `UploadedDocument` model supports:

```python
class UploadedDocument(Base):
    # ... existing fields ...
    
    document_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "EXTRACTED_IMAGE"
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Store extraction metadata
```

### Metadata Structure for Extracted Images

```json
{
    "source_document_id": 123,
    "page_number": 1,
    "image_index": 1,
    "dimensions": {
        "width": 1920,
        "height": 1080
    },
    "extraction_method": "pymupdf",
    "extracted_at": "2025-06-30T10:30:00Z"
}
```

## Configuration Options

### Environment Variables

Add to your `.env` file:

```env
# Image extraction settings
EXTRACT_IMAGES_BY_DEFAULT=true
EXTRACTED_IMAGES_DIR=uploads/extracted_images
MAX_IMAGE_SIZE_MB=10
SUPPORTED_IMAGE_FORMATS=png,jpg,jpeg
```

### Settings Configuration

```python
# In config.py
class Settings:
    # ... existing settings ...
    
    extract_images_by_default: bool = True
    extracted_images_dir: str = "uploads/extracted_images"
    max_image_size_mb: int = 10
    supported_image_formats: list = ["png", "jpg", "jpeg"]
```

## Advanced Features

### 1. Image Quality Filtering

```python
def is_image_worth_extracting(pix, min_width=100, min_height=100):
    """Filter out small or low-quality images"""
    if pix.width < min_width or pix.height < min_height:
        return False
    
    # Check if image is mostly blank/white
    samples = pix.samples
    if len(set(samples)) < 10:  # Very few colors
        return False
    
    return True
```

### 2. Duplicate Image Detection

```python
import hashlib

def get_image_hash(img_data):
    """Generate hash for duplicate detection"""
    return hashlib.md5(img_data).hexdigest()

# In extraction function
img_hash = get_image_hash(img_data)
# Check if hash already exists in database
```

### 3. Background Processing

```python
from app.processing.background_jobs import add_job

async def queue_image_extraction(document_id: int, user_id: int):
    """Queue image extraction as background job"""
    job_data = {
        "document_id": document_id,
        "user_id": user_id,
        "operation": "extract_images"
    }
    
    await add_job("image_extraction", job_data)
```

## Error Handling

### Common Issues and Solutions

1. **Memory Issues**: Large PDFs can consume significant memory
   - Process pages one at a time
   - Free pixmap objects immediately after use
   - Set memory limits

2. **Corrupted Images**: Some PDF images may be corrupted
   - Wrap extraction in try-catch blocks
   - Log errors for debugging
   - Continue processing other images

3. **Storage Space**: Many images can consume disk space
   - Implement cleanup policies
   - Consider cloud storage for large deployments
   - Compress images when appropriate

## Testing

### Unit Tests

```python
def test_extract_images_from_pdf():
    """Test basic image extraction"""
    # Create test PDF with images
    # Run extraction
    # Verify images are extracted correctly
    pass

def test_database_storage():
    """Test that extracted images are stored in database"""
    # Run extraction with database
    # Verify records are created
    # Check metadata is correct
    pass
```

### Integration Tests

```python
async def test_full_extraction_workflow():
    """Test complete extraction workflow"""
    # Upload PDF via API
    # Trigger extraction
    # Verify images are accessible
    # Check file system storage
    pass
```

## Performance Considerations

1. **Large PDFs**: Process in chunks or background jobs
2. **Storage**: Consider implementing image compression
3. **Database**: Index on source_document_id for quick lookups
4. **Memory**: Monitor memory usage during extraction
5. **Concurrent Uploads**: Limit concurrent extractions

## Security Considerations

1. **File Type Validation**: Ensure only safe image formats are saved
2. **User Permissions**: Only allow users to extract from their own documents
3. **Storage Location**: Ensure extracted images are stored securely
4. **File Size Limits**: Prevent extraction of excessively large images

## Deployment Notes

1. Create the `uploads/extracted_images` directory
2. Set appropriate file permissions
3. Configure storage cleanup policies
4. Monitor disk usage
5. Consider CDN for image serving in production

## Future Enhancements

1. **OCR Integration**: Extract text from images using OCR
2. **Image Analysis**: Use AI to analyze and tag images
3. **Thumbnail Generation**: Create thumbnails for quick preview
4. **Vector Embedding**: Generate embeddings for image search
5. **Cloud Storage**: Integrate with AWS S3, Azure Blob, etc.