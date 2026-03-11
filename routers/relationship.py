from fastapi import APIRouter, HTTPException
import mysql.connector
from pydantic import BaseModel
from database.connection import get_connection

router = APIRouter()


VALID_RELATIONSHIP_TYPES = ["biological", "adoptive", "step", "other"] #The only 4 allowed relationship types


class ParentAdd(BaseModel):
    parent_id:         int
    relationship_type: str = "biological"  # default is biological 



@router.post("/persons/{person_id}/parents", status_code=201, tags=["Relationships"])
def Add_a_new_parent_to_a_person(person_id: int, body: ParentAdd):
    """ This will create only a parent for a specific person using the person_id """

    # CONSTRAINT: valid relationship type 
    if body.relationship_type not in VALID_RELATIONSHIP_TYPES:      # if client write other than biological", "adoptive", "step", "other
        raise HTTPException(                                        # it will raise an error
            status_code=400,
            detail=f"relationship_type must be one of: {VALID_RELATIONSHIP_TYPES}"
        )

    # CONSTRAINT: a person cannot be their own parent 
    if body.parent_id == person_id:                               # person_id "1" = person_id "1" is not allowed
        raise HTTPException(
            status_code=400,
            detail="A person cannot be their own parent"
        )

    db     = get_connection()
    cursor = db.cursor()
    try:
            # CONSTRAINT: child must exist 
            cursor.execute("SELECT id FROM person WHERE id = %s", (person_id,))    #check the person_id if it exist and if not it will raise an error
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Person with id={person_id} not found"
                )

            # CONSTRAINT: parent must exist 
            cursor.execute("SELECT id FROM person WHERE id = %s", (body.parent_id,))  #check the parent_id if it exist and if not it will raise an error
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Parent with id={body.parent_id} not found"
                )

            # CONSTRAINT: max 2 biological parents 
            # SQL cannot count and compare like this automatically
            if body.relationship_type == "biological":                  # this will count how many biological parent and it should not be greater than 2
                cursor.execute(
                    "SELECT COUNT(*) FROM relationship WHERE child_id = %s AND type = 'biological'",
                    (person_id,)
                )
                total_biological = cursor.fetchone()[0]
                if total_biological >= 2:                               # if total is more than 2 then it will raise an error 400
                    raise HTTPException(
                        status_code=400,
                        detail="A person cannot have more than 2 biological parents"
                    )

            # CONSTRAINT: parent must be born before child
            # SQL cannot join and compare two rows like this automatically
            cursor.execute("SELECT birth_date FROM person WHERE id = %s", (body.parent_id,))    # get the parents birth date 
            parent_row = cursor.fetchone()                                                  

            cursor.execute("SELECT birth_date FROM person WHERE id = %s", (person_id,))         # get the child birth date
            child_row = cursor.fetchone()

            if parent_row and child_row:              #Check both rows exist / if null then obviously we can't compare       
                parent_birth = parent_row[0]           # Extract the actual date from the tuple
                child_birth  = child_row[0]
                # Only check if BOTH dates are known
                if parent_birth and child_birth and parent_birth >= child_birth:   #Parent_birth must be born before child
                    raise HTTPException(
                        status_code=400,
                        detail=f"Parent (born {parent_birth}) must be born before child (born {child_birth})"
                    )

            # CONSTRAINT: no cycles in the family tree 
            # SQL cannot do recursive tree traversal automatically
            # We walk UP the tree from parent_id.
            # If we find person_id in the ancestors -> cycle -> BLOCKED
            cursor.execute(""" 
                WITH RECURSIVE ancestors AS (            # This creates a temporary table called ancestors that builds itself step by step /like climbing up a family tree.
                    SELECT relationship.parent_id         #        
                    FROM relationship 
                    WHERE relationship.child_id = %s

                    UNION ALL

                    SELECT relationship.parent_id
                    FROM relationship 
                    JOIN ancestors  ON relationship.child_id = ancestors.parent_id
                )
                SELECT COUNT(*) FROM ancestors WHERE parent_id = %s
            """, (body.parent_id, person_id))
                # The code starts from the child and moves upward through every generation of parents. 
                # It keeps going until it reaches the top of the family tree. 
                # Then it checks whether the new parent already appears in that line. 
                # If it does, the relationship would create a cycle, so it is rejected.
            cycle_found = cursor.fetchone()[0]    #
            if cycle_found > 0:
                raise HTTPException(
                    status_code=400,
                    detail="This relationship would create a cycle in the family tree"
                )

            # ALL CHECKS PASSED → save the relationship 
            cursor.execute(
                "INSERT INTO relationship (parent_id, child_id, type) VALUES (%s, %s, %s)",
                (body.parent_id, person_id, body.relationship_type)
            )
            db.commit()

            return {
                "message":           "Parent added successfully",
                "child_id":          person_id,
                "parent_id":         body.parent_id,
                "relationship_type": body.relationship_type
            }

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        db.close()

@router.get("/persons/{person_id}/parents", tags=["Relationships"])
def Get_all_parents_of_person(person_id: int):
    """Returns all parents of a person using the person_id."""
    db     = get_connection()
    cursor = db.cursor()

    try:
        # CONSTRAINT: person must exist 
        cursor.execute("SELECT id FROM person WHERE id = %s", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Person with id={person_id} not found"
            )

        # JOIN gets the parent's names in the same query
        # GROUP_CONCAT combines multiple names into one string
        cursor.execute("""
            SELECT
                relationship.id,
                relationship.type,
                person.id,
                person.birth_date,
                person.death_date,
                GROUP_CONCAT(DISTINCT firstname.firstname ORDER BY firstname.id SEPARATOR ' ')  AS firstnames,       #GROUP_CONCAT is an SQL function that joins several values from different rows into one single text. 
                GROUP_CONCAT(DISTINCT lastname.lastname  ORDER BY l.id SEPARATOR ', ') AS lastnames                  # example yacine avatar blah
            FROM relationship 
            JOIN person  ON person.id = relationship.parent_id
            LEFT JOIN firstname  ON firstname.person_id = person.id
            LEFT JOIN lastname   ON lastname.person_id = person.id
            WHERE relationship.child_id = %s
            GROUP BY relationship.id, person.id, relationship.type
            ORDER BY relationship.type, person.id
        """, (person_id,))
        #It looks for all relationships where the given person is the child, 
        # finds the related parents, gets their birth and death dates, 
        # collects all their first names and last names, and shows the result in an organized list.
        rows = cursor.fetchall()

        return [
            {
                "relationship_id":   row[0],
                "relationship_type": row[1],
                "parent_id":         row[2],
                "birth_date":        str(row[3]) if row[3] else None,
                "death_date":        str(row[4]) if row[4] else None,
                "firstnames":        row[5],
                "lastnames":         row[6],
            }
            for row in rows
        ]

    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        db.close()


@router.get("/persons/{person_id}/children", tags=["Relationships"])
def Get_all_children_of_person(person_id: int):
    """Returns all children of a person."""
    db     = get_connection()
    cursor = db.cursor()

    try:
        # CONSTRAINT: person must exist 
        cursor.execute("SELECT id FROM person WHERE id = %s", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Person with id={person_id} not found"
            )

        cursor.execute("""
            SELECT
                relationship.id,
                relationship.type,
                person.id,
                person.birth_date,
                person.death_date,
                GROUP_CONCAT(DISTINCT firstname.firstname ORDER BY firstname.id SEPARATOR ' ')  AS firstnames,
                GROUP_CONCAT(DISTINCT lastname.lastname  ORDER BY lastname.id SEPARATOR ', ') AS lastnames
            FROM relationship 
            JOIN person ON person.id = relationship.child_id
            LEFT JOIN firstname ON firstname.person_id = person.id
            LEFT JOIN lastname ON lastname.person_id = person.id
            WHERE relationship.parent_id = %s
            GROUP BY relationship.id, person.id, relationship.type
            ORDER BY relationship.type, person.id
        """, (person_id,))
        #This code searches for all children of the given parent, 
        # collects each child’s information and names, and saves all the results in rows
        rows = cursor.fetchall()

        return [
            {
                "relationship_id":   row[0],
                "relationship_type": row[1],
                "child_id":          row[2],
                "birth_date":        str(row[3]) if row[3] else None,
                "death_date":        str(row[4]) if row[4] else None,
                "firstnames":        row[5],
                "lastnames":         row[6],
            }
            for row in rows
        ]

    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        db.close()


@router.delete("/persons/{person_id}/parents/{parent_id}", tags=["Relationships"])
def Remove_parent(person_id: int, parent_id: int):
    """Removes the relationship between a parent and a child."""
    db     = get_connection()
    cursor = db.cursor()

    try:
        # CONSTRAINT: both people must exist 
        cursor.execute("SELECT id FROM person WHERE id = %s", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Person with id={person_id} not found"
            )

        cursor.execute("SELECT id FROM person WHERE id = %s", (parent_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Parent with id={parent_id} not found"
            )

        cursor.execute(
            "DELETE FROM relationship WHERE parent_id = %s AND child_id = %s",
            (parent_id, person_id)
        )
        db.commit()

        # CONSTRAINT: relationship must exist
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="No relationship found between these two people"
            )

        return {"message": "Parent removed successfully"}

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        db.close()