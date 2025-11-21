from pathlib import Path
from typing import List, Dict
from .file_extractor import FileExtractor
import logging

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Process multiple files - extraction and detection combined"""
    
    def __init__(self, extractor: FileExtractor, max_file_workers: int = 3):
        self.extractor = extractor
        self.max_file_workers = max_file_workers
    
    def process_idea_files(self, idea_id: str, files_dir: Path) -> Dict[str, any]:
        """Process all files for a given idea"""
        
        if not files_dir.exists():
            logger.warning(f"No files found for idea {idea_id}")
            return {
                'extracted_content': '',
                'files_processed': 0,
                'file_types': '',
                'content_type': 'Text',
                'status': 'no_files'
            }
        
        files = self._find_files(files_dir)
        
        if not files:
            return {
                'extracted_content': '',
                'files_processed': 0,
                'file_types': '',
                'content_type': 'Text',
                'status': 'no_files'
            }
        
        print(f"\n📁 Processing {len(files)} files for idea {idea_id}")
        
        combined_content = []
        processed_count = 0
        file_types = []
        content_types = []  # Track content type from each file
        
        for file_path in files:
            try:
                # ✅ Single API call returns both content AND type
                result = self.extractor.extract_content(file_path)
                
                combined_content.append(f"\n--- Content from {file_path.name} ---\n{result['content']}\n")
                content_types.append(result['content_type'])
                
                file_ext = file_path.suffix.lower().replace('.', '')
                if file_ext not in file_types:
                    file_types.append(file_ext)
                
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed to extract {file_path.name}: {e}")
                combined_content.append(f"\n--- Error extracting {file_path.name}: {str(e)} ---\n")
        
        full_content = '\n'.join(combined_content)
        
        # ✅ Determine overall content type: if ANY file is Prototype, mark as Prototype
        overall_type = "Prototype" if "Prototype" in content_types else "Text"
        
        file_types_str = ', '.join(sorted(file_types))
        
        return {
            'extracted_content': full_content,
            'files_processed': processed_count,
            'file_types': file_types_str,
            'content_type': overall_type,
            'status': 'completed' if processed_count > 0 else 'failed'
        }
    
    def _find_files(self, directory: Path) -> List[Path]:
        """Find all supported files"""
        logger.debug(f"Searching for supported files in: {directory}")
        supported_extensions = {'.pdf', '.pptx', '.docx', '.mp4', '.mov', '.avi', '.jpg', '.jpeg', '.png', '.webp'}
        files = []
        
        for file in directory.iterdir():
            logger.debug(f"Found file: {file.name}, suffix: {file.suffix.lower()}")
            if file.is_file() and file.suffix.lower() in supported_extensions:
                files.append(file)
                logger.debug(f"Added supported file: {file.name}")
            else:
                logger.debug(f"Skipped unsupported file: {file.name}")
        
        logger.info(f"Found {len(files)} supported files in {directory}")
        return sorted(files)
