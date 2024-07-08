# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from parse_ogrn_nalog import scrape_ogrn_info
from from_db import get_contractor_by_ogrn_or_inn, update_contractor, add_contractor
from difflib import SequenceMatcher

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class OGRNRequest(BaseModel):
    ogrn: str

def compare_addresses(address1, address2):
    # Разбиваем адреса на части
    parts1 = [part.strip() for part in address1.split(',')]
    parts2 = [part.strip() for part in address2.split(',')]

    # Создаем словарь для хранения различий
    differences = []

    # Получаем максимальную длину для итерации
    max_length = max(len(parts1), len(parts2))

    # Сравниваем части адресов
    for i in range(max_length):
        part1 = parts1[i] if i < len(parts1) else ""
        part2 = parts2[i] if i < len(parts2) else ""

        if part1 != part2:
            differences.append((part1, part2))

    return differences

def find_differences_in_addresses(address1, address2):
    differences = compare_addresses(address1, address2)
    if not differences:
        return None

    result_old = []
    result_new = []
    for part1, part2 in differences:
        result_old.append(f"<span class='old-value'>{part1}</span>")
        result_new.append(f"<span class='new-value'>{part2}</span>")

    old_address = ", ".join(result_old)
    new_address = ", ".join(result_new)

    return old_address, new_address

def is_status_different(status1, status2):
    valid_statuses = ['Действует', "Действующее организация", "Действующее предприятие"]
    return ((status1 not in valid_statuses and status2 in valid_statuses) or
            (status1 in valid_statuses and status2 not in valid_statuses))

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search")
def search(request: Request, ogrn: str = Form(...)):
    try:
        data = scrape_ogrn_info(ogrn)
        print(data)
        if not data:
            raise HTTPException(status_code=500, detail="Failed to retrieve data")

        contractor = get_contractor_by_ogrn_or_inn(ogrn)

        differences = {}
        if contractor:
            if data['full_name'].casefold().split() != contractor['full_name'].casefold().split():
                differences['full_name'] = (contractor['full_name'].casefold(), data['full_name'])
            if data['short_name'].lower().split() != contractor['short_name'].lower().split():
                differences['short_name'] = (contractor['short_name'].casefold(), data['short_name'])
            if is_status_different(data['status'], contractor['status']):
                differences['status'] = (contractor['status'], data['status'])
            address_diff = find_differences_in_addresses(data['address'], contractor['address'])
            if address_diff:
                differences['address'] = address_diff
            print(differences)

            if differences:
                update_data = {}
                for i in differences.keys():
                    update_data[i] = data.get(i)
                update_contractor(update_data, contractor['ogrn'])
        else:
            add_contractor(data)


        okveds = data.pop("okveds", None)
        return templates.TemplateResponse("index.html",
                                          {"request": request, "data": data, "ogrn": ogrn, "okveds": okveds, "differences": differences})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
