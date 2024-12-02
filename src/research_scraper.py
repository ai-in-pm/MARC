import requests
import arxiv
from scholarly import scholarly
import pandas as pd
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional WebDriver imports with error handling
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium or WebDriver not available. Some web scraping features will be limited.")

@dataclass
class ResearchPaper:
    """
    Data class for storing research paper information
    """
    title: str
    authors: List[str]
    abstract: str
    url: str
    publication_date: Optional[str] = None
    source: str = 'Unknown'

class ResearchScraper:
    """
    A class to scrape research papers from multiple academic sources
    """
    def __init__(self, max_results: int = 10):
        self.max_results = max_results
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # WebDriver initialization with fallback
        self.driver = None
        if SELENIUM_AVAILABLE:
            try:
                # Setup Chrome options for headless browsing
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                
                # Initialize WebDriver
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()), 
                    options=chrome_options
                )
            except Exception as e:
                self.logger.error(f"Could not initialize WebDriver: {e}")
                self.driver = None

    def scrape_arxiv(self, query: str) -> List[ResearchPaper]:
        """
        Scrape research papers from arXiv
        """
        try:
            # Configure arXiv client
            search = arxiv.Search(
                query=query,
                max_results=self.max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            papers = []
            for result in search.results():
                try:
                    paper = ResearchPaper(
                        title=result.title,
                        authors=[str(author) for author in result.authors],
                        abstract=result.summary,
                        url=result.pdf_url,  # Use the direct PDF URL
                        publication_date=str(result.published),
                        source='arXiv'
                    )
                    papers.append(paper)
                    if len(papers) >= self.max_results:
                        break
                except Exception as e:
                    self.logger.warning(f"Error processing arXiv result: {e}")
                    continue
            
            self.logger.info(f"Found {len(papers)} papers from arXiv")
            return papers
        except Exception as e:
            self.logger.error(f"Error scraping arXiv: {e}")
            return []

    def scrape_semantic_scholar(self, query: str) -> List[ResearchPaper]:
        """
        Scrape research papers from Semantic Scholar
        """
        try:
            # Use the Semantic Scholar API
            url = f"https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": query,
                "limit": self.max_results,
                "fields": "title,authors,abstract,url,venue,year"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for paper_data in data.get('data', []):
                try:
                    if paper_data.get('title') and paper_data.get('authors'):
                        paper = ResearchPaper(
                            title=paper_data.get('title', ''),
                            authors=[author.get('name', '') for author in paper_data.get('authors', [])],
                            abstract=paper_data.get('abstract', 'No abstract available'),
                            url=paper_data.get('url') or f"https://www.semanticscholar.org/paper/{paper_data.get('paperId', '')}",
                            publication_date=str(paper_data.get('year', '')),
                            source='Semantic Scholar'
                        )
                        papers.append(paper)
                except Exception as e:
                    self.logger.warning(f"Error processing Semantic Scholar result: {e}")
                    continue
            
            self.logger.info(f"Found {len(papers)} papers from Semantic Scholar")
            return papers
        except Exception as e:
            self.logger.error(f"Error scraping Semantic Scholar: {e}")
            return []

    def scrape_google_scholar(self, query: str) -> List[ResearchPaper]:
        """
        Scrape research papers from Google Scholar
        """
        try:
            # Configure scholarly
            scholarly.configure_logger(level=logging.WARNING)
            
            # Search for papers
            search_query = scholarly.search_pubs(query)
            papers = []
            count = 0
            
            for result in search_query:
                try:
                    # Extract paper details
                    bib = result.get('bib', {})
                    paper = ResearchPaper(
                        title=bib.get('title', 'Unknown Title'),
                        authors=bib.get('author', ['Unknown Author']),
                        abstract=bib.get('abstract', 'No abstract available'),
                        url=result.get('pub_url', ''),
                        publication_date=str(bib.get('year', '')),
                        source='Google Scholar'
                    )
                    papers.append(paper)
                    
                    count += 1
                    if count >= self.max_results:
                        break
                except Exception as e:
                    self.logger.warning(f"Error processing Google Scholar result: {e}")
                    continue
            
            self.logger.info(f"Found {len(papers)} papers from Google Scholar")
            return papers
        except Exception as e:
            self.logger.error(f"Error scraping Google Scholar: {e}")
            return []

    def scrape_all_sources(self, query: str) -> List[ResearchPaper]:
        """
        Scrape research papers from multiple sources using parallel execution
        """
        all_papers = []
        
        # Define scraping functions to run in parallel
        scraping_functions = [
            (self.scrape_arxiv, "arXiv"),
            (self.scrape_semantic_scholar, "Semantic Scholar"),
            (self.scrape_google_scholar, "Google Scholar")
        ]
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_source = {
                executor.submit(func, query): source_name
                for func, source_name in scraping_functions
            }
            
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    papers = future.result()
                    self.logger.info(f"Retrieved {len(papers)} papers from {source_name}")
                    all_papers.extend(papers)
                except Exception as e:
                    self.logger.error(f"Error retrieving papers from {source_name}: {e}")
        
        # Remove duplicates based on title (case-insensitive)
        seen_titles = {}
        unique_papers = []
        for paper in all_papers:
            title_lower = paper.title.lower()
            if title_lower not in seen_titles:
                seen_titles[title_lower] = True
                unique_papers.append(paper)
        
        self.logger.info(f"Total unique papers found: {len(unique_papers)}")
        return unique_papers

    def to_dataframe(self, papers: List[ResearchPaper]) -> pd.DataFrame:
        """
        Convert list of ResearchPaper to pandas DataFrame
        """
        try:
            if not papers:
                return pd.DataFrame()
            
            # Convert papers to list of dictionaries
            paper_dicts = []
            for paper in papers:
                paper_dict = asdict(paper)
                paper_dict['authors'] = ', '.join(paper_dict['authors'])
                paper_dicts.append(paper_dict)
            
            return pd.DataFrame(paper_dicts)
        except Exception as e:
            self.logger.error(f"Error converting papers to DataFrame: {e}")
            return pd.DataFrame()

    def close(self):
        """
        Close WebDriver
        """
        if self.driver:
            self.driver.quit()
