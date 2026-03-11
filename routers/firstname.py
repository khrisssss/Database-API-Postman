from fastapi import APIRouter, HTTPException
import mysql.connector
from pydantic import BaseModel, field_validator
from database.connection import get_connection

router = APIRouter()

class FirstnameBody(BaseModel):
    firstname: str 

    @field_validator('firstname')
    @classmethod
    def not_empty(cls, value):      # cls the entire class / value will be the firstname that user sent 
        if not value.strip():
            raise ValueError("Firstname cannot be empty")
        return value.strip()
    
@router.post("/persons/{person_id}/firstname", status_code= 201, tags=["FirstName"])
def Add_a_new_firstname_to_a_person(person_id: int, body: FirstnameBody):
    """ This will create only a firstname for a specific person using the person_id """
    db= get_connection()
    cursor= db.cursor()

    try: 

        cursor.execute(
            "SELECT id FROM person WHERE id = %s",         #check if the person exists so it look in the person table
            (person_id,)
        
        )
        if not cursor.fetchone():                                               # if id does not exist (returns none) then it will raise an  error and cant put a name
            raise HTTPException(
                status_code=404,
                detail="Person not found in the database"
            )
        
        print('hello')
        print("ID", cursor.lastrowid)
        print("Personid", person_id)
        print("firstname", body.firstname)
        cursor.execute(
            "INSERT INTO firstname (person_id, firstname) VALUES (%s, %s)",     # it will insert the new name in to the firstname and add it into perso table
            (person_id, body.firstname)
        
        )
        print("IDllllllllllllllllll")
        db.commit()
        print("ID", cursor.lastrowid)
        print("Personid", person_id)
        print("firstname", body.firstname)
        return {
            "id": cursor.lastrowid,                                              # lastrowid will give a new id number 
            "person_id": person_id,
            "firstname": body.firstname                                     #insert firstname into firstname table 
        }
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(err))

    finally:
        db.close()
    
@router.put("/persons/{person_id}/firstnames/{firstname_id}",tags=["FirstName"])
def Update_a_firstname(person_id: int, firstname_id: int, body: FirstnameBody):
    """ Rename an existing firstname using the person_id and firstname_id """
    db= get_connection()
    cursor= db.cursor()

    try:
        # person must exist 
        cursor.execute("SELECT id FROM person WHERE id = %s", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Person with id={person_id} not found"
            )

        cursor.execute(
            "UPDATE firstname SET firstname = %s WHERE id = %s AND person_id = %s",
            (body.firstname, firstname_id, person_id)
        )
        db.commit()  #save

    
        if cursor.rowcount == 0:                   #this checks: does firstname_id=7 actually belong to person_id=1??? 
            raise HTTPException(                   #if not, then it will raise an error 404
                status_code=404,
                detail=f"Firstname with id={firstname_id} not found for this person"
            )

        return {
            "id":        firstname_id,
            "person_id": person_id,
            "firstname": body.firstname
        }

    except mysql.connector.Error as e:
        db.rollback()       # means undo everything that happened in that try block.
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        db.close()

@router.delete("/delete/persons/{person_id}/firstnames/{firstname_id}",tags=["FirstName"])
def Delete_firstname(person_id: int, firstname_id: int):
    """ Delete the firstname from a person using the person_id and firstname_id """

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
            "DELETE FROM firstname WHERE id = %s AND person_id = %s",
            (firstname_id, person_id)
        )
        db.commit()

        # firstname must exist for this person
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Firstname with id={firstname_id} not found for this person"
            )

        return {"message": "Firstname deleted successfully"}

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        db.close()










































