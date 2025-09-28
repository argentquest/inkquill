# /ai_rag_story_app/app/services/pdf_export_service.py

import io
import re
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
from urllib.request import urlopen

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, gray
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from reportlab.lib import colors
from PIL import Image as PILImage

from app.models.story import Story
from app.models.user import User

logger = logging.getLogger(__name__)


class StoryPDFExporter:
    """Professional PDF export service for stories with images and formatting."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for professional document formatting."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='StoryTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            spaceBefore=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Author style
        self.styles.add(ParagraphStyle(
            name='Author',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_CENTER,
            fontName='Helvetica',
            textColor=gray
        ))
        
        # Story body style
        self.styles.add(ParagraphStyle(
            name='StoryBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            spaceBefore=6,
            alignment=TA_JUSTIFY,
            fontName='Times-Roman',
            leading=18
        ))
        
        # Header style for chapters/sections
        self.styles.add(ParagraphStyle(
            name='StoryHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=18,
            spaceBefore=24,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Metadata style
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica',
            textColor=gray
        ))

    async def export_story_to_pdf(
        self, 
        story: Story, 
        user: User, 
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> bytes:
        """
        Export a story to PDF with professional formatting.
        
        Args:
            story: Story model instance
            user: User who owns the story
            title: Override title (optional)
            content: Override content (optional)
            
        Returns:
            PDF bytes
        """
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create document with custom margins
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,  # 1 inch
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
                title=title or story.title
            )
            
            # Build story content
            story_elements = []
            
            # Add cover page
            await self._add_cover_page(story_elements, story, user, title, content)
            
            # Add page break
            story_elements.append(PageBreak())
            
            # Add story content (use provided content, not story.content which may not exist)
            await self._add_story_content(story_elements, content or "")
            
            # Build PDF
            doc.build(story_elements)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Successfully generated PDF for story {story.id}, size: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating PDF for story {story.id}: {str(e)}")
            raise Exception(f"Failed to generate PDF: {str(e)}")

    async def _add_cover_page(
        self, 
        elements: List[Any], 
        story: Story, 
        user: User,
        title_override: Optional[str] = None,
        content: Optional[str] = None
    ):
        """Add professional cover page with title, author, and cover image."""
        # Add some space at top
        elements.append(Spacer(1, 1*inch))
        
        # Add cover image if available
        if story.image_url:
            try:
                cover_image = await self._process_image_from_url(story.image_url, max_width=4*inch, max_height=3*inch)
                if cover_image:
                    elements.append(cover_image)
                    elements.append(Spacer(1, 0.5*inch))
            except Exception as e:
                logger.warning(f"Could not add cover image: {e}")
        
        # Add title
        title = title_override or story.title or "Untitled Story"
        title_para = Paragraph(self._escape_html(title), self.styles['StoryTitle'])
        elements.append(title_para)
        
        # Add author
        author_name = user.display_name or user.username or "Anonymous"
        author_para = Paragraph(f"by {self._escape_html(author_name)}", self.styles['Author'])
        elements.append(author_para)
        
        # Add metadata
        elements.append(Spacer(1, 1*inch))
        
        # Creation date
        created_date = story.created_at.strftime("%B %d, %Y")
        elements.append(Paragraph(f"Created: {created_date}", self.styles['Metadata']))
        
        # Export date
        export_date = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(f"Exported: {export_date}", self.styles['Metadata']))
        
        # Word count if content is available
        content_for_count = content or ""
        if content_for_count:
            word_count = len(re.findall(r'\b\w+\b', re.sub(r'<[^>]+>', '', content_for_count)))
            elements.append(Paragraph(f"Word Count: {word_count:,} words", self.styles['Metadata']))
        
        # Footer - same as preview modal
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph(
            "This story was created using Ink And Quill - AI-powered storytelling tools for writers.", 
            self.styles['Metadata']
        ))

    async def _add_story_content(self, elements: List[Any], html_content: str):
        """Parse HTML content and add to PDF with proper formatting."""
        if not html_content:
            elements.append(Paragraph("No content available.", self.styles['StoryBody']))
            return
        
        # Parse HTML content and convert to PDF elements
        parsed_content = await self._parse_html_content(html_content)
        
        for element in parsed_content:
            elements.append(element)
        
        # Add story footer (same as preview modal)
        elements.append(Spacer(1, 2*inch))  # More space before footer
        
        # Add horizontal line (similar to preview)
        from reportlab.lib.colors import lightgrey
        from reportlab.platypus import HRFlowable
        elements.append(HRFlowable(width="100%", thickness=1, color=lightgrey, spaceAfter=20))
        
        # Add footer text (same as preview)
        elements.append(Paragraph(
            "This story was created using Ink And Quill - AI-powered storytelling tools for writers.",
            self.styles['Metadata']
        ))

    async def _parse_html_content(self, html_content: str) -> List[Any]:
        """Parse HTML content from Quill editor and convert to ReportLab elements."""
        elements = []
        
        # Remove HTML tags and split into paragraphs
        # This is a simplified parser - you might want to use BeautifulSoup for complex HTML
        content = html_content.strip()
        
        # Handle images first
        image_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        images = re.findall(image_pattern, content)
        
        # Split content by paragraphs (basic HTML parsing)
        paragraphs = re.split(r'</?p[^>]*>', content)
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue
                
            # Check if this paragraph contains an image
            if '<img' in para:
                # Extract and add images
                for img_url in re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', para):
                    try:
                        image = await self._process_image_from_url(img_url, max_width=5*inch, max_height=4*inch)
                        if image:
                            elements.append(Spacer(1, 12))
                            elements.append(image)
                            elements.append(Spacer(1, 12))
                    except Exception as e:
                        logger.warning(f"Could not add image {img_url}: {e}")
                
                # Remove image tags from text
                para = re.sub(r'<img[^>]*>', '', para)
            
            # Clean remaining HTML tags
            para = re.sub(r'<[^>]+>', '', para).strip()
            
            if para:
                # Handle different text formatting
                if para.startswith('Chapter ') or para.startswith('# '):
                    # Treat as header
                    elements.append(Paragraph(self._escape_html(para), self.styles['StoryHeader']))
                else:
                    # Regular paragraph
                    elements.append(Paragraph(self._escape_html(para), self.styles['StoryBody']))
                    elements.append(Spacer(1, 6))
        
        return elements

    async def _process_image_from_url(self, url: str, max_width: float, max_height: float) -> Optional[Image]:
        """Download and process image from URL for PDF inclusion."""
        try:
            # Check if it's a valid URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                logger.warning(f"Invalid image URL: {url}")
                return None
            
            # Download image
            with urlopen(url) as response:
                image_data = response.read()
            
            # Create ReportLab Image
            image_buffer = io.BytesIO(image_data)
            
            # Open with PIL to get dimensions
            pil_image = PILImage.open(image_buffer)
            original_width, original_height = pil_image.size
            
            # Calculate scaling to fit within max dimensions
            width_scale = max_width / original_width
            height_scale = max_height / original_height
            scale = min(width_scale, height_scale, 1.0)  # Don't upscale
            
            final_width = original_width * scale
            final_height = original_height * scale
            
            # Reset buffer position
            image_buffer.seek(0)
            
            # Create ReportLab image
            rl_image = Image(image_buffer, width=final_width, height=final_height)
            return rl_image
            
        except Exception as e:
            logger.warning(f"Could not process image from {url}: {e}")
            return None

    def _escape_html(self, text: str) -> str:
        """Escape HTML entities for ReportLab."""
        if not text:
            return ""
        
        # Basic HTML escaping
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        return text


# Global service instance
pdf_export_service = StoryPDFExporter()