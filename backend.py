import pandas as pd
import re

# Load data
df_analysis = pd.read_csv("final_data.csv")


# ===== RISK MODEL =====

def missing_info(row):
    return sum([
        row['salary_range'] == "unknown",
        row['company_profile'] == "unknown",
        row['requirements'] == "unknown"
    ])

def weak_description(row):
    return 1 if len(row['description']) < 50 else 0

def poor_text(row):
    text = row['description']
    ratio = len(re.findall(r'[^a-zA-Z]', text)) / max(len(text), 1)
    return 1 if ratio > 0.3 else 0

def scam_language(row):
    keywords = ["easy money", "quick earning", "no experience", "work from home"]
    return 1 if any(k in text for k in keywords for text in [row['description']]) else 0

def weak_company(row):
    return 1 if row['company_profile'] == "unknown" else 0

def missing_contact(row):
    text = row['description']
    return 1 if ("@" not in text and "www" not in text) else 0

def unrealistic_offer(row):
    keywords = ["high salary", "easy job"]
    return 1 if any(k in text for k in keywords for text in [row['description']]) else 0

def structural_issue(row):
    return sum([
        row['description'] == "unknown",
        row['requirements'] == "unknown",
        row['company_profile'] == "unknown"
    ]) >= 2

def anomaly(row):
    return 1 if len(row['description']) < 30 else 0


def risk_score(row):
    score = 0
    score += 2 * missing_info(row)
    score += 2 * weak_company(row)
    score += weak_description(row)
    score += poor_text(row)
    score += scam_language(row)
    score += missing_contact(row)
    score += unrealistic_offer(row)
    score += structural_issue(row)
    score += anomaly(row)
    return score