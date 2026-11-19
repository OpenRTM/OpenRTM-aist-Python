#!/usr/bin/env python3
#
# @brief YAT: YAml Template text processor
# @date $Date: 2008-02-09 20:04:27 $
# @author Norkai Ando <n-ando@aist.go.jp>
#
# Copyright (C) 2008 Noriaki Ando, All rights reserved.
#
# $Id: yat.py 775 2008-07-28 16:14:45Z n-ando $
#

#
# Usage:
# ------------------------------------------------------------
# import yaml
# import yat
#
# dict   = yaml.load(open(filename, "r").read())
# t      = yat.Template(template, "\[", "\]")
# result = t.generate(dict)
# ------------------------------------------------------------
#
# 1. Simple directive:
#    [dictionary_key]
#
#    Nested dictionaries can be expressed by dotted expression.
#
# example:
# dict = {"a": "This is a",
#         "b": {"1": "This is b.1",
#               "2": "This is b.2"}
#        }
#
# template:
# [a]
#
# [b.1]
#
# [b.2]
#
# result:
# This is a
# This is b.1
# This is b.2
#
#
# 2. "for" directive:
#    [for key in list] statement [endfor]
#
#    Iterative evaluation for listed values is performed by "for" statement.
#    In iteration at each evaluation, the value of the list is assigned to
#    "key". The "key" also can be the nested dictionary directive.
#
# example:
# dict = {"list": [0, 1, 2],
#         "listed_dict": [
#           {"name": "x", "value": "1.0"},
#           {"name": "y", "value": "0.2"},
#           {"name": "z", "value": "0.1"}]}
#
# template:
# [for lst in list]
# [lst],
# [endfor]
# [for lst in listed_dict]
# [lst.name]: [lst.value]
#
# [endfor]
#
# result:
# 1, 2, 3,
# x: 1.0
# y: 0.2
# x: 0.1
#
#
# 3. "if-index" directive:
#    [for key in val]
#    [if-index key is first|even|odd|last|NUMBER] statement1
#    [elif-index key is first|even|odd|last|NUMBER] statement2
#    [endif][endfor]
#
#    "if-index" is used to specify the index of the "for" iteration.
#    The "key" string which is defined in the "for" statement is used as index.
#    A number or predefined directives such as "first", "even", "odd" and
#    "last" can be used to specify the index.
#
# example:
# dict = {"list": [0,1,2,3,4,5,6,7,8,9,10]}
#
# template:
# [for key in list]
# [if-index key is 3] [key] is hoge!!
# [elif-index key is 6] [key] is foo!!
# [elif-index key is 9] [key] is bar!!
# [elif-index key is first] [key] is first
# [elif-index key is last] Omoro-------!!!!
# [elif-index key is odd] [key] is odd number
# [elif-index key is even] [key] is even number
# [endif]
# [endfor]
#
# result:
#  0 is first
#  1 is odd number
#  2 is even number
#  3 is hoge!!
#  4 is even number
#  5 is odd number
#  6 is foo!!
#  7 is odd number
#  8 is even number
#  9 is bar!!
#  Omoro-------!!!!
#
#
# 4. "if" directive: [if key is value] text1 [else] text2 [endif]
#    If "key" is "value", "text1" appears, otherwise "text2" appears.
#
# example:
# dict = {"key1": "a", "key2": "b"}
#
# template:
# [if key1 is a]
# The key1 is "a".
# [else]
# This key1 is not "a".
# [endif]
#
# result:
# The key1 is "a".
#
#
# 5. "if-any" directive: [if-any key1] text1 [else] text2 [endif]
#    If the "key1" exists in the dictionary, "text1" appears, otherwise
#    "text2" appears.
#
# example:
# dict = {"key1": "a", "key2": "b"}
#
# template:
# [if-any key1]
# key1 exists.
# [endif][if-any key3]
# key3 exists.
# [else]
# key3 does not exists.
# [endif]
#
# result:
# key1 exists.
# key3 does not exists.
#
#
# 6. bracket and comment:
#    [[] is left bracket if begin mark is "["
#    [# comment ] is comment if begin/end marks are "[" and "]"
#
# example:
# dict = {}
#
# template:
# [[]bracket]
# [# comment]
#
# result:
# [bracket]
#
import typing as _typing
import ast
import json
import operator
import re
import sys


class Template:
    """
    usage:
      tempalte_text = read template text from file
      dictionary    = create dictionaly by using yaml
      t = Template(tempalte_text)
      generated_text = t.generate(dictionary)

    """

    def __init__(self, template: str, begin_mark: str = r"\[", end_mark: str = r"\]") -> None:
        self.__procs = [self.__proc_text,
                        self.__proc_cmd,
                        self.__proc_bracket]
        self.template = template

        # regular expression to devide text into DIRECTIVE, BRACKET and COMMENT
        #
        # default:
        # START_MARK: "["
        # END_MARK  : "]"
        # -> START_MARK and END_MARK can be given in ctor
        #
        # ITEM: (?:"(?:[^\\"]|\\.)*"|[-\w.]+)
        # \[(ITEM(?: +ITEM)*)\]|(\[\[\])|\[#[^\]]*\]
        # ~~~~~~~~(1)~~~~~~ ~~(2)~~~ ~~~(3)~~~~~
        # (1) COMMAND  : '[' ITEM (whitespace ITEM)* ']
        #     ITEM     : STRING | NAME
        #     STRING   : '"' (not-slash-or-dquote | '\' anychar)* '"'
        #     NAME     : (alphanum | '_' | '-' | '.')+
        # (2) BEGIN_MARK_ESCAPE : '[[]'
        # (3) COMMENT  : '[#' not-rbracket
        #
        # re_item      = r'(?:"(?:[^\\"]|\\.)*"|[-\w.]+)'
        # re_command   = r'\[(%s(?: +%s)*)\]' % (re_item, re_item)
        # re_beginmark = r'\[\[\]'
        # re_comment   = r'\[#[^\]]*\]'
        # re_parse     = re.compile(r'%s|(%s)|%s'
        #                     % (re_command, re_beginmark, re_comment))
        # re_args      = re.compile(r'"(?:[^\\"]|\\.)*"|[-\w.]+')
        #
        #
        re_item = r'(?:"(?:[^\\"]|\\.)*"|[-\w.:]+)'
        re_command = r'%s(%s(?: +%s)*)%s' % \
            (begin_mark, re_item, re_item, end_mark)
        re_bracket = r'%s%s%s' % \
            (begin_mark, begin_mark, end_mark)
        re_comment = r'%s#[^%s]*%s' % \
            (begin_mark, end_mark, end_mark)
        self.begin_mark = begin_mark.replace("\\", "")
        self.re_parse = re.compile(r'%s|(%s)|%s' %
                                   (re_command, re_bracket, re_comment))
        self.re_args = re.compile(r'"(?:[^\\"]|\\.)*"|[-\w.:]+')
        self.re_number = re.compile(r'[0-9]+')

        # tokenize input text
        self.token = self.re_parse.split(self.template)
        self.token_len = len(self.token)

        # initialize variables
        self.script = program
        self.indent = 4
        self.script_level = 2
        self.level = 0
        self.index = 0
        self.cmd_cxt = []

        # parse token
        self.__parse_template(self.token)

        return

    def generate(self, dict: '_typing.Dict[str, _typing.Any]') -> str:
        renderer = GeneratorBase(self.token, dict)
        generated_class, = ast.parse(self.script).body
        process = next(method for method in generated_class.body
                       if isinstance(method, ast.FunctionDef) and method.name == "process")
        try:
            _TemplateProgram(renderer).run(process.body)
        except YATException as exc:
            renderer.print_error(exc)
            sys.exit(-1)
        return renderer.text

    def get_script(self) -> str:
        return self.script

    def __push_level(self) -> None:
        self.level += 1

    def __pop_level(self) -> None:
        self.level -= 1

    def __write_cmd(self, cmd: str) -> None:
        tmp_cmd = self.__indent()
        tmp_cmd += "self.set_index(%s)\n" % (self.index)
        self.script += tmp_cmd
        self.__write_cmd_noindex(cmd)

    def __write_cmd_noindex(self, cmd: str) -> None:
        tmp_cmd = self.__indent()
        tmp_cmd += cmd + "\n"
        self.script += tmp_cmd

    def __parse_template(self, dict: '_typing.List[_typing.Optional[str]]') -> None:
        try:
            # split into (TEXT DIRECTIVE BRACKET)* TEXT
            self.__parse()
        except YATException as e:
            self.__print_error(e)
            sys.exit(-1)

    def __indent(self) -> str:
        indent = " " * ((self.script_level + self.level) * self.indent)
        return indent

    def __parse(self) -> None:
        while self.index < self.token_len:
            self.__procs[self.index % 3]()
            self.index += 1

    def __proc_text(self) -> '_typing.Optional[bool]':
        if self.token[self.index] is None:
            return
        cmd_text = "self.write_token(%s)" % (self.index)
        self.__write_cmd(cmd_text)
        return True

    def __proc_bracket(self) -> '_typing.Optional[bool]':
        if self.token[self.index] is None:
            return
        cmd_text = "self.write(%s)" % json.dumps(self.begin_mark, ensure_ascii=False)
        self.__write_cmd(cmd_text)
        return True

    def __proc_cmd(self) -> '_typing.Optional[bool]':
        cmd = self.token[self.index]
        try:
            args = self.re_args.findall(cmd)
        except BaseException:
            return
        self.del_nl_after_cmd()
        argc = len(args)
        if argc == 0:
            raise InvalidDirective(self.lineno(), "_an empty directive_ ")

        # simple directive
        if argc == 1:
            if args[0] == "endfor":
                self.__endfor_cmd(args)
                return
            elif args[0] == "else":
                self.__else_cmd(args)
                return
            elif args[0] == "last":
                self.__last_cmd(args)
                return
            elif args[0] == "endif":
                self.__endif_cmd(args)
                return
            else:
                self.__cmd(args)
                return
        elif argc == 2:
            if args[0] == "if-any":
                self.__if_any_cmd(args)
                return
        elif argc == 4:  # [for key in value]
            if args[0] == "for" and args[2] == "in":
                self.__for_cmd(args)
                return True
            elif args[0] == "if" and args[2] == "is":
                self.__if_cmd(args)
            elif args[0] == "elif" and args[2] == "is":
                self.__elif_cmd(args)
            elif args[0] == "if-index" and args[2] == "is":
                self.__if_index_cmd(args)
            elif args[0] == "elif-index" and args[2] == "is":
                self.__elif_index_cmd(args)
            else:
                raise InvalidDirective(self.lineno(), cmd)
        else:
            raise InvalidDirective(self.lineno(), cmd)
        return True

    def __cmd(self, args: list) -> None:
        cmd_text = "self.write_dict(%s)" % json.dumps(args[0], ensure_ascii=False)
        self.__write_cmd(cmd_text)

    # ------------------------------------------------------------
    # [for] commands
    # - for
    # - last
    # - endfor
    # ------------------------------------------------------------
    def __for_cmd(self, args: list) -> None:
        """
        The following [for] directive
          [for tmp_key in directive]
        is converted into the following python command.
          for i in len(directive):
              self.dicts.append({tmp_key: ditective[i])
        and, endfor directive terminate as the following,
              self.dicts.pop()
        """
        key = args[1]
        directive = args[3]
        if not key.isidentifier():
            raise InvalidDirective(self.lineno(), "invalid loop key: " + key)
        # (key)     : variable string of index variable for [for] block
        # (key)_list: list value of specified directive
        # (key)_len : length of the list
        cmd_text = "%s_list = self.get_list(%s)" % (key, json.dumps(directive, ensure_ascii=False))
        self.__write_cmd(cmd_text)
        cmd_text = "%s_len = len(%s_list)" % (key, key)
        self.__write_cmd(cmd_text)
        cmd_text = "for %s_index in range(len(%s_list)):" % (key, key)
        self.__write_cmd(cmd_text)
        self.__push_level()
        cmd_text = "self.push_dict({\"%s\": %s_list[%s_index]})" \
            % (key, key, key)
        self.__write_cmd(cmd_text)
        self.cmd_cxt.append("for")

    def __endfor_cmd(self, args: list) -> None:
        try:
            cxt = self.cmd_cxt.pop()
            if cxt != "for":
                raise UnmatchedBlock(self.lineno(), "endfor")
            self.__write_cmd("self.pop_dict()")
            self.__pop_level()
        except BaseException:
            print(args, self.lineno())
            raise UnmatchedBlock(self.lineno(), "endfor")
        return

    # end of [for] commands
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # [if] commands
    # - if
    # - if-index
    # - if-any
    # ------------------------------------------------------------
    def __if_cmd(self, args: list) -> None:
        """
        The following [if] directive
          [if directive is string]
        is converted into the following python command.
          if self.__get_string() == "string":
        """
        directive = args[1]
        string = args[3]
        if string.startswith(('"', "'")):
            string = ast.literal_eval(string)
        cmd_text = "if self.get_text(%s) == %s:" % (
            json.dumps(directive, ensure_ascii=False), json.dumps(string, ensure_ascii=False))
        self.__write_cmd(cmd_text)
        self.__push_level()
        self.cmd_cxt.append("if")
        return

    def __elif_cmd(self, args: list) -> None:
        if self.cmd_cxt[-1] != "if":
            raise UnmatchedBlock(self.lineno(), "elif")
        directive = args[1]
        string = args[3]
        if string.startswith(('"', "'")):
            string = ast.literal_eval(string)
        cmd_text = "elif self.get_text(%s) == %s:" % (
            json.dumps(directive, ensure_ascii=False), json.dumps(string, ensure_ascii=False))
        self.__pop_level()
        self.__write_cmd_noindex(cmd_text)
        self.__push_level()
        return

    # [if-index] commands
    def __if_index_cmd(self, args) -> None:
        # [if-index KEY is [first|even|odd|last|NUMBER]]
        #  ~~~0~~~  ~1~  2 ~~~~~~~~~~~~~~3~~~~~~~~~~~~
        cmdlist = {"first": "if %s_index == 0:",
                   "even": "if (%s_index %% 2) == 0:",
                   "odd": "if (%s_index %% 2) != 0:",
                   "last": "if %s_index == %s_len - 1:"}
        key = args[1]
        cmd = args[3]
        if not key.isidentifier():
            raise InvalidDirective(self.lineno(), "invalid loop key: " + key)
        if self.re_number.fullmatch(cmd):
            cmd_text = "if %s_index == %s:" % (key, int(cmd))
        elif cmd in cmdlist:
            if cmd == "last":
                cmd_text = cmdlist[cmd] % (key, key)
            else:
                cmd_text = cmdlist[cmd] % (key)
        else:
            raise InvalidDirective(self.lineno(), ''.join(args))
        self.__write_cmd(cmd_text)
        self.__push_level()
        self.cmd_cxt.append("if-index")

    def __elif_index_cmd(self, args) -> None:
        if self.cmd_cxt[-1] != "if-index":
            raise UnmatchedBlock(self.lineno(), "elif-index")
        # [elif-index KEY is [first|even|odd|last|NUMBER]]
        #  ~~~0~~~  ~1~  2 ~~~~~~~~~~~~~~3~~~~~~~~~~~~
        cmdlist = {"first": "elif %s_index == 0:",
                   "even": "elif (%s_index %% 2) == 0:",
                   "odd": "elif (%s_index %% 2) != 0:",
                   "last": "elif %s_index == %s_len - 1:"}
        key = args[1]
        cmd = args[3]
        if not key.isidentifier():
            raise InvalidDirective(self.lineno(), "invalid loop key: " + key)
        if self.re_number.fullmatch(cmd):
            cmd_text = "elif %s_index == %s:" % (key, int(cmd))
        elif cmd in cmdlist:
            if cmd == "last":
                cmd_text = cmdlist[cmd] % (key, key)
            else:
                cmd_text = cmdlist[cmd] % (key)
        else:
            raise InvalidDirective(self.lineno(), ' '.join(args))
        self.__pop_level()
        self.__write_cmd_noindex(cmd_text)
        self.__push_level()

    # [if-any] command
    def __if_any_cmd(self, args: list) -> None:
        directive = args[1]
        cmd_text = "if self.has_key(%s):" % json.dumps(directive, ensure_ascii=False)
        self.__write_cmd(cmd_text)
        self.__push_level()
        self.cmd_cxt.append("if-any")
        return

    def __elif_any_cmd(self, args) -> None:
        if self.cmd_cxt[-1] != "if-any":
            raise UnmatchedBlock(self.lineno(), "elif-any")
        directive = args[1]
        cmd_text = "if self.has_key(%s):" % json.dumps(directive, ensure_ascii=False)
        self.__pop_level()
        self.__write_cmd_noindex(cmd_text)
        self.__push_level()
        return

    # [else], [endif] commands
    def __else_cmd(self, args: list) -> None:
        if self.cmd_cxt[-1] != "if" and self.cmd_cxt[-1] != "if-index" \
                and self.cmd_cxt[-1] != "if-any":
            raise UnmatchedBlock(self.lineno(), "else")
        self.__pop_level()
        self.__write_cmd_noindex("else:")
        self.__push_level()
        return

    def __endif_cmd(self, args: list) -> None:
        if self.cmd_cxt[-1] != "if" and self.cmd_cxt[-1] != "if-index" \
                and self.cmd_cxt[-1] != "if-any":
            raise UnmatchedBlock(self.lineno(), "endif")
        self.cmd_cxt.pop()
        self.__pop_level()
        return
    # end of [if] commands
    # ------------------------------------------------------------

    def __print_error(self, e) -> None:
        print("Parse Error: line", e.lineno, "in input data")
        print("  " + ''.join(nesteditem(e.value)))
        lines = self.template.split("\n")
        length = len(lines)
        print("------------------------------------------------------------")
        for i in range(1, 10):
            line_index = e.lineno - 6 + i
            if line_index > 0 and line_index < length:
                print(lines[line_index])
                if i == 5:
                    uline = '~' * len(lines[line_index])
                    print(uline)
        print("------------------------------------------------------------")

    def del_nl_after_cmd(self) -> None:
        # next text index after command
        next = self.index + 2
        if next > self.token_len:
            return
        if self.token[next] is None:
            return
        text = self.token[next]
        tlen = len(text)
        if tlen > 0 and text[0] == '\n':
            self.token[next] = text[1:]
            return
        elif tlen > 0 and text[0] == '\r':
            self.token[next] = text[1:]
            return
        elif tlen > 1 and text[0:2] == '\r\n':
            self.token[next] = text[2:]

    def lineno(self) -> int:
        line_number = 1
        for i in range(self.index):
            if isinstance(self.token[i], str):
                line_number += self.token[i].count('\n')
        for i in range(1, self.index, 3):
            line_number += 1
        return line_number


# ------------------------------------------------------------
# Generator and GeneratorBase classes
# ------------------------------------------------------------
program = """
class Generator(GeneratorBase):
    def __init__(self, token, dict):
        GeneratorBase.__init__(self, token, dict)
    def generate(self):
        try:
            self.process()
        except YATException as e:
            self.print_error(e)
            sys.exit(-1)
        return self.text

    def process(self):
"""


class _TemplateProgram:
    """Interpret the small set of operations emitted by the template parser."""

    _operators = {ast.Mod: operator.mod, ast.Sub: operator.sub,
                  ast.Eq: operator.eq, ast.NotEq: operator.ne}

    def __init__(self, renderer: 'GeneratorBase') -> None:
        self._variables = {}
        self._functions = {"len": len, "range": range}
        self._methods = {
            "set_index": renderer.set_index, "write_token": renderer.write_token,
            "write": renderer.write, "write_dict": renderer.write_dict,
            "get_list": renderer.get_list, "get_text": renderer.get_text,
            "has_key": renderer.has_key, "push_dict": renderer.push_dict,
            "pop_dict": renderer.pop_dict,
        }

    def run(self, statements: '_typing.Iterable[ast.stmt]') -> None:
        for statement in statements:
            if isinstance(statement, ast.Expr):
                self._value(statement.value)
            elif isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                self._assign(statement.targets[0], self._value(statement.value))
            elif isinstance(statement, ast.For) and not statement.orelse:
                for value in self._value(statement.iter):
                    self._assign(statement.target, value)
                    self.run(statement.body)
            elif isinstance(statement, ast.If):
                self.run(statement.body if self._value(statement.test) else statement.orelse)
            else:
                raise ValueError("unsupported template statement: " + type(statement).__name__)

    def _assign(self, target: 'ast.expr', value) -> None:
        if not isinstance(target, ast.Name) or not target.id.endswith(("_list", "_len", "_index")):
            raise ValueError("invalid template assignment")
        self._variables[target.id] = value

    def _value(self, expression: 'ast.expr'):
        if isinstance(expression, ast.Constant):
            return expression.value
        if isinstance(expression, ast.Name):
            return self._variables[expression.id]
        if isinstance(expression, ast.Dict):
            return {self._value(key): self._value(value)
                    for key, value in zip(expression.keys, expression.values)}
        if isinstance(expression, ast.Subscript):
            index = expression.slice
            if isinstance(index, ast.Index):
                index = index.value
            return self._value(expression.value)[self._value(index)]
        if isinstance(expression, ast.BinOp):
            operation = self._operators[type(expression.op)]
            return operation(self._value(expression.left), self._value(expression.right))
        if isinstance(expression, ast.Compare) and len(expression.ops) == 1:
            operation = self._operators[type(expression.ops[0])]
            return operation(self._value(expression.left), self._value(expression.comparators[0]))
        if isinstance(expression, ast.Call) and not expression.keywords:
            target = expression.func
            if isinstance(target, ast.Name) and target.id in self._functions:
                function = self._functions[target.id]
            elif (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self" and target.attr in self._methods):
                function = self._methods[target.attr]
            else:
                raise ValueError("unsupported template call")
            return function(*(self._value(arg) for arg in expression.args))
        raise ValueError("unsupported template expression: " + type(expression).__name__)


class GeneratorBase:
    def __init__(self, token: list, dict: '_typing.Dict[str, _typing.Any]') -> None:
        self.token = token
        self.dicts = [dict]
        self.index = 0
        self.text = ""

    def print_error(self, e: 'NotFound') -> None:
        print("\nTemplate Generation Error: line", e.lineno, "in input data")
        print("  " + ''.join(nesteditem(e.value)))
        temp = ""
        for i, s in enumerate(self.token):
            if s is not None:
                if i % 3 == 1:
                    temp += "[" + s + "]\n"
                else:
                    temp += s
        lines = temp.split("\n")
        length = len(lines)
        print("------------------------------------------------------------")
        for i in range(1, 10):
            line_index = e.lineno - 6 + i
            if line_index > 0 and line_index < length:
                print(lines[line_index])
                if i == 5:
                    uline = '~' * len(lines[line_index])
                    print(uline)
        print("------------------------------------------------------------")

    def set_index(self, index: int) -> None:
        self.index = index

    def push_dict(self, dict: '_typing.Dict[str, _typing.Any]') -> None:
        self.dicts.append(dict)

    def pop_dict(self) -> None:
        if len(self.dicts) < 2:
            raise UnmatchedBlock(self.lineno(), "")
        self.dicts.pop()

    def write(self, text: str) -> None:
        self.text += text

    def write_dict(self, keytext: str) -> None:
        self.write(self.get_text(keytext))

    def write_token(self, index: int) -> None:
        self.write(self.token[index])

    def lineno(self) -> int:
        cnt = 1
        for i in range(0, self.index, 3):
            if self.token[i] is not None:
                cnt += self.token[i].count('\n')
        # count deleted '\n' after commands
        for i in range(1, self.index, 3):
            if self.token[i] is not None:
                cnt += 1
        return cnt

    def get_text(self, keytext: str) -> str:
        val = self.get_value(keytext)
        if isinstance(val, str):
            return val
        if isinstance(val, (int, float)):
            return str(val)
        raise UnexpectedData(self.lineno(), "\"" + keytext + "\" should have string, int or float value.")

    def get_list(self, keytext: str) -> '_typing.List[_typing.Any]':
        val = self.get_value(keytext)
        if not isinstance(val, list):
            raise UnexpectedData(self.lineno(),
                                 "\"" + keytext + "\" should have list value.")
        return val

    def has_key(self, keytext: str) -> bool:
        try:
            self.get_value(keytext)
            return True
        except NotFound:
            return False

    def get_value(self, keytext: str):
        keys = keytext.split('.')
        for i in range(len(self.dicts) - 1, -1, -1):
            dict_value = self.get_dict_value(keys, self.dicts[i])
            if dict_value is not None:
                return dict_value
        raise NotFound(self.lineno(), keytext)

    def get_dict_value(self, keys: list, data):
        length = len(keys)
        d = data
        for i in range(length):
            if isinstance(d, dict) and keys[i] in d:
                d = d[keys[i]]
            else:
                return None
        return d


# ------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------
class YATException(Exception):
    pass


class UnknownError(YATException):
    def __init__(self, lineno: int) -> None:
        self.lineno = lineno
        self.value = "Unknown error."


class UnmatchedBlock(YATException):
    def __init__(self, lineno: int, msg: str) -> None:
        self.lineno = lineno
        self.value = "Unmatched block error: " + msg


class UnexpectedData(YATException):
    def __init__(self, lineno: int, msg: str) -> None:
        self.lineno = lineno
        self.value = msg


class NotFinalElement(YATException):
    def __init__(self, dictkey, dictvalue) -> None:
        self.value = "Specified key is not final element: ", \
            dictkey, "=>", dictvalue


class InvalidDirective(YATException):
    def __init__(self, lineno: int, directive: str) -> None:
        self.lineno = lineno
        self.value = "Invalid directive: \"[" + directive + "]\""


class UnmatchedData(YATException):
    def __init__(self, lineno: int, description: str) -> None:
        self.lineno = lineno
        self.value = "Unmatched data and input: ", description


class NotFound(YATException):
    def __init__(self, lineno: int, description: str) -> None:
        self.lineno = lineno
        self.value = "Value not found for: \"" + description + "\""

# ------------------------------------------------------------
# other functions
# ------------------------------------------------------------


def nesteditem(aList):
    for anItem in aList:
        if isinstance(anItem, list):
            for subitem in nesteditem(anItem):
                yield subitem
        else:
            yield anItem


if __name__ == "__main__":
    dict = []
    template = []
    # ------------------------------------------------------------
    # Example 0
    # ------------------------------------------------------------
    dict.append({"a": "This is a",
                 "b": {"1": "This is b.1",
                       "2": "This is b.2"}
                 })
    template.append("""[a]

[b.1]

[b.2]""")

    # ------------------------------------------------------------
    # Example 1
    # ------------------------------------------------------------
    dict.append({"list": [0, 1, 2],
                 "listed_dict": [
                {"name": "x", "value": "1.0"},
                {"name": "y", "value": "0.2"},
                {"name": "z", "value": "0.1"}]})
    template.append("""[for lst in list]
[lst],
[endfor]
[for lst in listed_dict]
[lst.name]: [lst.value]

[endfor]""")

    # ------------------------------------------------------------
    # Example 2
    # ------------------------------------------------------------
    dict.append({"list": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
    template.append("""[for key in list]
[if-index key is 3] [key] is hoge!!
[elif-index key is 6] [key] is foo!!
[elif-index key is 9] [key] is bar!!
[elif-index key is first] [key] is first
[elif-index key is last] Omoro-------!!!!
[elif-index key is odd] [key] is odd number
[elif-index key is even] [key] is even number
[endif]
[endfor]""")

    # ------------------------------------------------------------
    # Example 3
    # ------------------------------------------------------------
    dict.append({"key1": "a", "key2": "b"})
    template.append("""[if key1 is a]
The key1 is "a".
[else]
This key1 is not "a".
[endif]""")

    # ------------------------------------------------------------
    # Example 4
    # ------------------------------------------------------------
    dict.append({"key1": "a", "key2": "b"})
    template.append("""[if-any key1]
key1 exists.
[endif][if-any key3]
key3 exists.
[else]
key3 does not exists.
[endif]""")

    dict.append({})
    template.append("""
[[]bracket]
[# comment]
""")

    import yaml
    if len(dict) == len(template):
        for i in range(len(dict) - 1, len(dict)):
            t = Template(template[i])
            print("-" * 60)
            print("Example:", i)
            print("-" * 60)
            print("Template:\n")
            print(template[i])
            print("-" * 60)
            print("Dictionary:\n")
            print(yaml.dump(dict[i], default_flow_style=False))
            print("-" * 60)
            print("Generated Script:\n")
            print(t.get_script())
            print("-" * 60)
            print("Generated Text:\n")
            print(t.generate(dict[i]))
            print("")
