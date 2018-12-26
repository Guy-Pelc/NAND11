from logging import info, debug

SYMBOLS = ['{', '}', "(", ")", "[", "]", ".", ",", ";",
           "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]
SPECIAL_SYMBOLS = {
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;'}
KEYWORDS = ['class', 'constructor', 'function', 'method', 'field', 'static',
            'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',
            'let', 'do', 'if', 'else', 'while', 'return']


class JackTokenizer:

    def __init__(self, input_file_path):
        """
        Opens the input file/stream and gets ready to tokenize it.
        :param input_file_path:
        """
        with open(input_file_path, 'r') as f:
            content = f.readlines()

        clean_lines = self._clean_whitespace(content)
        self.token_str_list = self._tokens_str_from_clean_lines(clean_lines)
        self._index = None
        self._max_index = len(self.token_str_list) - 1

    @property
    def current_token(self):
        assert self._index is not None, "error, invalid token index"
        return self.token_str_list[self._index]

    @staticmethod
    def _tokens_str_from_clean_lines(clean_lines):
        """
        :param clean_lines: list of strings
        :return: list of strings that represent tokens
        """
        tokens = []

        for line in clean_lines:
            token = ''
            i = 0
            while i < len(line):
                if line[i] == '"':
                    token += line[i]
                    i += 1
                    while line[i] != '"':
                        token += line[i]
                        i += 1
                    token += line[i]
                else:
                    if line[i] == ' ':
                        if len(token) > 0:
                            tokens.append(token)
                        token = ''
                    elif line[i] in SYMBOLS:
                        if len(token) > 0:
                            tokens.append(token)
                        tokens.append(line[i])
                        token = ''
                    else:
                        token += line[i]
                i += 1

        return tokens

    @staticmethod
    def _clean_multiline_comments(content):
        clean_content = []
        is_multiline_comment = False
        for line in content:
            clean_line = ''
            len_line = len(line)
            i = 0

            while i < len_line:
                if line[i] == '/' and i < len_line - 1 and line[i + 1] == '*':
                    is_multiline_comment = True
                elif line[i] == "*" and i < len_line - 1 and line[i + 1] == '/':
                    is_multiline_comment = False
                    i += 2
                    continue
                if not is_multiline_comment:
                    clean_line += line[i]

                i += 1
            if len(clean_line) != 0:
                clean_content.append(clean_line)

        return clean_content

    @staticmethod
    def _clean_whitespace(content):
        """
        removes comments and whitespace
        :param content: array of strings
        :return: clean_content: array of strings
        """

        clean_content = []

        for line in content:
            clean_line = ''
            info('cleaning line: %s', line)
            for i in range(len(line)):
                # ignore one lined comments in format //...
                if line[i] == '/' and line[i + 1] == '/':
                    break
                debug('appending: %s', line[i])
                clean_line += line[i]
            info('clean line: %s', clean_line)
            clean_line = clean_line.strip()
            if len(clean_line) != 0:
                clean_content.append(clean_line)

        clean_content = JackTokenizer._clean_multiline_comments(clean_content)
        return clean_content

    def has_more_tokens(self):
        """
        Do we have more tokens in the input?
        :return: boolean
        """
        if len(self.token_str_list) == 0:
            return False
        return self._index != self._max_index

    def advance(self):
        """
        gets the next token from the input and makes it the current token.
        This method should only be called if hasMoreTokens() is true.
        Initially there is no current token.
        :return:
        """
        if self._index is None:
            self._index = 0
            return
        else:
            self._index += 1

    def peek_next_val(self):
        """
        gets value of next token,
        assumes that next token exists and that current token is not None
        :return: String, value of next token
        """
        assert self._index is not None
        self.advance()
        next_token_val = self.token_val()
        self._index -= 1

        return next_token_val

    def token_type(self):
        """
        Returns the type of the current token
        :return: TOKEN_TYPE : keyword, symbol, identifier, integerConstant, stringConstant
        """
        if self.current_token in SYMBOLS:
            return "symbol"
        elif self.current_token in KEYWORDS:
            return "keyword"
        elif self.current_token[0] == '"':
            return "stringConstant"
        elif self.current_token.isdigit():
            cur_int = int(self.current_token)
            assert (cur_int >= 0 & cur_int < 32768), "integer must be within 0 and 32767"
            return "integerConstant"
        else:
            assert not self.current_token[0].isdigit(), "first char must not be digit"
            for i in self.current_token:
                assert (i.isalnum() or i == "_"), " all chars in identifier must be alnum or '_'"
            return "identifier"

    def token_val(self):
        """
        gets value of current_token
        :return:
        """
        token_type = self.token_type()

        if token_type == "keyword":
            return self.key_word()
        elif token_type == "symbol":
            return self.symbol()
        elif token_type == "identifier":
            return self.identifier()
        elif token_type == "integerConstant":
            return self.int_val()
        elif token_type == "stringConstant":
            return self.string_val()
        else:
            raise Exception("invalid token_type")

    def key_word(self):
        """
        returns the keyword which is the current token.
        Should be called only when tokenType() is keyword
        :return: keyword: CLASS, METHOD,FUNCTION, CONSTRUCTOR, INT, BOOLEAN, CHAR, VOID,
                          VAR, STATIC, FIED, LET, DO, IF, ELSE, WHILE, RETURN, TRUE, FALSE, NULL, THIS
        """
        return self.current_token

    def symbol(self):
        """
        Returns the character which is the current token.
        Should be called only when tokenType() is symbol
        :return: char
        """
        symbol = self.current_token
        if symbol in SPECIAL_SYMBOLS:
            return SPECIAL_SYMBOLS[symbol]
        else:
            return symbol

    def identifier(self):
        """
        Returns the identifier which is the current token.
        Should be called only when tokenType() is identifier
        :return: string
        """
        return self.current_token

    def int_val(self):
        """
        Returns the integer value of the current token.
        Should be called only when tokenType() is integerConstant
        :return: int
        """
        return self.current_token

    def string_val(self):
        """
        Returns the string value of the current token, without the double quotes.
        Should be called only when tokenType() is stringConstant
        :return: int
        """
        string_val = self.current_token[1:-1]
        # replace special chars
        string_val = string_val.replace('&', '&amp;')
        string_val = string_val.replace('<', '&lt;')
        string_val = string_val.replace('>', '&gt;')

        return string_val
