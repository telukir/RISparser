__author__ = 'maik'


# Copyright (C) 2013 Angel Yanguas-Gil
# This program is free software, licensed under GPLv2 or later.
# A copy of the GPLv2 license is provided in the root directory of
# the source code.

"""Parse WOK and Refman's RIS files"""

import re

woktag = "^[A-Z][A-Z0-9] |^ER$|^EF$"
ristag = "^[A-Z][A-Z0-9]  - "
riscounter = "^[0-9]+."

wokpat = re.compile(woktag)
rispat = re.compile(ristag)
riscounterpat = re.compile(riscounter)

ris_boundtags = ('TY', 'ER')
wok_boundtags = ('PT', 'ER')

wok_ignoretags = ['FN', 'VR', 'EF']
ris_ignoretags = []

ristags = {
    'TY': "Record kind",
    'A1': "Author",
    'A2': "Secondary Author",
    'A3': "Tertiary Author",
    'A4': "Subsidiary Author",
    'AB': "Abstract",
    'AD': "Author Address",
    'AN': "Accession Number",
    'AU': "Author",
    'C1': "Custom 1",
    'CA': "Caption",
    'CN': "Call Number",
    'CY': "Place Published",
    'DA': "Date",
    'DB': "Name of Database",
    'DO': "DOI",
    'DP': "Database Provider",
    'ET': "Edition",
    'J2': "Alternate Title",
    'KW': "Keywords",
    'L1': "File Attachments",
    'L4': "Figure",
    'LA': "Language",
    'LB': "Label",
    'IS': "Number",
    'M3': "Type of Work",
    'N1': "Notes",
    'NV': "Number of Volumes",
    'OP': "Original Publication",
    'PB': "Publisher",
    'PY': "Year",
    'RI': "Reviewed Item",
    'RN': "Research Notes",
    'RP': "Reprint Edition",
    'SE': "Version",
    'SN': "ISBN",
    'SP': "Pages",
    'ST': "Short Title",
    'T2': "Dictionary Title",
    'TA': "Translated Author",
    'TI': "Title",
    'TT': "Translated Title",
    'UR': "URL",
    'VL': "Volume",
    'Y2': "Access Date",
    'ER': "[End of Reference]"
}


def readris(filename, wok=True):
    """Parse a ris file and return a list of entries.

    Entries are codified as dictionaries whose keys are the
    different tags. For single line and singly ocurring tags,
    the content is codified as a string. In the case of multiline
    or multiple key ocurrences, the content is returned as a list
    of strings.

    Keyword arguments:
    filename -- input ris file
    wok -- flag, Web of Knowledge format is used if True, otherwise
           Refman's RIS specifications are used.

    """

    if wok:
        gettag = lambda line: line[0:2]
        getcontent = lambda line: line[2:]
        istag = lambda line: (wokpat.match(line) is not None)
        starttag, endtag = wok_boundtags
        ignoretags = wok_ignoretags
    else:
        gettag = lambda line: line[0:2]
        getcontent = lambda line: line[6:]
        istag = lambda line: (rispat.match(line) is not None)
        iscounter = lambda line: (riscounterpat.match(line) is not None)
        starttag, endtag = ris_boundtags
        ignoretags = ris_ignoretags

    filelines = open(filename, 'r').readlines()
    # Corrects for BOM in utf-8 encodings while keeping an 8-bit
    # string representation
    st = filelines[0]
    if (st[0], st[1], st[2]) == ('\xef', '\xbb', '\xbf'):
        filelines[0] = st[3:]

    inref = False
    tag = None
    current = {}
    ln = 0

    for line in filelines:
        ln += 1
        if istag(line):
            tag = gettag(line)
            if tag in ignoretags:
                continue
            elif tag == endtag:
                # Close the active entry and yield it
                yield current
                current = {}
                inref = False
            elif tag == starttag:
                # New entry
                if inref:
                    text = "Missing end of record tag in line %d:\n %s" % (
                        ln, line)
                    raise IOError(text)
                current[tag] = getcontent(line)
                inref = True
            else:
                if not inref:
                    text = "Invalid start tag in line %d:\n %s" % (ln, line)
                    raise IOError(text)
                current[tag] = getcontent(line)
        else:
            if not line.strip():
                continue
            if inref:
                # Active reference
                if tag is None:
                    text = "Expected tag in line %d:\n %s" % (ln, line)
                    raise IOError(text)
                else:
                    # Active tag
                    if hasattr(current[tag], '__iter__'):
                        current[tag].append(line.strip())
                    else:
                        current[tag] = [current[tag], line.strip()]
            else:
                if iscounter(line):
                    continue
                text = "Expected start tag in line %d:\n %s" % (ln, line)
                raise IOError(text)


def main():
    import sys
    refs = []
    if len(sys.argv) > 2:
        if sys.argv[2] == 'ris':
            wok = False
        else:
            wok = True
    else:
        wok = True
    refs = readris(sys.argv[1], wok)
    a1 = 0
    a2 = 0
    au = 0
    other = 0
    for r in refs:
        if 'A1' in r:
            a1 += 1
        elif 'A2' in r:
            a2 += 1
        elif 'AU' in r:
            au += 1
        else:
            other += 1
    print("a1: %s" % a1)
    print("a2: %s" % a2)
    print("au: %s" % au)
    print("other: %s" % other)
    # authors = [r['A1'] for r in refs]
    # for a in authors:
    #    print a


if __name__ == '__main__':
    main()
