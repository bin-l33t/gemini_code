import re
import sys

def parse_usage_html(file_path="usage.txt"):
    print(f"--- Parsing {file_path} for Rate Limits ---")
    
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ BeautifulSoup is not installed. Please run: pip install beautifulsoup4")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: '{file_path}' not found. Make sure you saved the HTML content there.")
        return

    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all("tr")
    
    if not rows:
        print("⚠️  No table rows found.")
        return

    # Print Header
    print(f"\n{'MODEL NAME':<30} | {'RPM LIMIT':<15} | {'TPM LIMIT':<15}")
    print("-" * 65)

    found_models = []

    for row in rows:
        cells = row.find_all(["td", "th"])
        # Get all text from the row
        row_text = [c.get_text(strip=True) for c in cells]
        
        # We need at least 6 columns based on your debug output
        # Col 0: Status | Col 1: Model | Col 2: Category | Col 3: RPM | Col 4: TPM
        if len(row_text) < 5:
            continue

        # Check if column 1 is a model name (contains 'gemini')
        model_name = row_text[1]
        if "gemini" in model_name.lower():
            
            # Helper to clean "Used / Limit" strings (e.g. "2 / 2K" -> "2K")
            def clean_limit(val):
                if "/" in val:
                    return val.split("/")[-1].strip()
                return val

            rpm = clean_limit(row_text[3])
            tpm = clean_limit(row_text[4])
            
            print(f"{model_name:<30} | {rpm:<15} | {tpm:<15}")
            found_models.append(model_name)

    print("-" * 65)
    
    if not found_models:
        print("⚠️  No Gemini models found. Check column indices again.")

if __name__ == "__main__":
    parse_usage_html()
