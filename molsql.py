import os
import sqlite3
from MolDisplay import Atom, Bond, Molecule
import MolDisplay


class Database:

    def __init__(self, reset=False):
        if reset == True:
            if os.path.isfile('molecules.db'):
                os.remove('molecules.db')

        # Connection to the database
        self.conn = sqlite3.connect('molecules.db')

    def create_tables(self):
        # Create table for elements
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Elements(
            ELEMENT_NO INTEGER NOT NULL,
            ELEMENT_CODE VARCHAR(3) NOT NULL PRIMARY KEY,
            ELEMENT_NAME VARCHAR(3) NOT NULL,
            COLOUR1 CHAR(6) NOT NULL,
            COLOUR2 CHAR(6) NOT NULL,
            COLOUR3 CHAR(6) NOT NULL,
            RADIUS DECIMAL(3) NOT NULL);""")

        # Create table for atoms
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms(
            ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            ELEMENT_CODE VARCHAR(3) NOT NULL REFERENCES Elements(ELEMENT_CODE),
            X DECIMAL(7,4) NOT NULL,
            Y DECIMAL(7,4) NOT NULL,
            Z DECIMAL(7,4) NOT NULL);""")

        # Create table for bonds
        self.conn.execute(""" CREATE TABLE IF NOT EXISTS Bonds(
            BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
            A1 INTEGER NOT NULL,
            A2 INTEGER NOT NULL,
            EPAIRS INTEGER NOT NULL);""")

        # Creates a table for molecules
        self.conn.execute(""" CREATE TABLE IF NOT EXISTS Molecules(
            MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            NAME TEXT UNIQUE NOT NULL); """)

        # Creates a table for molecule atom
        self.conn.execute(""" CREATE TABLE IF NOT EXISTS MoleculeAtom(
            MOLECULE_ID INTEGER NOT NULL REFERENCES Molecules(MOLECULE_ID),
            ATOM_ID INTEGER NOT NULL REFERENCES Atoms(ATOM_ID),
            PRIMARY KEY(MOLECULE_ID,ATOM_ID));""")

        # Creates a table for molecule bond
        self.conn.execute(""" CREATE TABLE IF NOT EXISTS MoleculeBond(
            MOLECULE_ID INTEGER NOT NULL REFERENCES Molecules(MOLECULE_ID),
            BOND_ID INTEGER NOT NULL REFERENCES Bonds(BOND_ID),
            PRIMARY KEY(MOLECULE_ID,BOND_ID));""")

    def __setitem__(self, table, values):
        # Make string
        temp = "("+",".join(["?"] * len(values)) + ")"
        search = f"INSERT INTO {table} VALUES {temp}"
        # Execute query and commit changes
        self.conn.execute(search, values)
        self.conn.commit()

    def add_atom(self, molname, atom):
        # Insert new atom
        search = f"INSERT INTO Atoms (ELEMENT_CODE,X,Y,Z) VALUES ('{atom.atom.element}',{atom.atom.x},{atom.atom.y},{atom.atom.z})"
        cursor = self.conn.cursor()
        cursor.execute(search)
        # Save changes
        self.conn.commit()
        # Get the ID of the atom
        atomID = cursor.lastrowid

        # Get molecile ID with molname
        search = f"SELECT MOLECULE_ID FROM Molecules WHERE NAME = '{molname}'"
        cursor.execute(search)
        # Get molecule ID
        mol = cursor.fetchone()[0]

        # Add row to MoleculeAtom table
        search = f"INSERT INTO MoleculeAtom VALUES ({mol},{atomID})"
        cursor.execute(search)
        # Commit changes
        self.conn.commit()

    def add_bond(self, molname, bond):
        # Insert new bond
        search = f"INSERT INTO Bonds (A1,A2,EPAIRS) VALUES ({bond.bond.a1},{bond.bond.a2},{bond.bond.epairs})"
        cursor = self.conn.cursor()
        cursor.execute(search)
        # Save changes
        self.conn.commit()
        # Get the ID of the bond
        bondID = cursor.lastrowid

        # Get molecile ID with molname
        search = f"SELECT MOLECULE_ID FROM Molecules WHERE NAME = '{molname}'"
        cursor.execute(search)
        # Get molecule ID
        mol = cursor.fetchone()[0]

        # Add row to MoleculeBond table
        search = f"INSERT INTO MoleculeBond VALUES ({mol}, {bondID})"
        cursor.execute(search)
        # Commit changes
        self.conn.commit()

    def add_molecule(self, name, fp):
        # Create object
        mol = Molecule()
        mol.parse(fp)
        # Add row to Molecules table
        entry = f"INSERT INTO Molecules (NAME) VALUES (?)"
        self.conn.execute(entry, (name,))
        # Commit changes
        self.conn.commit()

        for i in range(mol.atom_no):
            atom = Atom(mol.get_atom(i))
            codeEl = atom.atom.element
            entry = f"INSERT INTO Elements (ELEMENT_NO, ELEMENT_CODE, ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3, RADIUS) \
                    SELECT 1, '{codeEl}', '{codeEl}', '00FF00', 'e2a286', '800080', 30 \
                    WHERE NOT EXISTS (SELECT 1 FROM Elements WHERE ELEMENT_CODE = '{codeEl}')"

            self.conn.execute(entry)
            self.add_atom(name, atom)
            self.conn.commit()

        # Loop through bonds
        for i in range(mol.bond_no):
            self.add_bond(name, Bond(mol.get_bond(i)))

    def load_mol(self, name):
        # Create object
        mol = MolDisplay.Molecule()
        # Retrieve all atoms
        search = f"""SELECT * FROM Atoms JOIN MoleculeAtom ON Atoms.ATOM_ID = MoleculeAtom.ATOM_ID
        JOIN Molecules ON MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID
        WHERE Molecules.NAME = ? ORDER BY ATOM_ID ASC"""
        response = self.conn.execute(search, (name,)).fetchall()

        # Loop through atoms and append it
        for atom in response:
            mol.append_atom(atom[1], atom[2], atom[3], atom[4])

        # Retrieve all bonds
        search = f""" SELECT * FROM Bonds JOIN MoleculeBond ON Bonds.BOND_ID = MoleculeBond.BOND_ID
        JOIN Molecules ON MoleculeBond.MOLECULE_ID = Molecules.MOLECULE_ID
        WHERE Molecules.NAME = ? ORDER BY BOND_ID ASC"""
        response = self.conn.execute(search, (name,)).fetchall()

        # Loop through bonds and append it
        for bond in response:
            mol.append_bond(bond[1], bond[2], bond[3])

        # Return object
        return mol

    def radius(self):
        # Create dictionary
        myDictionary = {}
        # Get element code and radius
        search = f"SELECT ELEMENT_CODE, RADIUS FROM Elements"
        response = self.conn.execute(search).fetchall()

        # Add to dictionary
        for i in response:
            myDictionary[i[0]] = i[1]

        # Return dictionary
        return myDictionary

    def element_name(self):
        # Create dictionary
        myDictionary = {}
        # Get element code and elemenr name
        search = f"SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements"
        response = self.conn.execute(search).fetchall()

        # Add to dictionary
        for i in response:
            myDictionary[i[0]] = i[1]

        # Return dictionary
        return myDictionary

    def radial_gradients(self):
        myString = ""

        # Get element names and colours
        search = f"SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements"
        response = self.conn.execute(search).fetchall()

        for i in response:
            # SVG Code
            radialGradientSVG = """
<radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
  <stop offset="0%%" stop-color="#%s"/>
  <stop offset="50%%" stop-color="#%s"/>
  <stop offset="100%%" stop-color="#%s"/>
</radialGradient>""" % (i[0], i[1], i[2], i[3])

            myString = myString + radialGradientSVG

        # Return string
        return myString

    def test(self, remove):
        cursor = self.conn.cursor()
        # Delete element form table
        cursor.execute(
            """DELETE FROM Elements WHERE ELEMENT_NAME = ?""", (remove,))
        # Commit changes
        self.conn.commit()

    def obtainMol(self):
        # Connect to Database
        conn = sqlite3.connect('molecules.db')
        cursor = conn.cursor()

        # Query to get data
        cursor.execute("""
            SELECT Molecules.NAME, COUNT(DISTINCT Bonds.BOND_ID), COUNT(DISTINCT Atoms.ATOM_ID)
            FROM Molecules
            JOIN MoleculeBond ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
            JOIN Bonds ON MoleculeBond.BOND_ID = Bonds.BOND_ID
            JOIN MoleculeAtom ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
            JOIN Atoms ON MoleculeAtom.ATOM_ID = Atoms.ATOM_ID
            GROUP BY Molecules.MOLECULE_ID
        """)

        # Get data and store it
        data = [{
            "name": name,
            "numBond": numBond,
            "numAtom": numAtom
        } for name, numBond, numAtom in cursor.fetchall()]

        cursor.close()
        conn.close()

        # Return dictionary
        return data
