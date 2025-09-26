import webbrowser
import urllib.parse
import requests
from bs4 import BeautifulSoup
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import datetime
import sys
import time

QUERY = "python developer"          
LOCATION = "Bengaluru, India"       
MAX_RESULTS = 20
OPEN_BROWSER = True

BASE_URL = "https://www.indeed.com/jobs"  

def build_search_url(query, location):
    params = {"q": query}
    if location:
        params["l"] = location
    return BASE_URL + "?" + urllib.parse.urlencode(params)

def fetch_search_html(url, timeout=12):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text

def parse_jobs(html, page_url):
    soup = BeautifulSoup(html, "lxml")
    jobs = []
    
    cards = soup.find_all(attrs={"data-jk": True})
    if not cards:
        cards = soup.find_all("div", class_="job_seen_beacon")
    for c in cards:
        title_node = c.find("h2") or c.find("a", class_="jobtitle") or c.find("a", {"data-tn-element": "jobTitle"})
        title = title_node.get_text(strip=True) if title_node else None

        company_node = c.find("span", class_="company") or c.find("span", class_="companyName") or c.find("div", class_="company")
        company = company_node.get_text(strip=True) if company_node else None

        loc_node = c.find(attrs={"class": lambda x: x and "location" in x}) or c.find("div", class_="companyLocation")
        location = loc_node.get_text(strip=True) if loc_node else None

        summary_node = c.find("div", class_="job-snippet") or c.find("div", class_="summary")
        summary = summary_node.get_text(" ", strip=True) if summary_node else None

        job_id = c.get("data-jk") or None
        job_url = f"{BASE_URL.replace('/jobs','')}/viewjob?jk={job_id}" if job_id else None

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "summary": summary,
            "job_url": job_url
        })
    return jobs

def save_csv(jobs, filename="results.csv"):
    df = pd.DataFrame(jobs)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    return filename

def make_pdf(jobs, filename="indeed_results.pdf", title=None):
    
    header = ["S.No", "Title", "Company", "Location", "Summary"]
    rows = [header]
    for i, j in enumerate(jobs, start=1):
        rows.append([
            str(i),
            j.get("title") or "",
            j.get("company") or "",
            j.get("location") or "",
            (j.get("summary") or "")[:300]  
        ])

    
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=20)
    table = Table(rows, repeatRows=1, colWidths=[30, 220, 140, 120, 300])
    style = TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#4B8BBE")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 12),
        ("FONTSIZE", (0,1), (-1,-1), 9),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BOX", (0,0), (-1,-1), 0.25, colors.grey),
    ])
    table.setStyle(style)

    
    story = []
    
    story.append(table)
    doc.build(story)
    return filename

def main():
    search_url = build_search_url(QUERY, LOCATION)
    print("Search URL:", search_url)
    if OPEN_BROWSER:
        try:
            webbrowser.open(search_url)
            print("Opened search page in your default browser.")
           
            time.sleep(0.7)
        except Exception as e:
            print("Could not open browser:", e)

    try:
        html = fetch_search_html(search_url)
    except Exception as e:
        print("Failed to fetch search page:", e)
        sys.exit(1)

    jobs = parse_jobs(html, search_url)
    if not jobs:
        print("No jobs found on the first page (site structure may differ).")
    else:
       
        jobs_for_pdf = jobs[:MAX_RESULTS]
        csv_path = save_csv(jobs, "results.csv")
        pdf_path = make_pdf(jobs_for_pdf, "indeed_results.pdf", title=f"Indeed results for '{QUERY}'")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Scraped {len(jobs)} jobs (saved {len(jobs_for_pdf)} to PDF).")
        print(f"CSV -> {csv_path}")
        print(f"PDF -> {pdf_path}")
        print(f"Completed at {now}")

if __name__ == "__main__":
    main()