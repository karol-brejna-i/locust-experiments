import csv

import requests
from bs4 import BeautifulSoup

OUTPUT_FILE_PATH = "data.csv"

page = requests.get("https://chess-db.com/public/execute.jsp?age=99&sex=a&countries=all").text

soup = BeautifulSoup(page, "html.parser")
table = soup.find("table", attrs={"border": "0"})
for tag in table.findAll(True):
    if tag.name.lower() in ["div"]:
        tag.append(tag["title"])
    if tag.name.lower() in ["a", "div"]:
        tag.unwrap()
    if tag.name.lower() in ["script", "style", "img", "center"]:
        tag.extract()

rows = [[td.text.strip() for td in row.findAll("td")] for row in table.findAll("tr") if not row.find_all("th")]

with open(OUTPUT_FILE_PATH, "w", newline="") as output_file:
    output_file.write("Number,Id,Name,Title,Fed,Elo,NElo,Born,flag,Games,Club/City,#Trns\n")
    rank_writer = csv.writer(output_file)
    rank_writer.writerows(rows)
