import JackTokenizer as Tk
import CompilationEngine as CmpE
from sys import argv
import os
"""
The analyzer program operates on a given source, where source is either a file name of the form
Xxx.jack or a directory name containing one or more such files.
For each source Xxx.jack, the analyzer goes through the following logic:
1. Create a JackTokenizer from the Xxx.jack input file.
2. Create an output file called Xxx.xml and prepare it for writing;
3. Use the CompilationEngine to compile the input JackTokenizer into the output file.
"""


def analyzer(file_path):
    input_file_path = file_path
    output_file_path = file_path[:-5] + ".xml"
    output_vm_path = file_path[:-5] + ".vm"

    tk = Tk.JackTokenizer(input_file_path)
    with open(output_file_path, 'w') as f:
        compiler = CmpE.CompilationEngine(tk, f, output_vm_path)
        compiler.compile_class()
    return


assert len(argv) == 2, 'path argument expected'
if argv[1][-5:] != '.jack':
    dirs = os.listdir(argv[1])
    for file in dirs:
        if file[-5:] == '.jack':
            analyzer(argv[1] + '/' + file)
else:
    analyzer(argv[1])
