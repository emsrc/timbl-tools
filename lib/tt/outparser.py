"""
Parsing Timbl ouput 

The general idea here is to have lazy parsing in two ways. First, functions
are generally iterators which yield a first result without analyzing the full
string. Second, functions parse the input string into its constituents, but
without descending into parsing these constituents - that's up to the caller.
"""

            
def parse_timbl_output(timbl_output):
    """
    Parse Timbl ouput
    
    @param timbl_output: any container which support iteration over the output
    lines, usually a file
    
    @return: a generator object which yield tuples of an instance string and a
    list of nearest neighbours
    
    This is a generator function which yields (instance, neighbours) pairs
    until timbl_ouput is exhausted. It can be called with "next()" , used in a
    "for" loop, etc
    
    The list of neighbours remains empty when parsing normal Timbl output.
    """
    inst_str = timbl_output.next()
    k_nn_list = []
    
    for line in timbl_output:
        if line.startswith("#"):
            k_nn_list.append(line)
        else:
            yield inst_str, k_nn_list
            inst_str = line
            k_nn_list = []
    
    # output final instance 
    yield inst_str, k_nn_list
    
    
            
def parse_inst(inst_str, feat_sep=None,
               with_distrib=False, with_distance=False):
    """
    Parse Timbl instance
    
    @param inst_str: instance string
    
    @keyword feat_sep: feature separator (defaults to whitespace)
    
    @keyword with_dstrib: instance string includes class distribution as
    produced with Timbl's +vdb (or +vk) option
    
    @keyword with_dist: instance string includes distance as
    produced with Timbl's +vdi option
    
    @return: a five tuple (feature string, true class, predicted class,
    distribution string, distance), where the latter two may be None. If
    present, distance is a float
    """
    # Automatically detecting the presence of a distribution and/or a distance
    # turns out to be hard, because the feature delimiter may vary
    # (whitespace, comma) and Timbl's output format is somehwat inconsistent.
    # Hence the caller must explicitly specify the instance format.
    inst_str = inst_str.rstrip()

    if with_distance:
        inst_str, distance = inst_str.rsplit(None, 1)
        distance = float(distance)
    else:
        distance = None
        
    if with_distrib:
        inst_str, distrib_str = inst_str.rsplit("{", 1)
        distrib_str = distrib_str.strip(" }")
        inst_str = inst_str.rstrip()
    else:
        distrib_str = ""

    feats_str, true_class, pred_class = inst_str.rsplit(feat_sep, 2)
    
    # for consistency always return everything
    return feats_str, true_class, pred_class, distrib_str, distance



def parse_feats(feats_str, feat_sep=None):
    """
    Parse features of an instance
    
    @param feats_str: feature string
    
    @keyword feat_sep: separator (defaults to whitespace)
    
    @return: an iterator that returns the individual features, or
    StopIteration when exhausted
    """
    return iter(feats_str.split(feat_sep))



def parse_distrib(distrib_str):
    """
    Parse a class distribution string
    
    @param distrib_str: a class distribution string as produced by Timbl +vdb
    option, but without the surrounding accolades
    
    @return: an iterator that returns subsequent (class, count) tuples, where
    class is a string and count is a float, or StopIteration when exhausted
    """
    return ( _convert_pair(pair.split())
             for pair in distrib_str.split(",") )


def _convert_pair(pair):
    return pair[0], float(pair[1])


#-------------------------------------------------------------------------------
# Parsing nearest neighbours under particular configurations of verbose output
#-------------------------------------------------------------------------------
 
def parse_neighbour_vk_vdi(nn_str):
    """
    Parse nearest neighbour as produced with Timbl's +vk +vdi option
    
    @param nn_str: nearest neighbour string
    
    @return: tuple of class distribution as a string and distance as a float
    
    Example:
    # k=4\t{ T 1.00000, J 79.0000 }\t0.22791476779488\n
    """
    distrib_str, distance = nn_str.split("\t")[1:]
    return distrib_str.strip("{} "), float(distance)


def parse_distance_vn_vdb(nn_str):
    """
    Parse nearest neighbour as produced with Timbl's +vn +vdb option
    
    @param nn_str: nearest neighbour string
    
    @return: distance as a float
    
    Input example:
    # k=2, 14 Neighbor(s) at distance:\t0.042844587034556\n
    """
    return float(nn_str.split("\t")[-1])


def parse_neighbour_vn_vdb(nn_str, feat_sep=None):
    """
    Parse nearest neighbour as produced with Timbl's +vn +vdb option
    
    @param nn_str: nearest neighbour string
    
    @keyword feat_sep: feature separator
    
    @return: tuple of instance features as a string and the class as a string
    
    Input example:
    #\t= = = = = = = = + p e = { T 1.00000 }\n
    """
    feats, class_ = nn_str.rsplit("{", 1)
    return feats[2:-1], class_.split()[0]
    
