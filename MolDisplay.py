import molecule

# radius = {'H': 25,
#           'C': 40,
#           'O': 40,
#           'N': 40,
#           }
# element_name = {'H': 'grey',
#                 'C': 'black',
#                 'O': 'red',
#                 'N': 'blue',
#                 }

header = """<svg version="1.1" width="1000" height="1000"
xmlns="http://www.w3.org/2000/svg">"""

footer = """</svg>"""

offsetx = 500
offsety = 500


class Atom:
    def __init__(self, c_atom):
        self.atom = c_atom
        self.z = c_atom.z

    def __str__(self):
        # Return string
        return "element: {} x: {} y: {} z: {}".format(self.atom.element, self.atom.x, self.atom.y, self.atom.z)

    def svg(self):
        # Computing values
        cx = (self.atom.x * 100.0) + offsetx
        cy = (self.atom.y * 100.0) + offsety
        r = radius[self.atom.element]
        fill = element_name[self.atom.element]
        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (cx, cy, r, fill)


class Bond:
    def __init__(self, c_bond):
        self.bond = c_bond
        self.z = c_bond.z

    def __str__(self):
        # Return string
        return "a1: {} a2: {} epairs: {} x1: {} y1: {} x2: {} y2: {} len: {} dx: {} dy: {}".format(self.bond.a1, self.bond.a2, self.bond.epairs, self.bond.x1, self.bond.y1, self.bond.x2, self.bond.y2, self.bond.len, self.bond.dx, self.bond.dy)

    def svg(self):

        # Formula to calculate x and y coordinates
        p1x = self.bond.x1 * 100 + offsetx - (self.bond.dy * 10.0)
        p2x = self.bond.x1 * 100 + offsetx + (self.bond.dy * 10.0)
        p3x = self.bond.x2 * 100 + offsetx + (self.bond.dy * 10.0)
        p4x = self.bond.x2 * 100 + offsetx - (self.bond.dy * 10.0)

        p1y = self.bond.y1 * 100 + offsety + (self.bond.dx * 10.0)
        p2y = self.bond.y1 * 100 + offsety - (self.bond.dx * 10.0)
        p3y = self.bond.y2 * 100 + offsety - (self.bond.dx * 10.0)
        p4y = self.bond.y2 * 100 + offsety + (self.bond.dx * 10.0)

        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y)


class Molecule(molecule.molecule):

    def __str__(self):
        my_string = ""

        # Make array of bonds and atoms
        for i in range(self.atom_no):
            my_string += Atom(self.get_atom(i)).__str__()

        for i in range(self.bond_no):
            my_string += Bond(self.get_bond(i)).__str__()

        return my_string

    def svg(self):
        atoms_arr = []
        bonds_arr = []
        arr = []
        my_string = ""

        # Array of atoms
        for i in range(self.atom_no):
            atoms_arr.append(self.get_atom(i))

        # Array of bonds
        for i in range(self.bond_no):
            bonds_arr.append(self.get_bond(i))

        # Call built in sort function
        atoms_arr.sort(key=lambda x: x.z)
        bonds_arr.sort(key=lambda x: x.z)

        i = 0
        j = 0
        k = 0

        while i < self.atom_no and j < self.bond_no:
            # sort z values of atoms and bonds
            if atoms_arr[i].z < bonds_arr[j].z:
                arr.append(Atom(atoms_arr[i]))
                i += 1
            else:
                arr.append(Bond(bonds_arr[j]))
                j += 1
            k += 1

        # See if anything was missing
        while i < self.atom_no:
            arr.append(Atom(atoms_arr[i]))
            i += 1
            k += 1

        while j < self.bond_no:
            arr.append(Bond(bonds_arr[j]))
            j += 1
            k += 1

        # Convert to string
        for m in arr:
            my_string = my_string + m.svg()

        return f'{header}{my_string}{footer}'

    def parse(self, file):
        arr = []

        # Skip three lines
        for i in range(3):
            skip_lines = file.readline()

        # Store content of 4th line
        var = file.readline().split()

        # Atom number
        num1 = int(var[0])
        # Bond number
        num2 = int(var[1])

        for i in range(num1):
            arr = file.readline().split()
            self.append_atom(arr[3], float(arr[0]),
                             float(arr[1]), float(arr[2]))
            

        for i in range(num2):
            arr = file.readline().split()
            self.append_bond(int(arr[0])-1, int(arr[1])-1, int(arr[2]))
