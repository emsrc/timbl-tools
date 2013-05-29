"""
graphing feature weights
"""

import sys

# TODO:
# - clean
# - tests
# - docstrings


        
def sort_table(field_names, table, field, reverse=True):
    """
    sort table on field
    """
    field_no = field_names.index(field)
    table.sort(lambda x,y: cmp(x[field_no], y[field_no]),
               reverse=reverse) 
    
    
def print_table(field_names, table, outf=sys.stdout):
    max_len = max([len(r[-1]) for r in table])
    
    if max_len:
        max_len = max(5, max_len)
        header = "Name".ljust(max_len)
    else:
        header = ""
        
    header += "".join([fn.rjust(16) for fn in field_names])
    outf.write(header  + "\n")
    line = len(header) * "-" + "\n"
    outf.write(line)
    
    for i, record in enumerate(table):
        if max_len:
            outf.write(record[-1].ljust(max_len))
            
        outf.write("{0:16d}{1:16d}".format(*record[:2]))
        
        for f in record[2:-1]:
            outf.write("{0:16f}".format(f))
            
        outf.write("\n")
        
    outf.write(line)
    
    
def graph_table(field_names, table, outf=sys.stdout, max_bar_size=60):
    if isinstance(outf, basestring):
        outf = open(outf, "w")
        
    max_len = max([len(r[-1]) for r in table])
    
    if max_len:
        max_len = max(5, max_len)
        header = "Name".ljust(max_len)
    else:
        header = " Feats"
        
    field_no = 2
    
    for metric in field_names[2:]:
        outf.write(header + metric.rjust(16) + "\n")
        line = (len(header) + 16 + 2 + max_bar_size) * "-" + "\n"
        outf.write(line)
        
        sort_table(field_names, table, metric)
        
        max_val = table[0][field_no]
        unit = max_val / float(max_bar_size)
        
        for i, record in enumerate(table):
            feat_name = record[-1]
            
            if feat_name:
                outf.write(feat_name.ljust(max_len))
            else:
                outf.write("{0:6d}".format(record[0]))
            
            outf.write("{0:16f}".format(record[field_no]))
                
            val = record[field_no]
            size = int(val / unit)
            outf.write(2 * " " + size * "=" + "\n")
        
        field_no += 1
        outf.write(line + "\n")
        
        
        
def parse_feat_weights(inf, feat_names=[]):
    """
    Parse feature weights from table in Timbl trace
    
    @param inf: Timbl ouput
    
    @keyword feat_names: list of feature names
    
    @return: list of field names and list of records
    """
    table = []
    
    if isinstance(inf, basestring):
        inf = open(inf)
        
    in_table = False
    
    for l in inf:
        record = l.split()
        
        if record[:2] == ['Feats', 'Vals']:
            field_names = record
            in_table = True
        elif not record:
            in_table = False
        elif in_table:
            # line may contain extra fields, e.g. "NUMERIC", which we ignore
            record = record[:len(field_names)]
            
            # convert to ints/floats
            feat_no = record[0] = int(record[0])

            try:
                record[1] = int(record[1])
            except ValueError:
                # assume ignored feature
                continue
            

            for i in range(2, len(record)): 
                record[i] = float(record[i])

            # append feature name (possibly empty) at end of record
            try:
                record.append(feat_names[feat_no - 1])
            except IndexError:
                record.append("")
            
            table.append(record)
            
    return field_names, table
    
    
        
def parse_feature_names(inf):
    if isinstance(inf, basestring):
        inf = open(inf)
        
    return [ l.strip() 
             for l in inf if l.strip() ]

    