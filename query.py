import requests
import csv

BASE_URL = "https://gtr.ukri.org/gtr/api/organisations/"
PROJECTS_ENDPOINT = "/projects"

organisation_ids = [
    "D9E2F69B-E694-49DC-B660-E0AA6C7A28E8",
    "189F1BDE-BC7C-437B-AC3C-AA4AC0B677F0",
    "64EDCEB7-556D-4890-9582-FD894F98C10D"
]

HEADERS = {
    "Accept": "application/vnd.rcuk.gtr.json-v7"
}

def fetch_paginated_data(url, params):
    results = []
    while True:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            results.extend([project for project in data.get("project", []) if project.get("status") != "Closed"])
            if params["page"] >= data.get("totalPages", 1):
                break
            params["page"] += 1
        else:
            print(f"Failed to fetch project data (Status Code: {response.status_code})")
            break
    return results

def fetch_person_details(href):
    response = requests.get(href, headers=HEADERS)
    if response.status_code == 200:
        person_data = response.json()
        return person_data.get("firstName"), person_data.get("surname")
    else:
        print(f"Failed to fetch person data (Status Code: {response.status_code})")
        return None, None

def fetch_organisation_projects(org_id, csv_writer):
    url = f"{BASE_URL}{org_id}{PROJECTS_ENDPOINT}"
    params = {"page": 1, "size": 100}
    projects = fetch_paginated_data(url, params)

    for project in projects:
        project_href = project.get("href")
        title = project.get("title")
        abstract_text = project.get("abstractText")

        if "links" in project:
            links = project["links"].get("link")
            for link in links:
                if "PER" in link.get("rel"):
                    person_href = link.get("href")
                    relationship = link.get("rel")
                    first_name, surname = fetch_person_details(link.get("href"))
                    print(f"Project {project.get('id')} - Project Persin: {first_name} {surname}")
                    csv_writer.writerow([project_href, title, abstract_text, person_href, relationship, first_name, surname])

def write_to_csv():
    with open("projects_data.csv", mode="w", newline="") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Project Href", "Title", "Abstract Text", "Person Href", "Relationship", "First Name", "Surname"])

        for org_id in organisation_ids:
            fetch_organisation_projects(org_id, csv_writer)

if __name__ == "__main__":
    write_to_csv()
    print("Data successfully written to projects_data.csv")
