#!/usr/bin/env python
#
# Copyright (c) 2011 Alfredo Deza <alfredodeza [at] gmail [dot] com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import optparse
import sys
from jargon        import tokenizer
from jargon.pyspec import _MethodWrap

BLUE   = '\033[94m'
GREEN  = '\033[92m'
YELLOW = '\033[93m'
RED    = '\033[91m'
ENDS   = '\033[0m'


def globals_from_execed_file(filename):
    globals_ = {}
    execfile(filename, globals_)
    return globals_


class FileCollector(list):

    def __init__(self, path, match):
        self.match = match
        self.path = path
        self._collect()

    def _collect(self):
        for root, dirs, files in os.walk(self.path):
            for item in files:
                if self.match and self.match in item: continue
                # NOTE what about pyc pyo files? get this fixed
                if item.lower().endswith("py"):
                    absolute_path = os.path.join(root, item)
                    if "test" in item.lower():
                        self.append(absolute_path)
    

def name_convertion(name):
    name = name.replace('_', ' ')
    name = name.capitalize() + '.'
    return name
    

def main():
    """Parse the options"""
    parse = optparse.OptionParser()
    parse.add_option("--verbose","-v", action="store_true",
            help="Prints all the matching files with line numbers")
    parse.add_option("--path", help="Specify a path to report on")
    options, arguments = parse.parse_args()

    verbose = False
    match   = False
    path    = os.getcwd()

    if options.verbose:
        verbose = True 

    if options.path:
        path = os.path.abspath(options.path)

    locate = FileCollector(path, match)
    total_methods = 0
    total_method_fails = 0
    for f in locate:
        global_modules = map(globals_from_execed_file, [f])
        test_modules = [  i for i in global_modules[0].values() if callable(i) and 'test' in i.__name__ ]
        for case in test_modules:
            suite_methods = 0
            suite = case()
            print "\n%s" % name_convertion(suite.__class__.__name__)
            methods = [i for i in dir(suite) if not i.startswith('_')]
            for test in methods:
                try:
                    t = getattr(suite, test)
                    t()
                    print "%s  - %s%s"% (GREEN, name_convertion(test), ENDS)
                    total_methods += 1
                except BaseException, e:
                    failure              = sys.exc_info()
                    tb                   = failure[2]
                    exc_name             = e.__class__.__name__
                    total_method_fails   += 1
                    print "%s  - %s%s" % (RED, name_convertion(test), ENDS)
    if not total_methods:
        print "No collected tests to run."

    elif total_method_fails:
        print "\n%s%s out of %s failed%s" % (RED,total_method_fails, total_methods, ENDS)
    else:
        print "\n%sall %s test(s) passed%s" % (GREEN, total_methods, ENDS)


if __name__ == "__main__":
    main()


