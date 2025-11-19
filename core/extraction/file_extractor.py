import logging
from pathlib import Path
from typing import Dict, Optional
import platform
import subprocess

# Import libraries for fallback conversion
try:
    from pptx import Presentation
    from docx import Document
    import cv2
except ImportError:
    # These are optional dependencies, only needed for file conversion
    pass

logger = logging.getLogger(__name__)

class FileExtractor:
    """Extracts raw text content from various file types."""

    def extract_content(self, file_path: Path) -> Dict[str, str]:
        """
        Extracts text content from a file.
        Returns a dictionary with 'text' and 'file_type'.
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {"text": "", "file_type": "not_found"}

        file_type = file_path.suffix.lower()
        text = ""

        try:
            if file_type == '.pdf':
                # Placeholder for PDF extraction.
                # A library like PyMuPDF (fitz) would be used here.
                text = f"Raw text from {file_path.name}"
            elif file_type == '.pptx':
                text = self._extract_text_from_pptx(file_path)
            elif file_type == '.docx':
                text = self._extract_text_from_docx(file_path)
            elif file_type in ['.mp4', '.mov', '.avi']:
                text = self._extract_info_from_video(file_path)
            elif file_type in ['.jpg', '.jpeg', '.png', '.gif']:
                text = f"Image file detected: {file_path.name}. Content analysis required."
            else:
                # Default to reading as a plain text file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
        except Exception as e:
            logger.error(f"Failed to extract content from {file_path}: {e}")
            text = f"Error extracting content from {file_path.name}."

        return {"text": text, "file_type": file_type}

    def _extract_text_from_pptx(self, file_path: Path) -> str:
        """Extracts text from a PPTX file."""
        try:
            prs = Presentation(file_path)
            text_runs = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text_runs.append(shape.text)
            return "\n".join(text_runs)
        except Exception as e:
            logger.error(f"Error reading PPTX file {file_path}: {e}")
            return f"Could not extract text from {file_path.name}."

    def _extract_text_from_docx(self, file_path: Path) -> str:
        """Extracts text from a DOCX file."""
        try:
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error reading DOCX file {file_path}: {e}")
            return f"Could not extract text from {file_path.name}."

    def _extract_info_from_video(self, file_path: Path) -> str:
        """Extracts basic information from a video file."""
        try:
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                raise IOError("Could not open video file.")

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0

            cap.release()
            return f"Video file detected: {file_path.name}. Duration: {duration:.2f} seconds. Further content analysis (e.g., audio transcription, keyframe extraction) would require additional libraries and processing."
        except Exception as e:
            logger.error(f"Error processing video file {file_path}: {e}")
            return f"Error processing video file {file_path.name}."
