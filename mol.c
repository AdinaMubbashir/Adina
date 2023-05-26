#include "mol.h"


// Copies values pointed to by element x,y, and z into the atom stored at atom
void atomset(atom *atom, char element[3], double *x, double *y, double *z)
{

    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
    strcpy(atom->element, element);
}

// Copies values in the atom stored at atom to the location pointed by element x,y, and z
void atomget(atom *atom, char element[3], double *x, double *y, double *z)
{
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
    strcpy(element, atom->element);
}

// Copies the values a1, a2 and epairs into the corresponding structure attributes in bond
void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs)
{
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->epairs = *epairs;
    bond->atoms = *atoms;
}

// Copies the structure attributes in bond to their corresponding arguments: a1, a2 and epairs
void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs)
{
    *a1 = bond->a1;
    *a2 = bond->a2;
    *atoms = bond->atoms;
    *epairs = bond->epairs;
    compute_coords(bond); //Function call
}

void compute_coords(bond *bond)
{
    //Calculate average of a1 and a2 z values
    bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2;

    //Coordinates
    bond->x1 = bond->atoms[bond->a1].x;
    bond->x2 = bond->atoms[bond->a2].x;

    bond->y1 = bond->atoms[bond->a1].y;
    bond->y2 = bond->atoms[bond->a2].y;

    //Distance from a1 to a2
    bond->len = sqrt(((bond->x2 - bond->x1) * (bond->x2 - bond->x1)) + ((bond->y2 - bond->y1) * (bond->y2 - bond->y1)));
    
    //Differences between x and y values of bond
    bond->dx = (bond->x2 - bond->x1) / bond->len;
    bond->dy = (bond->y2 - bond->y1) / bond->len;
}

// Returns the address of the malloced area of memory
molecule *molmalloc(unsigned short atom_max, unsigned short bond_max)
{
    // Create temp variable
    molecule *store = (molecule *)malloc(sizeof(molecule));
    // Check to see if memory allocation failed
    if (store == NULL)
    {
        fprintf(stderr, "Malloc/Realloc has failed"); // Print message
        molfree(store);
        return NULL;
    }

    store->atom_max = atom_max;
    store->bond_max = bond_max;

    store->atom_no = 0;
    store->bond_no = 0;

    store->atoms = (atom *)malloc(sizeof(atom) * atom_max);
    // Check to see if memory allocation failed
    if (store->atoms == NULL)
    {
        fprintf(stderr, "Malloc/Realloc has failed"); // Print message
        molfree(store);
        return NULL;
    }

    store->atom_ptrs = (atom **)malloc(sizeof(struct atom *) * atom_max);
    // Check to see if memory allocation failed
    if (store->atom_ptrs == NULL)
    {
        fprintf(stderr, "Malloc/Realloc has failed"); // Print message
        molfree(store);
        return NULL;
    }

    store->bonds = (bond *)malloc(sizeof(bond) * bond_max);
    // Check to see if memory allocation failed
    if (store->bonds == NULL)
    {
        fprintf(stderr, "Malloc/Realloc has failed"); // Print message
        molfree(store);
        return NULL;
    }

    store->bond_ptrs = (bond **)malloc(sizeof(struct bond *) * bond_max);
    // Check to see if memory allocation failed
    if (store->bond_ptrs == NULL)
    {
        fprintf(stderr, "Malloc/Realloc has failed"); // Print message
        molfree(store);
        return NULL;
    }

    // Returns address of malloced area of memory
    return store;
}

// Returns the address of the malloced area of memory
molecule *molcopy(molecule *src)
{

    molecule *mole;

    mole = molmalloc(src->atom_max, src->bond_max); // malloc memory
    // Check to see if memory allocation failed
    if (mole == NULL)
    {
        fprintf(stderr, "Malloc/Realloc has failed"); // Print message
        return NULL;
    }

    for (int i = 0; i < src->atom_no; i++)
    { // Copy into new structure
        molappend_atom(mole, &src->atoms[i]);
    }

    for (int i = 0; i < src->bond_no; i++)
    { // Copy into new structure
        molappend_bond(mole, &src->bonds[i]);
    }

    return mole;
}

// Free memory
void molfree(molecule *ptr)
{
    free(ptr->atoms);
    free(ptr->atom_ptrs);
    free(ptr->bonds);
    free(ptr->bond_ptrs);
    free(ptr);
}

// Copies the data pointed to by atom to the first “empty” atom in atoms in the molecule pointed to by molecule
void molappend_atom(molecule *molecule, atom *atom)
{
    // Check if maximum size is reached
    if (molecule->atom_no == molecule->atom_max)
    {

        if (molecule->atom_max == 0) // If atom_max is 0, it is set to 0
        {
            molecule->atom_max += 1;
        }
        else
        {
            molecule->atom_max *= 2; // Size of atom_max is doubled
        }

        molecule->atoms = (struct atom *)realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max); // realloc size
        if (molecule->atoms == NULL)
        {
            fprintf(stderr, "Malloc/Realloc has failed");
            molfree(molecule);
            exit(-1); // Exit if realloc failed
        }
        molecule->atom_ptrs = (struct atom **)realloc(molecule->atom_ptrs, sizeof(struct atom *) * molecule->atom_max); // realloc size
        if (molecule->atom_ptrs == NULL)
        {
            fprintf(stderr, "Malloc/Realloc has failed");
            molfree(molecule);
            exit(-1); // Exit if realloc failed
        }
    }

    // Copy data into empty space
    molecule->atoms[molecule->atom_no] = *atom;

    for (int i = 0; i <= molecule->atom_no; i++)
    {
        // Point to the corresponding atoms in the new atoms array
        molecule->atom_ptrs[i] = &molecule->atoms[i];
    }

    molecule->atom_no++;
}

// Copies the data pointed to by bond to the first “empty” bond in bonds in the molecule pointed to by molecule
void molappend_bond(molecule *molecule, bond *bond)
{
    // Check if maximum size is reached
    if (molecule->bond_no == molecule->bond_max)
    {

        if (molecule->bond_max == 0) // If bond_max is 0, it is set to 0
        {
            molecule->bond_max += 1;
        }
        else
        {
            molecule->bond_max *= 2; // Size of bond_max is doubled
        }

        molecule->bonds = (struct bond *)realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max); // realloc size
        if (molecule->bonds == NULL)
        {
            fprintf(stderr, "Malloc/Realloc has failed");
            molfree(molecule);
            exit(-1); // Exit if realloc failed
        }
        molecule->bond_ptrs = (struct bond **)realloc(molecule->bond_ptrs, sizeof(struct atom *) * molecule->bond_max); // realloc size
        if (molecule->bond_ptrs == NULL)
        {
            fprintf(stderr, "Malloc/Realloc has failed");
            molfree(molecule);
            exit(-1); // Exit if realloc failed
        }
    }

    // Copy data into empty space
    molecule->bonds[molecule->bond_no] = *bond;

    for (int i = 0; i <= molecule->bond_no; i++)
    {
        // Point to the corresponding bonds in the new bonds array
        molecule->bond_ptrs[i] = &molecule->bonds[i];
    }

    molecule->bond_no++;
}

// Compare function for atom
int atom_cmp(const void *a, const void *b)
{
    double z1 = (*(atom **)a)->z;
    double z2 = (*(atom **)b)->z;

    double num = 0.0;

    if (z1 > z2)
    {
        num = 1;
    }
    else if (z1 < z2)
    {
        num = -1;
    }
    else if (z1 == z2)
    {
        num = 0;
    }

    return num;
}

// Compare function for bond
int bond_cmp(const void *a, const void *b)
{

    double z1 = (*(bond **)a)->z;
    double z2 = (*(bond **)b)->z;

    double num = 0.0;

    if (z1 > z2)
    {
        num = 1;
    }
    else if (z1 < z2)
    {
        num = -1;
    }
    else if (z1 == z2)
    {
        num = 0;
    }

    return num;
}

void molsort(molecule *molecule)
{
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom *), atom_cmp);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond *), bond_cmp);
}

// Set values for x rotation
void xrotation(xform_matrix xform_matrix, unsigned short deg)
{
    double rad = deg * (M_PI / 180.0);

    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = -sin(rad);
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(rad);
    xform_matrix[2][2] = cos(rad);
}

// Set values for y rotation
void yrotation(xform_matrix xform_matrix, unsigned short deg)
{
    double rad = deg * (M_PI / 180.0);

    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(rad);
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = -sin(rad);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(rad);
}

// Set values for z rotation
void zrotation(xform_matrix xform_matrix, unsigned short deg)
{
    double rad = deg * (M_PI / 180.0);

    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = -sin(rad);
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = sin(rad);
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

void mol_xform(molecule *molecule, xform_matrix matrix)
{
    double temp_atom[3];

    for (int i = 0; i < molecule->atom_no; i++)
    {
        temp_atom[0] = molecule->atoms[i].x;
        temp_atom[1] = molecule->atoms[i].y;
        temp_atom[2] = molecule->atoms[i].z;

        atom *temp = molecule->atom_ptrs[i];

        temp->x = matrix[0][0] * temp_atom[0] + matrix[0][1] * temp_atom[1] + matrix[0][2] * temp_atom[2];
        temp->y = matrix[1][0] * temp_atom[0] + matrix[1][1] * temp_atom[1] + matrix[1][2] * temp_atom[2];
        temp->z = matrix[2][0] * temp_atom[0] + matrix[2][1] * temp_atom[1] + matrix[2][2] * temp_atom[2];
    }

    //Call function for each bond in molecule
    for (int i = 0; i < molecule->bond_no; i++)
    {
        compute_coords(&molecule->bonds[i]);
    }
}
