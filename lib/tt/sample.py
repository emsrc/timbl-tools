"""
Sampling instances

"""

# TODO:
# - docstrings


import sys
import random


def get_class_counts(inf, sep=None, class_field=-1):
    if isinstance(inf, basestring):
        inf = open(inf)
        
    class_counts = {}
        
    for l in inf:
        l = l.strip()
        if not l: continue
        class_ = l.split(sep)[class_field]
        class_counts[class_] = class_counts.get(class_, 0) + 1
        
    return class_counts


def get_class_fractions(class_counts):
    total = float(sum(class_counts.values()))
    class_fracts = {}
    
    for class_, count in class_counts.items():
        class_fracts[class_] = count / total
        
    return class_fracts


def print_class_dist(class_counts, out=sys.stdout):
    line = 78 * "-" + "\n"
    classes = class_counts.keys()
    classes.sort()
    class_fracts = get_class_fractions(class_counts)
    form_str = "{0:16d}    {1:12.8f}    {2}\n"
    out.write(line)
    out.write("           COUNT"
              "        FRACTION"
              "    CLASS\n")
    out.write(line)
    
    for class_ in classes:
        out.write(
            form_str.format(
                class_counts[class_], 
                class_fracts[class_],
                class_))
        
    out.write(line)    
    total = sum(class_counts.values())
    out.write("{0:16d}\n".format(total))
        
        
def sample_down(inf, class_fracts={}, sep=None, class_field=-1, outf=sys.stdout):
    """
    fast but inaccurate down-sampling
    """
    # what is the distribution of the error?
    if isinstance(inf, basestring):
        inf = open(inf)
        
    if isinstance(outf, basestring):
        outf = open(outf, "w")
        
    for l in inf:
        l = l.strip()
        if not l: continue
        class_ = l.split(sep)[class_field]
        
        if random.random() < class_fracts.get(class_, 1.0):
            outf.write(l + "\n")
