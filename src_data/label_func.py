# This needs to be run in an environment with rdkit. I used conda to install
# this library on a windows machine so the commands:
#
# cmd.exe
# conda activate my-rdkit-env
#
# Must be run beforehand

import os
import csv
from rdkit import Chem
from itertools import islice

from pprint import pprint

FUNC_GROUPS = [
    "Alkane".replace(" ", "_").lower(),
    "Alkene".replace(" ", "_").lower(),
    "Alkyne".replace(" ", "_").lower(),
    "Arene".replace(" ", "_").lower(),
    "Ketone".replace(" ", "_").lower(),
    "Ester".replace(" ", "_").lower(),
    "Amide".replace(" ", "_").lower(),
    "Carboxylic_acid".replace(" ", "_").lower(),
    "Alcohol".replace(" ", "_").lower(),
    "Amine".replace(" ", "_").lower(),
    "Nitrile".replace(" ", "_").lower(),
    "Alkyl_halide".replace(" ", "_").lower(),
    "Acyl_Halide".replace(" ", "_").lower(),
    "Ether".replace(" ", "_").lower(),
    "Methyl".replace(" ", "_").lower(),
    "Alkane".replace(" ", "_").lower(),
]

# I've given the same order for the functional groups as the paper.
# Some of these patterns were crossed referenced with the following website:
#   https://www.daylight.com/dayhtml_tutorials/languages/smarts/smarts_examples.html
FUNC_SMARTS = [
    r'[CX4]',  # Alkane^a
    r'[$([CX2]=[X2])]',  # Alkene
    r'[$([CX2]#C)]',  # Alkyne
    r'[c]',  # Arene
    r'[#6][CX3](=O)[#6]',  # Ketone
    r'[#6][CX3](=O)[OX2H0][#6]',  # Ester
    r'[NX3][CX3](=[OX1])[#6]',  # Amide
    r'[CX3](=O)[OX2H1]',  # Carboxylic acid
    r'[CHX4][OX2H]',  # Alcohol
    # Amine, Also written as [NX3;H2,H1;!$(NC=O)].[NX3;H2,H1;!$(NC=O)]
    # where the "disconnection" symbol (".") to match two separate
    # not-necessarily bonded identical patterns.
    r'[NX3;H2,H1;!$(NC=O)]',
    r'[NX1]#[CX2]',  # Nitrile
    r'[CX4][F,Cl,Br,I]',  # Alkyl halide
    r'[CX3](=[OX1])[F,Cl,Br,I]',  # Acyl Halide
    r'[OD2]([#6])[#6]',  # Ether^b
    r'[$([NX3](=O)=O),$([NX3+](=O)[O-])][!#8]',  # nitro^b
    # These are subgroups of Alkane^a
    # r'[CH3X4]',  # Methyl^b
    # r'[CX4;H0,H1,H2]',  # Alkane^b
]

# Convert all the functional smart string to rdkit molecule classes and pair with
# their original string representation
FUNC_SMARTS_MOL_TUP = list(
    zip(FUNC_SMARTS, map(Chem.MolFromSmarts, FUNC_SMARTS)))


def create_cas_functional(save_path, inchi_path=os.path.join('data', 'CAS_func.csv')):
    """
    Creates a new csv file contain information about whether a molecule contains
    the functional groups presented in the paper. Each molecule is identified
    by its CAS number.

    Parameters:
        filename:
            The file path to create the new csv file. By default it will store
            it in the current directory with a name of 'filename'.
    """

    with open(inchi_path, 'r', newline='') as inchi_file, open(save_path, 'w', newline='') as CAS_func:

        # Converts each line into dictionary with top values as keys
        inchi_reader = csv.DictReader(inchi_file, delimiter='\t')
        CAS_func_writer = csv.DictWriter(
            CAS_func, fieldnames=['cas_id'] + FUNC_SMARTS, delimiter=',')

        CAS_func_writer.writeheader()

        for line in islice(inchi_reader, 5):

            cas_id, inchi = line['cas_id'], line['inchi']

            # If a molecule can't be constructed from it's inchi just skip over it
            try:
                molecule_dict = detect_func_grps(inchi)
            except Exception:
                continue

            # Add the cas_id to the molecule dictionary
            molecule_dict['cas_id'] = cas_id

            CAS_func_writer.writerow(molecule_dict)

    return


def detect_func_grps(inchi):
    """
    Identifies which functional groups are present within a molecule
    (identified by its inchi).

    Returns:
        A dictionary whose keys are SMART string for the functional groups and
        whose values are the True/False to indicate if that functional group is
        present.
    """

    molecule = Chem.MolFromInchi(inchi)
    molecule_dict = {string: int(molecule.HasSubstructMatch(
        func_grp)) for string, func_grp in FUNC_SMARTS_MOL_TUP}

    return molecule_dict


def main():
    INCHI_PATH = os.path.join('data', 'inchi_LAB.txt')
    SAVE_PATH = os.path.join('data', 'CAS_TO_FUNC_LAB.csv')
    create_cas_functional(SAVE_PATH, inchi_path=INCHI_PATH)


if __name__ == '__main__':
    main()
