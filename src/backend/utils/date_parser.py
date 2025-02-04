from datetime import datetime, timedelta
import re

def extract_date(query):
    date_patterns = [
        (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),  
        (r"\d{2}/\d{2}/\d{4}", "%d/%m/%Y"),  
        (r"(\d{1,2})\s([A-Za-z]+)\s(\d{4})", None)  
    ]

    for pattern, date_format in date_patterns:
        match = re.search(pattern, query)
        if match:
            if date_format:
                return datetime.strptime(match.group(0), date_format).strftime("%Y-%m-%d")
            else:
                day, month_name, year = match.groups()
                month_number = datetime.strptime(month_name, "%B").month
                return f"{year}-{month_number:02d}-{int(day):02d}"

    return None  

def extract_date_range(query):
    date_matches = re.findall(r"\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{1,2} [A-Za-z]+ \d{4}", query)

    if not date_matches:
        return None, None, "No valid date found in query."

    if len(date_matches) == 1:
        start_date = extract_date(date_matches[0])
        end_date = start_date
    elif len(date_matches) == 2:
        start_date, end_date = extract_date(date_matches[0]), extract_date(date_matches[1])

    if not start_date or not end_date:
        return None, None, "Invalid date format detected."

    today = datetime.today().strftime("%Y-%m-%d")
    if start_date > today or (end_date and end_date > today):
        return None, None, "Cannot query for future dates."

    five_years_ago = (datetime.today() - timedelta(days=5 * 365)).strftime("%Y-%m-%d")
    if start_date < five_years_ago:
        return None, None, "Cannot fetch data older than 5 years."

    return start_date, end_date, None  

def get_date_range(start_date, end_date=None):
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
        else:
            end_dt = start_dt + timedelta(days=1) - timedelta(seconds=1)

        return {"$gte": start_dt, "$lt": end_dt}

    except ValueError:
        return None

