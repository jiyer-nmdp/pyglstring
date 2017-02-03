#!/usr/bin/env python3
"""
check_glstring.py

Does a sanity check of a GL String

checks...
- if locus found in more than one locus block
  e.g., this is good
  HLA-A*01:01/HLA-A*01:02+HLA-A*24:02|HLA-A*01:03/HLA-A*01:04+HLA-A*24:03
  e.g., this is bad
  HLA-A*01:01/HLA-A*01:02+HLA-A*24:02^HLA-A*01:03/HLA-A*01:04+HLA-A*24:03

- if a allele list contains more than one locus
  e.g., this is good
  HLA-B*44:01/HLA-C*44:02
  e.g., this is bad
  HLA-B*44:01/HLA-C*44:02

todo:
    check_genotypelist
    check_genotype
    check_phased
"""

import argparse
import re


def gl_to_allele(gl):
    for locus_block in gl.split('^'):
        for genotype in locus_block.split('|'):
            for locus in genotype.split('+'):
                for allele_list in locus.split('~'):
                    for allele in allele_list.split('/'):
                        print(allele)


def gl_to_allele2(gl):
    for locus_block in gl.split('^'):
        for genotype in locus_block.split('|'):
            for locus in genotype.split('+'):
                for allele_list in locus.split('~'):
                    for allele in allele_list.split('/'):
                        yield allele


def gl_to_allele3(gl):
    for allele in re.split('[\^\|\+\~\/]', gl):
        yield allele


def gl_to_muug(gl):
    # create an empty list
    muug_list = []
    (mom, dad) = gl.split('+')
    momi = mom.split('~')
    dadi = dad.split('~')

    for ma, pa in zip(momi, dadi):
        parents = [ma, pa]
        parents.sort()  # sort in place
        ug = '+'.join(parents)
        muug_list.append(ug)
    muug_list.sort()  # sort in place
    return ('^'.join(muug_list))


def getalleles(gl):
    """given a glstring, return a set containing all the alleles"""
    alleles = set()
    for allele in re.split('[\^\|\+\~\/]', gl):
        alleles.add(allele)
    return alleles


def getloci(alleles):
    """given a list or set of alleles, return a set containing all the loci"""
    loci = set()
    for allele in alleles:
        loci.add(allele.split('*')[0])
    return loci


def checkdups(mysetlist):
    """takes a list of sets, and returns a set of items that are found in
    more than one set"""
    alldups = set()
    for i, myset in enumerate(mysetlist):
        dups = set()
        othersets = set().union(*mysetlist[i+1:])
        dups = myset & othersets
        alldups.update(dups)
    return alldups


def check_locus_blocks(gl):
    """check to see if any loci are found in more than one locus block"""
    locusblocks = gl.split('^')
    if len(locusblocks) > 1:
        loci = []
        for locusblock in locusblocks:
            print(locusblock)
            loci.append(getloci(getalleles(locusblock)))
        dups = checkdups(loci)
        if len(dups) == 0:
            print("No loci found in more than one locus block\n")
        else:
            print("Loci found in more than 1 locus block:", dups, "\n")
    else:
        print("only one locus block, nothing to check\n")


def get_allele_lists(gl):
    """takes a GL String and returns a list of allele lists it contains"""
    allele_lists = []
    for allele_list in re.split('[\^\|\+\~]', gl):
        if "/" in allele_list:
            allele_lists.append(allele_list)
    return allele_lists


def check_allele_lists(gl):
    """takes a GL String, and checks to see if there are more than one loci
    each of the allele lists, and if any of the allele lists have a duplicate
    allele"""

    allele_lists = get_allele_lists(gl)
    if len(allele_lists) > 0:
        for allele_list in allele_lists:
            loci = getloci(getalleles(allele_list))
            if len(loci) > 1:
                print(allele_list, ' contains more than on locus')
            else:
                print(allele_list, ' OK')
    else:
        print('no allele lists found in GL String')


def do_check(gl):
    """check the glstrings!"""
    print("gl = ", gl)
    print("Checking locus blocks...")
    check_locus_blocks(gl)
    print("Checking allele lists...")
    check_allele_lists(gl)
    print("--------\n")
    # check_genotype_list(gl)
    # check_genotypes(gl)
    # check_phased(gl)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--glstring",
                        # required=True,
                        help="GL String to be checked",
                        type=str)
    args = parser.parse_args()

    if args.glstring:
        do_check(args.glstring)
    else:
        testgl = [
            "HLA-A*01:01/HLA-A*01:02",
            "HLA-A*01:01/HLA-B*01:02",
            "HLA-A*01:01/HLA-A*01:02+HLA-A*24:02",
            ("HLA-A*01:01/HLA-A*01:02+HLA-A*24:02|"
             "HLA-A*01:03/HLA-A*01:04+HLA-A*24:03"),
            "HLA-A*01:01~HLA-B*44:02+HLA-A*02:01~HLA-B*08:01",
            "HLA-A*01:01+HLA-A*24:02^HLA-B*08:01+HLA-B*44:02",
            ("HLA-A*01:01+HLA-A*24:02^HLA-B*08:01+HLA-B*44:02^"
             "HLA-A*01:01+HLA-A*24:02^HLA-B*08:01+HLA-B*44:02"),
        ]
        for gl in testgl:
            do_check(gl)


if __name__ == '__main__':
    main()