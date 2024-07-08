# -*- coding: utf-8 -*-
from core.db import Base, session, engine
from core.db import Contractor
from sqlalchemy import text, func


def get_contractor_by_ogrn_or_inn(ogrn_or_inn):
    contractor_inn = session.query(Contractor).filter(Contractor.INN == ogrn_or_inn).first()
    contractor_ogrn = session.query(Contractor).filter(Contractor.OGRN == ogrn_or_inn).first()
    if contractor_inn:
         data = { "ogrn": contractor_inn.OGRN,
                "inn": contractor_inn.INN,
                "full_name": contractor_inn.Идентификатор,
                "short_name":contractor_inn.КраткоеНаименование,
                "kpp": contractor_inn.Kpp,
                "status": contractor_inn.Status,
                "address": contractor_inn.AddressAddressLine1
         }
         print(data)
         return data
    if contractor_ogrn:
        data = {"ogrn": contractor_ogrn.OGRN,
                "inn": contractor_ogrn.INN,
                "full_name": contractor_ogrn.Идентификатор,
                "short_name": contractor_ogrn.КраткоеНаименование,
                "kpp": contractor_ogrn.Kpp,
                "status": contractor_ogrn.Status,
                "address": contractor_ogrn.AddressAddressLine1
                }
        print(data)
        return data
    return None


def update_contractor(update_data, ogrn):
    contractor = session.query(Contractor).filter(Contractor.OGRN == ogrn).first()
    if contractor:
        for i in update_data.keys():
            contractor.i = update_data[i]
        session.commit()
        print(f"Contractor with OGRN {ogrn} updated successfully.")
    else:
        print(f"Contractor with OGRN {ogrn} not found.")


def add_contractor(contractor_data):
    try:
        # Получаем максимальный Id
        max_id = session.query(func.max(Contractor.Id)).scalar()
        print(max_id)
        new_id = (max_id or 0) + 1

        insert_query = """
        INSERT INTO NH_Контрагент (Id, OGRN, INN, Идентификатор, КраткоеНаименование, Kpp, Status, 
        AddressAddressLine1, СписокВладельцев, versionNumber, ЭтоГруппа, ВоСколькоГруппВходит)
        VALUES ( :id, :ogrn, :inn, :full_name, :short_name, :kpp, :status, :address, 'no data', 1, 1, 1)
        """

        params = {
            "id": new_id,
            "ogrn": contractor_data.get('ogrn'),
            "inn": contractor_data.get('inn'),
            "full_name": contractor_data.get('full_name'),
            "short_name": contractor_data.get('short_name'),
            "kpp": contractor_data.get('kpp'),
            "status": contractor_data.get('status'),
            "address": contractor_data.get('address'),
        }
        print(params)
        with engine.connect() as connection:
            connection.execute(text(insert_query), params)
            connection.commit()

        print("New contractor added successfully.")
    except Exception as e:
        print(f"Failed to add new contractor: {str(e)}")


