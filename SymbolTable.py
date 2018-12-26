class SymbolTable:
    def __init__(self):
        """
        Creates a new empty symbol table
        """
        self.subroutine_table = {}
        self.class_table = {}
        self.index_table = {'STATIC': 0,
                            'FIELD': 0,
                            'ARG': 0,
                            'VAR': 0}

    def start_subroutine(self):
        """
        Starts a new subroutine scope (i.e. erases all names in the previous subroutine's scope.)
        :return:
        """
        self.subroutine_table = {}
        self.index_table['VAR'] = 0
        self.index_table['ARG'] = 0

    def define(self, name, o_type, kind):
        """
        Defines a new identifier of a given name,
        type and kind and assigns it a running index.
        STATIC and FIELD identifiers have a class scope,
        while ARG and VAR identifiers have a subroutine scope.
        :param name: String
        :param o_type: String
        :param kind: STATIC, FIELD, ARG, VAR
        :return:
        """

        index = self.var_count(kind)

        if (kind == 'FIELD') | (kind == 'STATIC'):
            self.class_table[name] = {'type': o_type,
                                      'kind': kind,
                                      'index': index}
        elif (kind == 'ARG') | (kind == 'VAR'):
            self.subroutine_table[name] = {'type': o_type,
                                           'kind': kind,
                                           'index': index}
        else:
            raise Exception('invalid kind')

        self.index_table[kind] += 1

    def var_count(self, kind):
        """
        Returns the number of variables of the given kind
        already defined in the current scope.
        :param kind: STATIC, FIELD, ARG or VAR
        :return: int
        """

        return self.index_table[kind]

    def is_in_table(self, name):
        if name in self.subroutine_table:
            return True
        elif name in self.class_table:
            return True
        else:
            return False

    def kind_of(self, name):
        """
        Returns the 'kind' of the named identifier in the current scope
        :param name: String
        :return: String
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name]['kind']
        elif name in self.class_table:
            return self.class_table[name]['kind']
        else:
            raise Exception('identifier not found')

    def type_of(self, name):
        """
        Returns the 'type' of the named identifier in the current scope
        :param name: String
        :return: String
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name]['type']
        elif name in self.class_table:
            return self.class_table[name]['type']
        else:
            raise Exception('identifier not found')

    def index_of(self, name):
        """
        Returns the 'index' assigned to named identifier
        :param name: String
        :return: int
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name]['index']
        elif name in self.class_table:
            return self.class_table[name]['index']
        else:
            raise Exception('identifier not found')
