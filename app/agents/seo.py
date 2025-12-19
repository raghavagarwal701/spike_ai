import logging
import os
import re
import json
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import time
from app.llm.client import llm_client
from app.llm.schemas import SEOCodeResponse

load_dotenv()

logger = logging.getLogger(__name__)

CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
SPREADSHEETS_CONFIG_FILE = os.getenv("SPREADSHEETS_CONFIG_FILE", "spreadsheets.json")


def extract_spreadsheet_id(source: str) -> str:
    """
    Extract spreadsheet ID from either a direct ID or a full Google Sheets URL.
    
    Supports URL formats:
    - https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
    - https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0
    - https://docs.google.com/spreadsheets/d/SPREADSHEET_ID
    
    Args:
        source: Either a spreadsheet ID or a full Google Sheets URL
        
    Returns:
        The extracted spreadsheet ID
    """
    # Pattern to match Google Sheets URL and extract the ID
    url_pattern = r'docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)'
    match = re.search(url_pattern, source)
    
    if match:
        return match.group(1)
    
    # If no URL pattern found, assume it's already a direct ID
    return source.strip()


def load_spreadsheet_configs() -> list:
    """
    Load spreadsheet configurations from a JSON file.
    
    Returns:
        List of spreadsheet configuration dictionaries
    """
    if not os.path.exists(SPREADSHEETS_CONFIG_FILE):
        logger.warning(f"Spreadsheets config file '{SPREADSHEETS_CONFIG_FILE}' not found. Using empty list.")
        return []
    
    try:
        with open(SPREADSHEETS_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config.get("spreadsheets", [])
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in spreadsheets config: {e}")
        return []
    except Exception as e:
        logger.error(f"Error reading spreadsheets config: {e}")
        return []


class SEOAgent:
    def __init__(self):
        self.dfs = {}
        self._load_data()

    def _load_data(self):
        """Load SEO data from multiple Google Sheets using service account credentials."""
        if not os.path.exists(CREDENTIALS_FILE):
            raise RuntimeError(
                f"Credentials file '{CREDENTIALS_FILE}' not found. "
                "Please ensure the service account credentials are available."
            )

        spreadsheet_configs = load_spreadsheet_configs()
        if not spreadsheet_configs:
            raise RuntimeError(
                f"No spreadsheets configured. Please add spreadsheets to '{SPREADSHEETS_CONFIG_FILE}'."
            )

        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]

            creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
            client = gspread.authorize(creds)

            for config in spreadsheet_configs:
                spreadsheet_name = config.get("name", "unnamed")
                source = config.get("source", "")
                
                if not source:
                    logger.warning(f"Skipping spreadsheet '{spreadsheet_name}': no source provided")
                    continue
                
                spreadsheet_id = extract_spreadsheet_id(source)
                logger.info(f"Loading spreadsheet '{spreadsheet_name}' (ID: {spreadsheet_id})")
                
                try:
                    spreadsheet = client.open_by_key(spreadsheet_id)
                    
                    for worksheet in spreadsheet.worksheets():
                        sheet_name = worksheet.title
                        # Create a unique key combining spreadsheet name and sheet name
                        key = f"{spreadsheet_name}__{sheet_name}".lower().replace(" ", "_")

                        # Simple retry mechanism for Rate Limit (429)
                        max_retries = 5
                        for attempt in range(max_retries):
                            try:
                                data = worksheet.get_all_records()
                                if data:
                                    self.dfs[key] = pd.DataFrame(data)
                                    logger.info(f"Loaded sheet: {key} ({len(data)} rows)")
                                else:
                                    values = worksheet.get_all_values()
                                    if len(values) > 1:
                                        headers = values[0]
                                        rows = values[1:]
                                        self.dfs[key] = pd.DataFrame(rows, columns=headers)
                                        logger.info(f"Loaded sheet: {key} ({len(rows)} rows)")
                                break  # Success, exit retry loop
                            except Exception as e:
                                if "429" in str(e) and attempt < max_retries - 1:
                                    wait_time = (2 ** attempt) + 1  # Exponential backoff: 2, 3, 5, 9...
                                    logger.warning(f"Rate limit hit for '{sheet_name}'. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                                    time.sleep(wait_time)
                                else:
                                    raise e  # Re-raise if not 429 or out of retries
                                
                except Exception as e:
                    logger.error(f"Error loading spreadsheet '{spreadsheet_name}': {e}")
                    continue

            if not self.dfs:
                raise RuntimeError("No data loaded from any Google Sheets.")

            logger.info(f"SEO Agent: Loaded {len(self.dfs)} sheets from {len(spreadsheet_configs)} spreadsheet(s)")

        except Exception as e:
            logger.error(f"Error loading from Google Sheets: {e}")
            raise RuntimeError(f"Failed to load SEO data: {e}")

    def refresh_data(self):
        """Manually refresh data from Google Sheets."""
        self.dfs = {}
        self._load_data()

    async def process_query(self, query: str):
        # 1. Generate Python code to answer prediction
        code = self._generate_code(query)
        if not code:
            return "I could not generate a solution for that SEO request."
            
        logger.debug(f"Generated Code:\n{code}")

        # 2. Execute Code
        try:
            # Sandbox environment
            local_vars = {"dfs": self.dfs, "pd": pd}
            exec(code, local_vars)
            
            # Expect result in 'result' variable
            if "result" in local_vars:
                return str(local_vars["result"])
            else:
                return "The generated analysis code did not return a 'result' variable."
        except Exception as e:
            return f"Error executing analysis code: {str(e)}"

    def _generate_code(self, query: str):
        # Prepare context about available dataframes
        schema_info = "Available Dataframes (in 'dfs' dictionary):\n"
        for name, df in self.dfs.items():
            columns = ", ".join(df.columns.tolist())  # List all columns
            schema_info += f"- {name}: Columns [{columns}]\n"
            
        prompt = f"""
        You are an SEO Data Analyst. You have access to a dictionary 'dfs' containing Pandas DataFrames with Screaming Frog audit data.
        
        {schema_info}
        
        User Information Request: "{query}"
        
        Write Python code to calculate the answer.
        - You MUST return a JSON object with a field "code" containing the Python code.
        - The code MUST populate a variable named `result` with the final string answer or data.
        - Use `dfs['dataset_name']` to access data.
        - Assume `pd` is imported.
        - Handle case insensitivity if checking string contents.
        - Do not answer the question directly. Write Python code to calculate it.
        - If data is missing or query is impossible, write code that sets `result` to an error message string.
        
        Example:
        result = str(dfs['internal_all'].head(5))
        """
        
        try:
            response = llm_client.chat_structured(
                messages=[{"role": "user", "content": prompt}],
                response_model=SEOCodeResponse,
                model="gemini-2.5-flash"
            )
            return response.code.strip()
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return None

seo_agent = SEOAgent()
