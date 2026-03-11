
-- Create the database
CREATE DATABASE IF NOT EXISTS Bob_Family_Tree
  CHARACTER SET utf8mb4       -- support all characters, including accents like é, à, ü and special symbols.
  COLLATE utf8mb4_unicode_ci;


-- Select the database of genealogy to work with
USE Bob_Family_Tree;



CREATE TABLE IF NOT EXISTS person (                   -- store only the dates 
    id int NOT NULL AUTO_INCREMENT,        -- unique number for each person
    birth_date date,
    death_date date,
    PRIMARY KEY (id),
    CONSTRAINT chk_death_after_birth
        CHECK (                          -- RULE: death must be after birth (when both are provided)
            birth_date IS NULL
            OR death_date IS NULL
            OR death_date > birth_date
        )
        -- ON DELETE CASCADE: delete person = delete their firstnames too

);

CREATE TABLE IF NOT EXISTS firstname (                 -- a person can have multiple firstnames, so we store them in a separate table
    id int NOT NULL AUTO_INCREMENT,
    person_id int NOT NULL,
    firstname varchar(50) NOT NULL,
    PRIMARY KEY (id),

    CONSTRAINT chk_firstname_not_empty      -- RULE: firstname cannot be empty
        CHECK (TRIM(firstname) != ''),

        -- ON DELETE CASCADE: delete person = delete their firstnames too
    CONSTRAINT fk_firstname_person
        FOREIGN KEY (person_id)
        REFERENCES person(id)
        ON DELETE CASCADE     
);


CREATE TABLE IF NOT EXISTS lastname (                  -- last name is optional and a person can have zero or multiple lastnames, so we store them in a separate table
    id int NOT NULL AUTO_INCREMENT,
    person_id int NOT NULL,
    lastname varchar(50),
    PRIMARY KEY (id),
        -- ON DELETE CASCADE: delete person = delete their lastnames too
    CONSTRAINT fk_lastname_person
        FOREIGN KEY (person_id)
        REFERENCES person(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relationship ( 
    id int NOT NULL AUTO_INCREMENT,
    parent_id int NOT NULL,
    child_id int NOT NULL,
    PRIMARY KEY (id),

    CONSTRAINT chk_not_self_parent              -- RULE: a person cannot be their own parent
        CHECK (parent_id != child_id),

    UNIQUE KEY unique_relationship (parent_id, child_id)  -- RULE: no duplicate relationship
                                                    -- ex. you cannot add "Yacine is biological parent of Noemi" twice  
);                                                 


SHOW TABLES;

















