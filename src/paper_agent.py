import uuid
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import pandas as pd
import os
import sys
from dataclasses import dataclass, asdict

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Conditional import with error handling
try:
    from src.research_scraper import ResearchScraper, ResearchPaper
    RESEARCH_SCRAPER_AVAILABLE = True
except ImportError as e:
    RESEARCH_SCRAPER_AVAILABLE = False
    ResearchScraper = None
    ResearchPaper = None
    print(f"Warning: Research Scraper could not be imported: {e}. Research paper features will be limited.")

@dataclass
class ResearchPaper:
    """
    Represents a research paper with comprehensive metadata.
    """
    id: str = None
    title: str = ""
    authors: List[str] = None
    publication_date: str = None
    venue: str = ""
    abstract: str = ""
    keywords: List[str] = None
    url: str = ""
    citation_count: int = 0
    research_domains: List[str] = None
    
    def __post_init__(self):
        # Generate unique ID if not provided
        if not self.id:
            self.id = str(uuid.uuid4())
        
        # Initialize empty lists if None
        self.authors = self.authors or []
        self.keywords = self.keywords or []
        self.research_domains = self.research_domains or []
        
        # Set publication date if not provided
        if not self.publication_date:
            self.publication_date = datetime.now().strftime("%Y-%m-%d")

class PaperAgent:
    """
    Specialized agent for managing and analyzing research papers.
    """
    def __init__(self, name: str = None):
        # Generate a unique ID and name if not provided
        self.id = str(uuid.uuid4())
        self.name = name or f"paper_agent_{self.id[:8]}"
        self.role = "research_paper_management"
        
        # Logging setup
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        
        # Add console handler if not already present
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Only initialize if ResearchScraper is available
        if RESEARCH_SCRAPER_AVAILABLE:
            try:
                self.research_scraper = ResearchScraper()
                self.collected_papers: List[ResearchPaper] = []
                self.papers_dataframe: Optional[pd.DataFrame] = None
                self.logger.info("Research scraper initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize research scraper: {e}")
                self.research_scraper = None
                self.collected_papers = []
                self.papers_dataframe = None
        else:
            self.research_scraper = None
            self.collected_papers = []
            self.papers_dataframe = None
            self.logger.warning("Research scraper not available")

    def search_papers(self, query: str) -> List[ResearchPaper]:
        """
        Search and collect research papers from multiple sources
        """
        if not RESEARCH_SCRAPER_AVAILABLE or not self.research_scraper:
            self.logger.warning("Research paper search is not available.")
            return []

        try:
            self.logger.info(f"Searching for papers with query: {query}")
            self.collected_papers = self.research_scraper.scrape_all_sources(query)
            self.logger.info(f"Found {len(self.collected_papers)} papers")
            
            if self.collected_papers:
                self.papers_dataframe = self.research_scraper.to_dataframe(self.collected_papers)
                return self.collected_papers
            else:
                self.logger.warning("No papers found for the given query")
                return []
        except Exception as e:
            self.logger.error(f"Error searching papers: {e}")
            return []

    def get_papers_dataframe(self) -> pd.DataFrame:
        """
        Return collected papers as a DataFrame
        """
        return self.papers_dataframe if self.papers_dataframe is not None else pd.DataFrame()

    def filter_papers(self, keywords: List[str]) -> List[ResearchPaper]:
        """
        Filter collected papers based on keywords
        """
        if not self.collected_papers:
            return []
        
        filtered_papers = [
            paper for paper in self.collected_papers
            if any(keyword.lower() in paper.title.lower() or 
                   keyword.lower() in paper.abstract.lower() 
                   for keyword in keywords)
        ]
        
        return filtered_papers

    def export_papers_to_csv(self, papers: List[ResearchPaper] = None, filename: str = None):
        """
        Export collected papers to a CSV file
        """
        papers_to_export = papers or self.collected_papers
        
        if not papers_to_export:
            self.logger.warning("No papers to export.")
            return None
        
        # Generate a default filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_papers_{timestamp}.csv"
        
        # Ensure the exports directory exists
        export_dir = os.path.join(project_root, 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        full_path = os.path.join(export_dir, filename)
        
        try:
            # Convert papers to DataFrame and export
            df = pd.DataFrame([{
                'title': p.title,
                'authors': ', '.join(p.authors),
                'abstract': p.abstract,
                'url': p.url,
                'source': p.venue,
                'publication_date': p.publication_date
            } for p in papers_to_export])
            
            df.to_csv(full_path, index=False, encoding='utf-8')
            self.logger.info(f"Exported {len(papers_to_export)} papers to {full_path}")
            return full_path
        except Exception as e:
            self.logger.error(f"Error exporting papers to CSV: {e}")
            return None

    def summarize_papers(self, papers: List[ResearchPaper]) -> str:
        """
        Generate a summary of collected papers with web links
        """
        if not papers:
            return "No papers to summarize."
        
        summary = "Research Paper Summary:\n\n"
        for paper in papers[:10]:  # Limit to 10 papers
            summary += f"Title: {paper.title}\n"
            summary += f"Authors: {', '.join(paper.authors)}\n"
            summary += f"Source: {paper.venue}\n"
            summary += f"Web Link: {paper.url}\n"
            summary += f"Abstract: {paper.abstract[:200]}...\n\n"
        
        return summary

    def close(self):
        """
        Close resources
        """
        if self.research_scraper:
            self.research_scraper.close()
