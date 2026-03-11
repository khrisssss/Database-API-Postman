# Constraints 

##  Person

| # |                           Rule                                       |               Example                                |
|---|----------------------------------------------------------------------|------------------------------------------------------|
| 1 | A person must have at least one first name / last name is optional   |   Cannot create a person with no name at all         |
| 2 | Birth date must be before death date                                 |   Born 2000, died 1990 is not logic at all           | 
| 3 | Dates must be real calendar dates ex.                                |   30/02/1990 is invalid (February never has 30 days) |
                                                                              |   00/01/1990 Day 0 doesn't exist                     |
                                                                           |   15/13/1990 Month 13 doesn't exist                  |
                                                                           |    abcd-ef-gh Not a date at all hmmm!                |
                                                                           
## Biological Parents

| 4 | A person can have **at most 2 biological parents**                              |  Adding a 3rd biological parent is a miracle   ;)                          |
| 5 | A child cannot be born **before or on the same day** as their biological parent |  Parent born 1950, child born 1940 is invalid as what Maxime explained     |
| 6 | A parent cannot also be a child of the same person                              |  If Yacine is parent of Noemi, Noemi cannot be parent of Maxime            |

## Adoptive / Step / Other Parents

| 7  | A person can have **unlimited** adoptive, step, or other parents                                  |  Possible/Allowed                                            | 
       (Parents can divorce and remarry → giving a child multiple step-parents)                          |                                                             |
       (A child can be adopted multiple times)                                                           |                                                              |
       (A child can have many legal guardians)                                                           |                                                              |
| 8 | The same chronological rule applies: parent must be born before child (when both dates are known) |  Cannot adopt someone older than you                         |
| 9 | The same cycle rule applies: no circular relationships                                            |  If A is already above B in the tree, A can never go below B |
                                                                                                         |  because that would create an impossible loop.               |
## Relationships (general)
Parents can divorce and remarry → giving a child multiple step-parents
| 10 | A person **cannot be their own parent**                                 |  You cannot give birth to yourself or be your own guardian. |
| 11 | The same parent-child pair with the same type cannot be added twice     |  Duplicate relationships is NOT allowed                     |
| 12 | A relationship must reference two **existing** people                   | Cannot add a parent with an ID that DOES NOT exist          |
| 13 | No **cycles** allowed in the family tree                                |  A → parent of B → parent of C → parent of A is invalid    |

##  Names

| 14 | A person can have **multiple first names** (stored separately)          |  "Jema" + "Khrisly" are two firstnames    |
| 15 | A person can have **multiple last names** (stored separately)           |  "Sucgang" + "Planchon" are two lastnames |
| 16 | Names cannot be empty strings                                           |  `""` is not a valid firstname            |
A person cannot be deleted if they are a parent (unless cascade is enabled)ℹ️ We use CASCADE — deleting a person removes their relationships
---

##  Summary

> - You can be born, live, and die — those dates must make logical sense.
> - You can have 0, 1, or 2 biological parents max.
> - You can have as many adoptive/step parents as needed.
> - No one can be their own ancestor (no time travel ).
> - You can have many firstnames and lastnames.
