import SymbolTable
import VMWriter

OP = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']
UNARY_OP = ['-', '~']
KEYWORD_CONSTANT = ['true', 'false', 'null', 'this']
TYPES = ['int', 'char', 'boolean', 'void']


class CompilationEngine:
    def __init__(self, input_file, output_file, output_vm_path):
        """
        Creates a new compilation engine with the given input and output.
        The next routine called must be compileClass().
        :param input_file: JackTokenizer
        :param output_file: File
        """
        self.tk = input_file
        self.f = output_file
        self.symbol_table = SymbolTable.SymbolTable()
        self.writer = VMWriter.VMWriter(output_vm_path)

        self.current_class = ""
        self.current_subroutine = ""
        self.current_ret_type = ""

    def compile_class(self):
        """
        Compiles a complete class.
        format: 'class' className '{' classVarDec* subroutineDec* '}'
        :return:
        """

        self.f.write("<class>\n")
        self.tk.advance()

        assert self.tk.token_val() == 'class'
        self.write_elementary_expression_and_advance()
        assert self.is_class_name()
        self.current_class = self.tk.token_val()
        self.write_identifier_and_advance('class', 'definition')
        assert self.tk.token_val() == '{'
        self.write_elementary_expression_and_advance()
        self.compile_class_var_dec()
        while self.tk.token_val() != '}':
            self.compile_subroutine()
        assert self.tk.token_val() == '}'
        self.write_elementary_expression_and_advance(False)
        self.f.write("</class>\n")
        return

    def write_elementary_expression_and_advance(self, is_advance=True):
        assert self.tk.token_type() != 'identifier'
        self.f.write("<{0}> {1} </{0}>\n".format(self.tk.token_type(),
                                                 self.tk.token_val()))
        if is_advance:
            self.tk.advance()

    def write_identifier_and_advance(self, category, usage, index=False):
        if index is False:
            self.f.write("<{0} category='{2}' usage='{3}'> {1} </{0}>\n".format(self.tk.token_type(),
                                                                                self.tk.token_val(),
                                                                                category,
                                                                                usage)
                         )
        else:
            self.f.write("<{0} category='{2}' usage='{3}' index='{4}'> {1} </{0}>\n".format( self.tk.token_type(),
                                                                                            self.tk.token_val(),
                                                                                            category,
                                                                                            usage,
                                                                                            index))
        self.tk.advance()

    def compile_class_var_dec(self):
        """
        Compiles a static declaration or a field declaration
        :return:
        """

        while self.tk.token_val() in ['static', 'field']:
            # compile one declaration
            self.f.write("<classVarDec>\n")

            kind = self.tk.token_val().upper()
            self.write_elementary_expression_and_advance()
            assert self.is_type()
            o_type = self.tk.token_val()
            if o_type in TYPES:
                self.write_elementary_expression_and_advance()
            else:
                self.write_identifier_and_advance('class','call')
            assert self.is_var_name()
            name = self.tk.token_val()
            self.symbol_table.define(name, o_type, kind)
            index = self.symbol_table.index_of(name)
            self.write_identifier_and_advance(kind, 'definition', index)
            while self.tk.token_val() == ',':
                self.write_elementary_expression_and_advance()
                assert self.is_var_name()
                name = self.tk.token_val()
                self.symbol_table.define(name,o_type,kind)
                index = self.symbol_table.index_of(name)
                self.write_identifier_and_advance(kind,'definition',index)
            assert self.tk.token_val() == ';'
            self.write_elementary_expression_and_advance()
            # self.tk.advance()
            self.f.write("</classVarDec>\n")

        return

    def is_var_name(self):
        return self.tk.token_type() == 'identifier'

    def is_class_name(self):
        return self.tk.token_type() == 'identifier'

    def is_type(self):
        """
        returns true if current token is a type
        :return:
        """
        if self.tk.token_val() in ['int', 'char', 'boolean']:
            return True
        elif self.tk.token_type() == 'identifier':  # className
            return True
        else:
            return False

    def compile_subroutine(self):
        """
        Compiles a complete method, function or constructor
        subroutineDec format:
        ('constructor'|'function'|'method') ('void'|type) subroutineName
        '('parameterList') subroutineBody
        subroutineBody format:
        '{'varDec* statements '}'
        :return:
        """
        self.f.write("<subroutineDec>\n")
        while self.tk.token_val() in ['constructor', 'function', 'method']:
            self.write_elementary_expression_and_advance()

            assert (self.is_type() | (self.tk.token_val() == 'void')), 'expected "void"|type'
            self.current_ret_type = self.tk.token_val()
            if self.tk.token_val() in TYPES:
                self.write_elementary_expression_and_advance()
            else:
                # className
                self.write_identifier_and_advance('class', 'call')

            assert self.is_subroutine_name(), 'expected subroutine Name'
            self.current_subroutine = self.tk.token_val()
            self.write_identifier_and_advance('subroutine', 'definition')

            assert self.tk.token_val() == '(', 'expected "("'
            self.write_elementary_expression_and_advance()

            n_args = self.compile_parameter_list()

            assert self.tk.token_val() == ')', 'expected ")"'
            self.write_elementary_expression_and_advance()

            self.writer.write_function(self.current_class+self.current_subroutine, n_args)
            #  compile subroutine body:
            self.f.write("<subroutineBody>\n")

            assert self.tk.token_val() == '{', 'expected "{"'
            self.write_elementary_expression_and_advance()

            while self.tk.token_val() == 'var':
                self.compile_var_dec()

            self.compile_statements()

            assert self.tk.token_val() == '}'
            self.write_elementary_expression_and_advance()

            self.f.write("</subroutineBody>\n")
            self.f.write("</subroutineDec>\n")
            return

    def is_subroutine_name(self):
        return self.tk.token_type() == 'identifier'

    def compile_parameter_list(self):
        """
        Compiles a (possibly empty) parameter list,
        not including the enclosing "()"
        format: ((type varName) (','type varName)*)?
        :return: n_args, int
        """
        self.f.write("<parameterList>\n")
        n_args = 0
        if self.is_type():

            type = self.tk.token_val()
            if type in TYPES:
                self.write_elementary_expression_and_advance()
            else:
                # className
                self.write_identifier_and_advance('class', 'usage')

            assert self.is_var_name(), 'expected var name'
            name = self.tk.token_val()
            kind = 'ARG'
            self.symbol_table.define(name, type, kind)
            index = self.symbol_table.index_of(name)
            self.write_identifier_and_advance(kind, 'definition', index)
            n_args += 1

            while self.tk.token_val() == ',':
                self.write_elementary_expression_and_advance()

                assert self.is_type(), 'expected type'
                type = self.tk.token_val()
                self.write_elementary_expression_and_advance()

                assert self.is_var_name()
                name = self.tk.token_val()
                self.symbol_table.define(name, type, kind)
                index = self.symbol_table.index_of(name)
                self.write_identifier_and_advance(kind, 'definition', index)
                n_args += 1
        self.f.write("</parameterList>\n")
        return n_args

    def compile_var_dec(self):
        """
        Compiles a var declaration.
        format: 'var' type varName (','varName)*);
        :return:
        """
        self.f.write("<varDec>\n")
        assert self.tk.token_val() == 'var'
        kind = 'VAR'
        self.write_elementary_expression_and_advance()
        assert self.is_type()
        type = self.tk.token_val()
        if type in ['int','char','boolean']:
            self.write_elementary_expression_and_advance()
        else:
            # className
            self.write_identifier_and_advance('class', 'call')
        assert self.is_var_name()
        name = self.tk.token_val()
        self.symbol_table.define(name,type,kind)
        index = self.symbol_table.index_of(name)
        self.write_identifier_and_advance(kind,'definition',index)
        while self.tk.token_val() == ',':
            self.write_elementary_expression_and_advance()
            assert self.is_var_name()
            name = self.tk.token_val()
            self.symbol_table.define(name, type, kind)
            index = self.symbol_table.index_of(name)
            self.write_identifier_and_advance(kind, 'definition', index)

        assert self.tk.token_val() == ';'
        self.write_elementary_expression_and_advance()

        self.f.write("</varDec>\n")
        return

    def compile_statements(self):
        """
        Compiles a sequence of statements, not including the enclosing "{}".
        :return:
        """
        self.f.write("<statements>\n")
        while self.tk.token_val() in ['let', 'if', 'while', 'do', 'return']:
            if self.tk.token_val() == 'return':
                self.compile_return()
            elif self.tk.token_val() == 'if':
                self.compile_if()
            elif self.tk.token_val() == 'let':
                self.compile_let()
            elif self.tk.token_val() == 'do':
                self.compile_do()
            elif self.tk.token_val() == 'while':
                self.compile_while()
            else:
                raise Exception("unknown statement")
        self.f.write("</statements>\n")
        return

    def compile_do(self):
        """
        Compiles a do statement
        format: 'do' subroutineCall ';'
        :return:
        """
        self.f.write("<doStatement>\n")
        assert self.tk.token_val() == 'do'
        self.write_elementary_expression_and_advance()
        self.compile_subroutine_call()
        self.writer.write_pop('temp', 0)
        assert self.tk.token_val() == ';'
        self.write_elementary_expression_and_advance()
        self.f.write("</doStatement>\n")
        return

    def compile_subroutine_call(self):
        """
        Compiles a subroutineCall
        format: subroutineName '(' expressionList ')' | (className|varName)
                               '.' subroutineName '(' expressionList ')'
        """
        assert self.tk.token_type() == 'identifier'
        name = self.tk.token_type()
        if self.tk.peek_next_val() == '.':
            # className/varName
            if self.symbol_table.is_in_table(name):
                # varName
                category = self.symbol_table.kind_of(name)
                index = self.symbol_table.index_of(name)
                self.write_identifier_and_advance(category, 'call', index)
            else:
                # className
                self.write_identifier_and_advance('class', 'call')
        else:
            # subroutineName
            self.write_identifier_and_advance('subroutine', 'call')

        if self.tk.token_val() == '.':
            self.write_elementary_expression_and_advance()
            assert self.is_subroutine_name()
            self.write_identifier_and_advance('subroutine', 'call')
        assert self.tk.token_val() == '('
        self.write_elementary_expression_and_advance()
        self.compile_expression_list()
        assert self.tk.token_val() == ')'
        self.write_elementary_expression_and_advance()
        return

    def compile_let(self):
        """
        Compiles a let statement
        format: 'let' varName ('['expression']')? '=' 'expression ';'
        :return:
        """
        self.f.write("<letStatement>\n")
        assert self.tk.token_val() == 'let'
        self.write_elementary_expression_and_advance()
        assert self.is_var_name()
        name = self.tk.token_val()
        kind = self.symbol_table.kind_of(name)
        index = self.symbol_table.index_of(name)
        self.write_identifier_and_advance(kind,'call',index)
        if self.tk.token_val() == "[":
            self.write_elementary_expression_and_advance()
            self.compile_expression()
            assert self.tk.token_val() == ']'
            self.write_elementary_expression_and_advance()
        assert self.tk.token_val() == '='
        self.write_elementary_expression_and_advance()
        self.compile_expression()
        assert self.tk.token_val() == ';'
        self.write_elementary_expression_and_advance()

        self.f.write("</letStatement>\n")
        return

    def compile_while(self):
        """
        Compiles a while statement
        format: 'while' '(' expression ')' '{' statements'}'
        :return:
        """
        self.f.write("<whileStatement>\n")
        assert self.tk.token_val() == 'while'
        self.write_elementary_expression_and_advance()
        assert self.tk.token_val() == '('
        self.write_elementary_expression_and_advance()
        self.compile_expression()
        assert self.tk.token_val() == ')'
        self.write_elementary_expression_and_advance()
        assert self.tk.token_val() == '{'
        self.write_elementary_expression_and_advance()
        self.compile_statements()
        assert self.tk.token_val() == '}'
        self.write_elementary_expression_and_advance()
        self.f.write("</whileStatement>\n")
        return

    def compile_return(self):
        """
        Compiles a return statement
        :return:
        """
        self.f.write("<returnStatement>\n")
        assert self.tk.token_val() == 'return'
        if self.current_ret_type == 'void':
            self.writer.write_push('constant', 0)
        self.writer.write_return()
        self.write_elementary_expression_and_advance()
        if self.tk.token_val() != ';':
            self.compile_expression()
        assert self.tk.token_val() == ';'
        self.write_elementary_expression_and_advance()
        self.f.write("</returnStatement>\n")

    def compile_if(self):
        """
        Compiles an if statement.
        possibly with a trailing else clause.
        format: 'if' '('expression ')''{'statements'}('else'{'statements'}')?
        :return:
        """
        self.f.write("<ifStatement>\n")
        assert self.tk.token_val() == 'if'
        self.write_elementary_expression_and_advance()
        assert self.tk.token_val() == '('
        self.write_elementary_expression_and_advance()
        self.compile_expression()
        assert self.tk.token_val() == ')'
        self.write_elementary_expression_and_advance()
        assert self.tk.token_val() == '{'
        self.write_elementary_expression_and_advance()

        self.compile_statements()

        assert self.tk.token_val() == '}'
        self.write_elementary_expression_and_advance()
        if self.tk.token_val() == 'else':
            self.write_elementary_expression_and_advance()
            assert self.tk.token_val() == '{'
            self.write_elementary_expression_and_advance()
            self.compile_statements()
            assert self.tk.token_val() == '}'
            self.write_elementary_expression_and_advance()

        self.f.write("</ifStatement>\n")
        return

    def compile_expression(self):
        """
        Compiles an expression.
        format:
        term (op term)*
        :return:
        """
        self.f.write("<expression>\n")
        self.compile_term()
        while self.tk.token_val() in OP:
            self.write_elementary_expression_and_advance()
            self.compile_term()
        self.f.write("</expression>\n")

    def compile_term(self):
        """
        Compiles a 'term'. This routine is faced with a slight difficulty
        when trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier,
        the routine must distinguish between a variable, an array entry,
        and a subroutine call. A single look-ahead token,
        which may be one of "[", "(", or "." suffices to distinguish between
        the three possibilities. Any other token is not part of this term and should
        not be advanced over.
        format:
        integerConstant | stringConstant | keywordConstant | varName|
        varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        :return:
        """
        self.f.write("<term>\n")
        if self.tk.peek_next_val() == '[':
            assert self.is_var_name()
            # varName
            name = self.tk.token_val()
            category = self.symbol_table.kind_of(name)
            index = self.symbol_table.index_of(name)
            self.write_identifier_and_advance(category, 'call', index)
            self.write_elementary_expression_and_advance()  # '['
            self.compile_expression()
            assert self.tk.token_val() == ']'
            self.write_elementary_expression_and_advance()
        elif self.tk.peek_next_val() == '.':
            self.compile_subroutine_call()

        elif self.tk.token_val() == '(':
            self.write_elementary_expression_and_advance()
            self.compile_expression()
            assert self.tk.token_val() == ')'
            self.write_elementary_expression_and_advance()
        elif self.tk.token_val() in UNARY_OP:
            self.write_elementary_expression_and_advance()
            self.compile_term()
        elif self.tk.token_type() in ['integerConstant', 'stringConstant', 'keyword']:  # int,str,keyword
            self.write_elementary_expression_and_advance()
        else:
            # varName
            assert self.is_var_name()
            name = self.tk.token_val()
            kind = self.symbol_table.kind_of(name)
            index = self.symbol_table.index_of(name)
            self.write_identifier_and_advance(kind,'call',index)

        self.f.write("</term>\n")

    def compile_expression_list(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        format: (expression (','expression)*)?
        :return:
        """
        self.f.write("<expressionList>\n")
        if self.tk.token_val() != ')':  # expression list is not empty
            self.compile_expression()
            while self.tk.token_val() == ',':
                self.write_elementary_expression_and_advance()
                self.compile_expression()
        self.f.write("</expressionList>\n")
