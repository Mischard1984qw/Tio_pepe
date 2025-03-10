"""Web scraping and data extraction agent for the Tío Pepe system."""

from typing import Dict, Any, List
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WebAgent:
    """Specialized agent for web scraping and data extraction tasks."""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.session = requests.Session()
        self.driver = None

    def process_task(self, task: Any) -> Dict[str, Any]:
        """Process a web task based on its type."""
        task_type = task.data.get('web_type')
        url = task.data.get('url')

        if not url:
            raise ValueError("No URL provided for processing")

        if task_type == 'scrape_static':
            return self._scrape_static_content(url)
        elif task_type == 'scrape_dynamic':
            return self._scrape_dynamic_content(url)
        elif task_type == 'extract_links':
            return self._extract_links(url)
        else:
            raise ValueError(f"Unsupported web task type: {task_type}")

    def _scrape_static_content(self, url: str) -> Dict[str, Any]:
        """Scrape content from a static webpage."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content = {
                'title': soup.title.string if soup.title else '',
                'text': soup.get_text(strip=True),
                'meta_description': '',
                'h1_headers': [h1.text for h1 in soup.find_all('h1')]
            }
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                content['meta_description'] = meta_desc.get('content', '')
                
            return {'content': content}
        except Exception as e:
            self.logger.error(f"Static scraping error: {str(e)}")
            raise

    def _scrape_dynamic_content(self, url: str) -> Dict[str, Any]:
        """Scrape content from a dynamic webpage using Selenium."""
        try:
            if not self.driver:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                self.driver = webdriver.Chrome(options=chrome_options)

            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            content = {
                'title': self.driver.title,
                'text': self.driver.find_element(By.TAG_NAME, 'body').text,
                'dynamic_elements': []
            }
            
            # Collect dynamic elements (e.g., elements loaded by JavaScript)
            dynamic_elements = self.driver.find_elements(By.CLASS_NAME, 'dynamic-content')
            content['dynamic_elements'] = [
                {'text': elem.text, 'html': elem.get_attribute('innerHTML')}
                for elem in dynamic_elements
            ]
            
            return {'content': content}
        except Exception as e:
            self.logger.error(f"Dynamic scraping error: {str(e)}")
            raise

    def _extract_links(self, url: str) -> Dict[str, Any]:
        """Extract all links from a webpage."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    links.append({
                        'url': href,
                        'text': link.text.strip(),
                        'title': link.get('title', '')
                    })
            
            return {'links': links}
        except Exception as e:
            self.logger.error(f"Link extraction error: {str(e)}")
            raise

    def cleanup(self) -> None:
        """Cleanup resources used by the agent."""
        if self.driver:
            self.driver.quit()
        self.session.close()
        self.logger.info("Web agent cleaned up")