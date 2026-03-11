from fastapi import APIRouter, HTTPException
import mysql.connector
from pydantic import BaseModel, field_validator
from database.connection import get_connection

router = APIRouter()

class LastnameBody(BaseModel):
    lastname: str

    @field_validator('lastname')
    @classmethod
    def not_empty(cls, value):
        if not value.strip():
            raise ValueError("Lastname cannot be empty")
        return value.strip()

@router.post("/persons/{person_id}/lastname", status_code=201, tags=["LastName"])
def Add_a_new_lastname_to_a_person(person_id: int, body: LastnameBody):
    """ This will create only a lastname for a specific person using the person_id """
    db = get_connection()
    cursor = db.cursor()

    try: 
        cursor.execute(
            "SELECT id FROM person WHERE id = %s",
            (person_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Person with id={person_id} not found"
            )
        
        cursor.execute(
            "INSERT INTO lastname (person_id, lastname) VALUES (%s, %s)",
            (person_id, body.lastname)
        )
        db.commit()

        return {
            "id": cursor.lastrowid,
            "person_id": person,
            "lastname": body.lastname
        
        }
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(err))

    finally:
        db.close()

@router.put("/persons/{person_id}/lastnames/{lastname_id}", tags=["LastName"])
def Update_a_lastname(person_id: int, lastname_id: int, body: LastnameBody):
    """ Rename an existing lastname using the person_id and lastname_id """

    db = get_connection()
    cursor = db.cursor()

    try: 
        # person must exist 
        cursor.execute("SELECT id FROM person WHERE id = %s", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Person with id={person_id} not found"
            )

        cursor.execute(
            "UPDATE lastname SET lastname = %s WHERE id = %s AND person_id = %s",
            (body.lastname, lastname_id, person_id)
        )
        db.commit()

        # lastname must exist for this person ───
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Lastname with id={lastname_id} not found for this person"
            )

        return {
            "id":        lastname_id,
            "person_id": person_id,
            "lastname":  body.lastname
        }

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        db.close()

@router.delete("/persons/{person_id}/lastnames/{lastname_id}", tags=["LastName"])
def Delete_lastname(person_id: int, lastname_id: int):
    """ Delete specific lastname using the person_id and lastname_id """
    db = get_connection()
    cursor = db.cursor()

    try: 

        cursor.execute(
            
        )

