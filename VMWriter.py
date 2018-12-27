class VMWriter:
    def __init__(self,output_file):
        """
        creates a new file and prepares it for writing
        VM commands
        :param output_file: String
        """
        self.f = open(output_file, 'w')

    def write_push(self, segment, index):
        """
        Writes a VM 'push' command
        :param segment: CONST,ARG,LOCAL,STATIC,THIS,THAT,POINTER,TEMP
        :param index: int
        :return:
        """
        self.f.write("push {} {}\n".format(segment, index))

    def write_pop(self, segment, index):
        """
        Writes a VM 'pop' command
        :param segment: CONST,ARG,LOCAL,STATIC,THIS,THAT,POINTER,TEMP
        :param index: int
        :return:
        """
        self.f.write("pop {} {}\n".format(segment, index))

    def write_arithmetic(self, command):
        """
        writes a VM arithmetic command
        :param command: ADD,SUB,NEG,EQ,GT,LT,AND,OR,NOT
        :return:
        """
        self.f.write(command.lower())

    def write_label(self, label):
        """
        writes a VM label command
        :param label: String
        :return:
        """
        raise Exception()

    def write_goto(self, label):
        """
        Writes a VM label command
        :param label: String
        :return:
        """
        raise Exception()

    def write_if(self, label):
        """
        Writes a VM if-goto command
        :param label: String
        :return:
        """
        raise Exception()

    def write_call(self, name, n_args):
        """
        Writes a VM 'call' command
        :param name: String
        :param n_args: int
        :return:
        """
        self.f.write("call {} {}".format(name, n_args))

    def write_function(self, name, n_locals):
        """
        Writes a VM 'function' command
        :param name: String
        :param n_locals: int
        :return:
        """
        self.f.write("function {} {}".format(name, n_locals))

    def write_return(self):
        """
        writes a VM return command
        :return:
        """
        self.f.write('return\n')

    def close(self):
        """
        closes the output file
        :return:
        """
        self.f.close()
