# API Documentation

Base URL: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

---

## Database Schema

The database has 4 tables:

**person** — stores dates only
| Column | Type | Notes |
|--------|------|-------|
| id | INT | auto-generated |
| birth_date | DATE | optional |
| death_date | DATE | optional, must be after birth_date |

**firstname** — one row per firstname
| Column | Type | Notes |
|--------|------|-------|
| id | INT | auto-generated |
| person_id | INT | links to person.id |
| firstname | VARCHAR | cannot be empty |

**lastname** — one row per lastname
| Column | Type | Notes |
|--------|------|-------|
| id | INT | auto-generated |
| person_id | INT | links to person.id |
| lastname | VARCHAR | optional |

**relationship** — one row per parent-child link
| Column | Type | Notes |
|--------|------|-------|
| id | INT | auto-generated |
| parent_id | INT | links to person.id |
| child_id | INT | links to person.id |
| type | ENUM | biological, adoptive, step, other |

---

## Business Rules

| # | Rule | Enforced by |
|---|------|-------------|
| 1 | A person must have at least one firstname | API |
| 2 | Birth date must be before death date | SQL CHECK |
| 3 | Firstname cannot be empty or blank | SQL CHECK + Pydantic |
| 4 | Max 2 biological parents | API |
| 5 | Parent must be born before child | API |
| 6 | No cycles in the family tree | API |
| 7 | A person cannot be their own parent | API |
| 8 | No duplicate relationships | SQL UNIQUE |
| 9 | Deleting a person deletes their names and relationships | SQL CASCADE |

---

## API Routes

---

### Persons

#### POST /persons
Creates a new person. At least one firstname is required.

Request body:
```json
{
    "firstnames": ["Bob", "Robert"],
    "lastnames":  ["Lowblow"],
    "birth_date": "1901-01-01",
    "death_date": null
}
```

Minimum request body:
```json
{
    "firstnames": ["Bob"]
}
```

Response `201`:
```json
{
    "id": 1,
    "birth_date": "1901-01-01",
    "death_date": null,
    "firstnames": ["Bob"],
    "lastnames": ["Lowblow"]
}
```

---

#### GET /persons
Returns all persons in the database.

Response `200`:
```json
[
    {
        "id": 1,
        "birth_date": "1901-01-01",
        "death_date": null,
        "firstnames": [{"id": 1, "firstname": "Bob"}],
        "lastnames":  [{"id": 1, "lastname": "Lowblow"}]
    }
]
```

---

#### GET /persons/{person_id}
Returns one person by their ID.

Response `200`:
```json
{
    "id": 1,
    "birth_date": "1901-01-01",
    "death_date": null,
    "firstnames": [{"id": 1, "firstname": "Bob"}],
    "lastnames":  [{"id": 1, "lastname": "Lowblow"}]
}
```

Response `404` — person not found:
```json
{ "detail": "Person with id=99 not found" }
```

---

#### PATCH /persons/{person_id}
Adds or updates the birth date and/or death date.
Only send the field you want to change.
Send `null` to remove a date.

Request body examples:
```json
{ "birth_date": "1901-01-01" }
```
```json
{ "death_date": "1999-12-31" }
```
```json
{ "birth_date": "1901-01-01", "death_date": "1999-12-31" }
```
```json
{ "birth_date": null }
```

Response `200`:
```json
{
    "id": 1,
    "birth_date": "1901-01-01",
    "death_date": "1999-12-31"
}
```

---

#### DELETE /persons/{person_id}
Deletes a person permanently.
Their firstnames, lastnames and relationships are deleted automatically (CASCADE).

Response `200`:
```json
{ "message": "Person 1 deleted successfully" }
```

---

### Names

#### POST /persons/{person_id}/firstnames
Adds a new firstname to an existing person.

Request body:
```json
{ "firstname": "Jean" }
```

Response `201`:
```json
{
    "id": 3,
    "person_id": 1,
    "firstname": "Jean"
}
```

---

#### PUT /persons/{person_id}/firstnames/{firstname_id}
Renames an existing firstname.

Request body:
```json
{ "firstname": "Robert" }
```

Response `200`:
```json
{
    "id": 3,
    "person_id": 1,
    "firstname": "Robert"
}
```

---

#### DELETE /persons/{person_id}/firstnames/{firstname_id}
Removes a firstname from a person.

Response `200`:
```json
{ "message": "Firstname deleted successfully" }
```

---

#### POST /persons/{person_id}/lastnames
Adds a new lastname to an existing person.

Request body:
```json
{ "lastname": "Lowblow" }
```

Response `201`:
```json
{
    "id": 2,
    "person_id": 1,
    "lastname": "Lowblow"
}
```

---

#### PUT /persons/{person_id}/lastnames/{lastname_id}
Renames an existing lastname.

Request body:
```json
{ "lastname": "Dupont" }
```

---

#### DELETE /persons/{person_id}/lastnames/{lastname_id}
Removes a lastname from a person.

Response `200`:
```json
{ "message": "Lastname deleted successfully" }
```

---

### Relationships

#### POST /persons/{person_id}/parents
Adds a parent to a person.

Request body:
```json
{
    "parent_id": 2,
    "relationship_type": "biological"
}
```

Allowed relationship types: `biological`, `adoptive`, `step`, `other`
Default: `biological`

Response `201`:
```json
{
    "message": "Parent added successfully",
    "child_id": 1,
    "parent_id": 2,
    "relationship_type": "biological"
}
```

Error examples:
```json
{ "detail": "A person cannot have more than 2 biological parents" }
{ "detail": "Parent must be born before child" }
{ "detail": "This relationship would create a cycle in the family tree" }
{ "detail": "A person cannot be their own parent" }
```

---

#### GET /persons/{person_id}/parents
Returns all parents of a person.

Response `200`:
```json
[
    {
        "relationship_id": 1,
        "relationship_type": "biological",
        "parent_id": 2,
        "birth_date": "1870-05-01",
        "death_date": null,
        "firstnames": "John",
        "lastnames": "Lowblow"
    }
]
```

---

#### GET /persons/{person_id}/children
Returns all children of a person.

Response `200`:
```json
[
    {
        "relationship_id": 1,
        "relationship_type": "biological",
        "child_id": 1,
        "birth_date": "1901-01-01",
        "death_date": null,
        "firstnames": "Bob",
        "lastnames": "Lowblow"
    }
]
```

---

#### DELETE /persons/{person_id}/parents/{parent_id}
Removes the relationship between a parent and a child.

Response `200`:
```json
{ "message": "Parent removed successfully" }
```
