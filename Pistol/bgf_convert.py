#!/usr/bin/python
"""\
bgf_convert Converts Biograph files to XYZ or CTAB files

Usage: bgf_convert.py [options] <filename>

Options are:
-h      Print this help message
-x      Output in xyz format (default)
-c      Output in ctab format
-j      Output in Jaguar input format

Copyright (c) 2003 Richard P. Muller (rmuller@sandia.gov). All rights
reserved. See the LICENSE file for licensing details.
"""

import sys,getopt,string,math,re

sym2no = { # Converts a symbol to an atomic number
    'X' : 0, 'H'  : 1, 'He' : 2, 'Li' : 3, 'Be' : 4,
    'B'  : 5, 'C'  : 6, 'N'  : 7, 'O'  : 8, 'F'  : 9,
    'Ne' : 10, 'Na' : 11, 'Mg' : 12, 'Al' : 13, 'Si' : 14,
    'P'  : 15, 'S'  : 16, 'Cl' : 17, 'Ar' : 18, 'Fe' : 26,
    'Ga' : 31, 'Ru' : 44, 'U' : 92,
    'x' : 0, 'h'  : 1, 'he' : 2, 'li' : 3, 'be' : 4,
    'b'  : 5, 'c'  : 6, 'n'  : 7, 'o'  : 8, 'f'  : 9,
    'ne' : 10, 'na' : 11, 'mg' : 12, 'al' : 13, 'si' : 14,
    'p'  : 15, 's'  : 16, 'cl' : 17, 'ar' : 18, 'fe' : 26, 
    'ga' : 31,  'ru' : 44, 'u' : 92} 

output_extension = {
    'jag':'in',
    'bgf':'bgf',
    'ctab':'ctab',
    'xyz':'xyz'
    }

bond_distance = [
    1.0, 1.20, 1.40,
    1.82, 1.3725, 0.795, 1.70, 1.55, 1.52, 1.47, 1.54,
    2.27, 2.3, 2.3, 2.30, 2.30, 2.30, 2.30, 1.88]

def cleansym(s):
    return re.split('[^a-zA-Z]',s)[0]

def distance(at1,at2):
    sym1,x1,y1,z1 = at1
    sym2,x2,y2,z2 = at2
    return math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2)+math.pow(z1-z2,2))

def cutoff_distance(at1,at2):
    sym1,x1,y1,z1 = at1
    sym2,x2,y2,z2 = at2
    an1 = sym2no[sym1]
    an2 = sym2no[sym2]
    return 0.6*(bond_distance[an1]+bond_distance[an2])

def get_bonds(mol):
    bonds = []
    nat = len(mol)
    for i in range(nat):
        for j in range(i):
            rij = distance(mol[i],mol[j])
            rij0 = cutoff_distance(mol[i],mol[j])
            if rij < rij0:
                # CTAB atom numbering starts from 1, not zero
                bonds.append((j+1,i+1))

    return bonds


def help_and_exit():
    print __doc__
    sys.exit()
    return

def error_and_exit(error_message):
    print error_message
    sys.exit()
    return

def make_output_filename(input_filename,output_format):
    return string.replace(input_filename,'bgf',output_extension[output_format])

def output_ctab(mol,ctab_filename):
    bonds = get_bonds(mol)
    nat = len(mol)
    nbonds = len(bonds)
    file = open(ctab_filename,'w')
    file.write('%3d%3d\n' % (nat,nbonds))
    for (sym,x,y,z) in mol:
        file.write('%10.4f%10.4f%10.4f %3s\n' % (x,y,z,sym))
    for (iat,jat) in bonds:
        file.write('%3d%3d1\n' % (iat,jat))
    file.close()
    return
    
def output_xyz(mol,xyz_filename):
    nat = len(mol)
    file = open(xyz_filename,'w')
    file.write('%i \nFile generated by bgf_convert\n' % nat)
    for (sym,x,y,z) in mol:
        file.write('%s %10.4f %10.4f %10.4f\n' % (sym,x,y,z))
    file.close()
    return

def output_jag(mol,jag_filename):
    nat = len(mol)
    file = open(jag_filename,'w')
    file.write('File generated by bgf_convert\n')
    file.write('&gen\nidft=22111\nip11=2\n&\n')
    file.write('&zmat\n')
    for (sym,x,y,z) in mol:
        file.write('%s %10.4f %10.4f %10.4f\n' % (sym,x,y,z))
    file.write('&\n')
    file.close()
    return

def input_bgf(filename):
    hetatm = re.compile('HETATM')
    file = open(filename,'r')
    lines = file.readlines()
    file.close()
    mol = []
    for line in lines:
        if hetatm.search(line):
            words = string.split(line)
            x,y,z = float(words[6]),float(words[7]),float(words[8])
            sym = cleansym(words[2])
            mol.append((sym,x,y,z))
    return mol

def printmol(mol):
    for atom in mol:
        print "%s %10.4f %10.4f %10.4f" % atom
    return

def main():
    if len(sys.argv) < 2: help_and_exit()
    opts,args = getopt.getopt(sys.argv[1:],'hxcj')
    output_format = 'xyz'

    for (key,value) in opts:
        if key == '-h': help_and_exit()
        if key == '-c': output_format = 'ctab'
        if key == '-x': output_format = 'xyz'
        if key == '-j': output_format = 'jag'

    for filename in args:
        mol = input_bgf(filename)
        out_name = make_output_filename(filename,output_format)
        if output_format == 'ctab':
            output_ctab(mol,out_name)
        elif output_format == 'xyz':
            output_xyz(mol,out_name)
        elif output_format == 'jag':
            output_jag(mol,out_name)
        else:
            error_and_exit('Unknown format: %s' % output_format)
    return

    
if __name__ == '__main__':
    main()
