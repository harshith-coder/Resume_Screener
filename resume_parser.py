import io
import tempfile
import os
import logging
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document

try:
    from pyresparser import ResumeParser
except Exception:
    ResumeParser = None

try:
    from pdf2image import convert_from_bytes
    import pytesseract
except Exception:
    convert_from_bytes = None
    pytesseract = None


logger = logging.getLogger(__name__)


def _ocr_pdf_bytes(data, max_pages=10, dpi=200):
    """Perform OCR on PDF bytes and return extracted text.

    If dependencies are missing or an error occurs, returns empty string.
    """
    if convert_from_bytes is None or pytesseract is None:
        logger.debug("OCR dependencies not available")
        return ""
    try:
        images = convert_from_bytes(data, dpi=dpi)
        texts = []
        for i, img in enumerate(images):
            if i >= max_pages:
                break
            texts.append(pytesseract.image_to_string(img))
        return "\n".join(texts)
    except Exception as e:
        logger.debug("OCR failed: %s", e)
        return ""


def extract_text_from_file(uploaded_file, max_size_bytes=10 * 1024 * 1024):
    """Extract text and structured fields from uploaded resume file.

    Returns a dict: { 'text': str, 'meta': dict }.
    """
    filename = getattr(uploaded_file, 'name', 'uploaded').lower()
    data = uploaded_file.read()

    if not data:
        return {'text': '', 'meta': {}}

    if len(data) > max_size_bytes:
        logger.debug("File too large: %d bytes", len(data))
        return {'text': '', 'meta': {}}

    text = ''
    meta = {}

    # Handle PDF
    if filename.endswith('.pdf'):
        try:
            text = pdf_extract_text(io.BytesIO(data)) or ''
        except Exception:
            text = ''

        if not text or len(text.strip()) < 60:
            ocr = _ocr_pdf_bytes(data)
            if ocr and len(ocr.strip()) > len(text):
                text = ocr

    # Handle DOCX
    elif filename.endswith('.docx'):
        try:
            doc = Document(io.BytesIO(data))
            text = '\n'.join([p.text for p in doc.paragraphs])
        except Exception:
            text = ''

    else:
        try:
            text = data.decode('utf-8', errors='ignore')
        except Exception:
            text = ''

    # Try structured parsing if available
    if ResumeParser is not None:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                tmp.write(data)
                tmp_path = tmp.name
            parsed = ResumeParser(tmp_path).get_extracted_data()
            if isinstance(parsed, dict):
                meta = parsed
                parsed_text = parsed.get('text', '') or ''
                if parsed_text and len(parsed_text) > len(text):
                    text = parsed_text
        except Exception:
            logger.debug('pyresparser failed or not available')
        finally:
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

    return {'text': text or '', 'meta': meta or {}}
