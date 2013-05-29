"""
wraper class for file-based classification with Timbl
"""

import logging
import os
import tempfile
import subprocess


# TODO:
# - docstrings
# - logging
# - use Timbl server


class TimblFile(object):
    """
    file-based classification with Timbl
    """
    
    def __init__(self, timbl_exec="Timbl", default_opts=""):
        # when running under Wing IDI, the shell search path is not available,
        # so the path to the Timbl exec must be specified
        self.timbl_exec = timbl_exec
        self.default_opts = default_opts
        
    # training
        
    def train(self, train_inst_fn, inst_base_fn, options="", log=False):
        """
        train on single file and save instance base
        """
        command = "%s %s %s -f %s -I %s" % (
            self.timbl_exec, 
            self.default_opts,
            options,
            train_inst_fn,
            inst_base_fn)
        
        if log:
            command += " >%s.log 2>&1" % train_inst_fn

        proc = subprocess.call(command, shell=True, cwd=os.getcwd())
        
        return inst_base_fn
    
    
    def train_multi(self, train_inst_fns, inst_base_fn, options="", log=False):
        """
        train on multiple files and save instance base
        """ 
        all_inst_fn = self._cat_inst_files(train_inst_fns)
        self.train(all_inst_fn, inst_base_fn, options=options, log=log)
        os.remove(all_inst_fn)
        return inst_base_fn

    # testing
        
    def test(self, test_inst_fn, inst_base_fn, out_fn=None, options="",
             log=False):
        """
        test on single file with given instance base
        """
        command = "%s %s %s -t %s -i %s -o %s" % (
            self.timbl_exec, 
            self.default_opts,
            options,
            test_inst_fn,
            inst_base_fn)
        
        if out_fn:
            command += " -o %s" % out_fn
            
        if log:
            command += " >%s.log 2>&1" % test_inst_fn 

        proc = subprocess.call(command, shell=True, cwd=os.getcwd())
        
        return out_fn
    
    
    def test_multi(self, test_inst_fns, inst_base_fn, out_fns=None,
                   options="", log=False):
        """
        test on multiple file with given instance base
        """
        # use named temp files to prevent filename collisions during parallel execution  
        all_in_f = tempfile.NamedTemporaryFile(prefix="all_in_",
                                               suffix=".inst", mode="w", delete=False)
        all_sizes = []
        
        # concatenate all test intance files into one big input file,
        # keeping track of their sizes
        for fn in test_inst_fns:
            inst = open(fn).readlines()
            all_sizes.append(len(inst))
            all_in_f.writelines(inst)
            
        all_in_f.close()
        
        all_out_f = tempfile.NamedTemporaryFile(prefix="all_out_",
                                                suffix=".inst", mode="w", delete=False)
        all_out_f.close()
        
        self.test(all_in_f.name, inst_base_fn, all_out_f.name, options, log=log)

        all_out_f = open(all_out_f.name)
        
        if out_fns is None:
            out_fns = [ os.path.splitext(fn)[0] + ".out"
                        for fn in test_inst_fns ]
        else:
            assert len(out_fns) == len(test_inst_fns)

        # split the output instance files into output parts with sizes
        # according to the corresponding input parts
        for out_fn, size in zip(out_fns, all_sizes):
            out = open(out_fn, "w")
            
            for i in range(size):
                out.write(all_out.readline())

        os.remove(all_in_f.name)
        os.remove(all_out_f.name)
        
        return out_fns
    
        
    # training and testing combined
    
    def train_test(self, train_inst_fn, test_inst_fn, out_fn=None,
                   log_fn=None, options="", log=False, out_dir=None):
        """
        train on single file and test on single file
        """
        if not out_fn:
            out_fn = os.path.splitext(test_inst_fn)[0] + ".out" 
            if out_dir:
                out_fn = os.path.basename(out_fn)
                out_fn = os.path.join(out_dir, out_fn)
               
        command = "%s %s %s -f %s -t %s -o %s" % (
            self.timbl_exec, 
            self.default_opts,
            options,
            train_inst_fn,
            test_inst_fn,
            out_fn)
        
        if log:
            if not log_fn:
                log_fn = os.path.splitext(out_fn)[0] + ".log" 
                if out_dir:
                    log_fn = os.path.basename(log_fn)
                    log_fn = os.path.join(out_dir, log_fn)
                
            command += " >%s 2>&1" % log_fn
            
            
        logging.info(command)
        proc = subprocess.call(command, shell=True, cwd=os.getcwd())
        
        return out_fn, log_fn
    
    
    def train_test_multi(self, train_inst_fns, test_inst_fns, out_fns=None,
                         log_fn=None, options="", log=False, out_dir=None):
        """
        train on multiple training files and test on multiple test files
        """
        all_train_fname = self._cat_inst_files(train_inst_fns)
        
        # use named temp files to prevent filename collisions during parallel execution  
        all_test_f = tempfile.NamedTemporaryFile(prefix="all_test",
                                                 suffix=".inst", 
                                                 mode="w", 
                                                 delete=False)
        all_sizes = []
        
        # concatenate all test intance files into one big input file,
        # keeping track of their sizes
        for fn in test_inst_fns:
            inst = open(fn).readlines()
            all_sizes.append(len(inst))
            all_test_f.writelines(inst)
            
        all_test_f.close()
        
        all_out_f = tempfile.NamedTemporaryFile(prefix="all_out",
                                                suffix=".inst", 
                                                mode="w", 
                                                delete=False)
        all_out_f.close()
        
        # out_dir is only for log file, and does not affect the location of
        # all_out_f.name
        
        self.train_test(all_train_fname, 
                        all_test_f.name,
                        all_out_f.name,
                        log_fn=log_fn,
                        options=options,
                        log=log,
                        out_dir=out_dir)
        
        all_out_f = open(all_out_f.name)
        
        if out_fns:
            assert len(out_fns) == len(test_inst_fns)
        else:
            # create output filenames
            out_fns = []
            for fn in test_inst_fns:
                out_fn = os.path.splitext(fn)[0] + ".out" 
                if out_dir:
                    out_fn = os.path.basename(out_fn)
                    out_fn = os.path.join(out_dir, out_fn)
                out_fns.append(out_fn)
                        
        # split the output instance files into output parts with sizes
        # according to the corresponding input parts
        for out_fname, size in zip(out_fns, all_sizes):
            out_f = open(out_fname, "w")
            
            for i in range(size):
                out_f.write(all_out_f.readline())

        os.remove(all_train_fname)
        os.remove(all_test_f.name)
        os.remove(all_out_f.name)

        # there is only a single log file
        return out_fns, log_fn
    
    # cross validation
    
    def cross_validate(self, inst_fns, test_inst_fns=None, out_fns=None,
                       log_fns=None, options="", n=None, log=False, out_dir=None):
        # Default is to use the same instance files for training and testing
        # during cross-validation. However, the instance files used for
        # testing may be explicitly specified. This allows for down-sampling
        # of the training instances without affecting the test instances.
        if not test_inst_fns:
            test_inst_fns = inst_fns
            
        if not out_fns:
            out_fns = len(inst_fns) * [None]
            
        if not log_fns:
            log_fns = len(inst_fns) * [None]
            
        if not n:
            n = len(inst_fns)
        else:
            assert n <= len(inst_fns)
            
        for i in range(n):
            train_inst_fn = self._cat_inst_files(
                inst_fns[:i] + inst_fns[i+1:])
            
            out_fns[i], log_fns[i] = self.train_test(
                train_inst_fn,
                test_inst_fns[i],
                out_fn=out_fns[i],
                options=options,
                log=log,
                out_dir=out_dir)

            os.remove(train_inst_fn)
            
        return out_fns, log_fns
    
    # support
    
    def _cat_inst_files(self, inst_fns):
        # Use named temp files to prevent filename collisions during parallel execution.
        # Caller is reponsible for deleting the file!
        all_inst_fn = tempfile.NamedTemporaryFile(suffix=".inst", mode="w",
                                                  delete=False).name
        # won't work on windows
        for fn in inst_fns:
            # might be faster using xargs
            subprocess.call("cat %s >> %s" % (fn, all_inst_fn), 
                            shell=True, cwd=os.getcwd())
            
        return all_inst_fn
    
        
    
        