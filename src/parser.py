import requests
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
from src.config import USER_AGENT

class SECParser:
    def __init__(self):
        self.headers = {
            "User-Agent": USER_AGENT,
            "Host": "www.sec.gov" # XML files are usually on www.sec.gov
        }

    def fetch_and_parse_xml(self, xml_url):
        """
        Downloads the XML file from the URL and converts it to a Pandas DataFrame.
        """
        print(f"Downloading XML from: {xml_url}")
        try:
            response = requests.get(xml_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # Parse the XML content
            # 13F XML structure is usually: <informationTable> ... <infoTable> ... </infoTable> </informationTable>
            tree = ET.parse(BytesIO(response.content))
            root = tree.getroot()
            
            # Namespace handling: SEC XMLs often have namespaces like {http://www.sec.gov/edgar/document/thirteenf/informationtable}
            # We strip them to make parsing easier.
            data = []
            
            for info_table in root:
                # We iterate through children because tag names might have namespaces
                row = {}
                for child in info_table:
                    # Remove namespace from tag: '{http://...}nameOfIssuer' -> 'nameOfIssuer'
                    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    
                    if tag == 'shrsOrPrnAmt':
                        # This tag usually has children (sshPrnamt, sshPrnamtType)
                        for subchild in child:
                            subtag = subchild.tag.split('}')[-1]
                            row[subtag] = subchild.text
                    else:
                        row[tag] = child.text
                
                # Normalize the data into a clean dictionary
                clean_row = {
                    "stock_name": row.get("nameOfIssuer"),
                    "cusip": row.get("cusip"),
                    "value_x1000": float(row.get("value", 0)), # Value is usually in thousands
                    "shares": float(row.get("sshPrnamt", 0)),
                    "share_type": row.get("sshPrnamtType")
                }
                data.append(clean_row)

            # Convert to DataFrame
            df = pd.DataFrame(data)
            return df

        except Exception as e:
            print(f"Error parsing XML: {e}")
            return pd.DataFrame() # Return empty DF on failure

# Test block
if __name__ == "__main__":
    # Use the URL you got from the previous step (Berkshire Hathaway) to test
    # If you didn't get one, use this hardcoded one for testing:
    # Berkshire Hathaway Q3 2024 Info Table
    test_url = "https://www.sec.gov/Archives/edgar/data/0001067983/000119312525282901/46994.xml"
    
    parser = SECParser()
    df = parser.fetch_and_parse_xml(test_url)
    
    if not df.empty:
        print("\n--- SUCCESS: Data Extracted ---")
        print(df.head())
        print(f"\nTotal Holdings Found: {len(df)}")
        print(f"Top Holding: {df.iloc[0]['stock_name']}")
    else:
        print("Failed to parse data.")