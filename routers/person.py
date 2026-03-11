from datetime import date
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from fastapi import APIRouter
from database.connection import get_connection
router = APIRouter()


class PersonCreate(BaseModel):
    firstnames: Optional[list[str]] = []
    lastnames:  Optional[list[str]] = []
    birth_date: Optional[date] = None
    death_date: Optional[date] = None

    @field_validator('firstnames') #only firstname can't be empty
    @classmethod 
    def names_not_empty(cls, value):
        for name in value:
            if not name.strip():
                raise ValueError("Firstname cannot be empty strings")
        return value

class PersonUpdate(BaseModel):
    birth_date: Optional[date] = None
    death_date: Optional[date] = None

# My constraint that is not possible to do in SQL
def check_at_least_one_firstname(firstnames):
    if not firstnames or len(firstnames) == 0:         #A person must have at least one firstname
        raise HTTPException(
            status_code=400,
            detail="A person must have at least one firstname"
        )
    
@router.post("/persons", status_code=201, tags=["Person"])
def Add_a_new_person_to_the_database(person: PersonCreate):
    """ Creates a new person. At least one firstname is required and last name, DOB and DOD are optional """
    if not person.firstnames or len(person.firstnames) == 0:
        raise HTTPException(
            status_code=400,
            detail="A person must have at least one firstname"
        )

    db = get_connection()  # Establish a connection to the database
    cursor = db.cursor()  # Create a cursor object to execute SQL queries

    try:
        cursor.execute(
            "INSERT INTO person (birth_date, death_date) VALUES (%s, %s)",
            (person.birth_date, person.death_date)
        )
        new_id = cursor.lastrowid   # Get the ID of the newly inserted record
        # first i have to create the person table
        # then, get the id of the new person then
        # insert the firstnames and lastnames in the names table with the person_id as a foreign key

        for firstname in person.firstnames:
            cursor.execute(
                "INSERT INTO firstname(person_id,firstname) VALUES (%s, %s)",
                (new_id, firstname)
            )

        for lastname in person.lastnames:
            cursor.execute(
                "INSERT INTO lastname(person_id, lastname) VALUES (%s, %s)",
                (new_id, lastname)
            )

        db.commit()  # Commit the transaction to save changes to the database

        return {
            "id":         new_id,
            "birth_date": person.birth_date,
            "death_date": person.death_date,
            "firstnames": person.firstnames,
            "lastnames":  person.lastnames
        }
    except mysql.connector.Error as err:
        db.rollback()  # undo everything if something failed
        # then, it will return an error message
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        db.close()  # success or not, close the database connection


@router.get("/persons", tags=["Person"])
def List_all_persons():
    """ Returns ALL persons in the database with their firstnames, lastnames, DOB and DOD """
    db = get_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT id FROM person"  # get all the ids of the persons in the database first
        )
        ids = cursor.fetchall()  # fetchall() returns a list of rows

        result = []  # empty list to store the results

        for row in ids:
            person_id = row[0]  # get the id of the person

            cursor.execute(
                "SELECT id, birth_date, death_date FROM person WHERE id = %s",
                (person_id,)
            )
            person = cursor.fetchone()  # fetchone bcus ID is unique, it will return only one row
            print('person:', person)
            cursor.execute(
                "SELECT id, firstname FROM firstname WHERE person_id = %s",
                (person_id,)
            )
            # fetchall() bcus a person can have multiple firstnames, it will return a list of rows
            firstname = cursor.fetchall()
            cursor.execute(
                "SELECT id, lastname FROM lastname "
                "WHERE person_id = %s",
                (person_id,)
            )
            lastname = cursor.fetchall()
            result.append({
                    "id": person[0],
                    "birth_date": person[1],
                    "death_date": person[2],
                    # extract the firstnames from the rows
                    "firstnames": [row[1] for row in firstname],
                    # extract the lastnames from the rows
                    "lastnames": [row[1] for row in lastname]
                })
        return result

    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        db.close()


@router.get("/persons/{person_id}", tags=["Person"])
def Get_information_about_a_specific_person(person_id: int):
    """Returns ONE specific person by their ID. """
    db = get_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT * FROM person WHERE id = %s",
            (person_id,)
        )
        person = cursor.fetchone()

        cursor.execute(
            "SELECT firstname FROM firstname WHERE person_id = %s",
            (person_id,)
        )
        firstname = cursor.fetchall(
        )
        cursor.execute(
            "SELECT lastname FROM lastname WHERE person_id = %s",
            (person_id,)
        )
        lastname = cursor.fetchall(
        )

        result = {
            "id": person[0],
            "birth_date": person[1],
            "death_date": person[2],
            "firstnames": [row[0] for row in firstname],
            "lastnames": [row[0] for row in lastname]
        }

        return result

    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        db.close()


@router.patch("/persons/{person_id}", tags=["Person"])
#def Update_information_about_a_specific_person(person_id: int, update_person: PersonCreate, firstname_id: int = None, lastname_id: int = None):
def Update_birth_date_or_death_date_of_a_person(person_id: int, update_person: PersonUpdate):
    """ Updates a person's date of birth or date of death only """
    db = get_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT id, birth_date, death_date FROM person WHERE id = %s",
            (person_id,)
        )
        person = cursor.fetchone()

        # Keep old value if no new value was sent
        new_birth = update_person.birth_date if update_person.birth_date else person[1]
        new_death = update_person.death_date if update_person.death_date else person[2]

        cursor.execute(
            "UPDATE person SET birth_date = %s, death_date = %s WHERE id = %s",
            (new_birth, new_death, person_id)
        )
        db.commit()

        return {
            "id":         person_id,
            "birth_date": str(new_birth) if new_birth else None,
            "death_date": str(new_death) if new_death else None,
        }

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        db.close()


@router.delete("/persons/{person_id}", status_code=201, tags=["Person"])
def Delete_a_specific_person(person_id: int):
    """
    Deletes a person permanently.
    Their names and relationships will be deleted automatically as well (CASCADE).
    """
    db = get_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM person WHERE id = %s", (person_id,))
        db.commit()

        return (f"Person {person_id} deleted successfully")

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        db.close()



