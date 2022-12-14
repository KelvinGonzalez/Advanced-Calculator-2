from math import *
import os

objects = {}
functions = {}
variables = {}
temp_variables = {}

ans = []


def FindClosingParenthesis(text, index, starter="(", ender=")"):
    if text[index] != starter:
        return -1
    memory = 1
    for i in range(index + 1, len(text)):
        if text[i] == starter:
            memory += 1
        elif text[i] == ender:
            memory -= 1
        if memory == 0:
            return i
    return -1


def IsValidChar(char):
    return char.isalnum() or char == "_"


def IsValidName(name):
    for c in name:
        if not IsValidChar(c):
            return False
    return True


def IsCorrectName(start, name, prompt):
    count = len(name)
    i = start-1
    while i >= 0 and (IsValidChar(prompt[i]) or prompt[i] == "."):
        count += 1
        i -= 1
    i = start + len(name)
    while i < len(prompt) and IsValidChar(prompt[i]):
        count += 1
        i += 1
    return len(name) == count


def ParsePrompt(prompt):
    result_prompt = prompt
    for o in objects.keys():
        i = 0
        while i < len(result_prompt):
            if result_prompt[i:i+len(o)] == o and IsCorrectName(i, o, result_prompt):
                replacement_text = f"objects[\"{o}\"]"
                result_prompt = result_prompt[:i] + replacement_text + result_prompt[i+len(o):]
                i += len(replacement_text) - len(o)
            i += 1
    for f in functions.keys():
        i = 0
        while i < len(result_prompt):
            if result_prompt[i:i+len(f)] == f and IsCorrectName(i, f, result_prompt):
                replacement_text = f"functions[\"{f}\"]"
                result_prompt = result_prompt[:i] + replacement_text + result_prompt[i+len(f):]
                i += len(replacement_text) - len(f)
            i += 1
    for v in variables.keys():
        i = 0
        while i < len(result_prompt):
            if result_prompt[i:i+len(v)] == v and IsCorrectName(i, v, result_prompt):
                replacement_text = f"variables[\"{v}\"]"
                result_prompt = result_prompt[:i] + replacement_text + result_prompt[i+len(v):]
                i += len(replacement_text) - len(v)
            i += 1
    for tv in temp_variables.keys():
        i = 0
        while i < len(result_prompt):
            if result_prompt[i:i+len(tv)] == tv and IsCorrectName(i, tv, result_prompt):
                replacement_text = f"temp_variables[\"{tv}\"]"
                result_prompt = result_prompt[:i] + replacement_text + result_prompt[i+len(tv):]
                i += len(replacement_text) - len(tv)
            i += 1
    return result_prompt


def ParseFunctionParameters(function_text, parameters):
    result_function_text = function_text
    for i in range(len(parameters)):
        j = 0
        while j < len(result_function_text):
            if result_function_text[j:j+len(parameters[i])] == parameters[i] and IsCorrectName(j, parameters[i], result_function_text):
                replacement_text = f"args[{i}]"
                result_function_text = result_function_text[:j] + replacement_text + result_function_text[j+len(parameters[i]):]
                j += len(replacement_text) - len(parameters[i])
            j += 1
    return result_function_text


class Function:
    def __init__(self, funct, args=None):
        if args is None:
            args = []

        self.funct = funct
        self.args = args

    def __call__(self, *args):
        return eval(ParsePrompt(ParseFunctionParameters(self.funct, self.args)))

    def __repr__(self):
        temp_funct = self.funct.replace('"', '\\"')
        return f"Function(\"{temp_funct}\", {self.args})"

    def __str__(self):
        return f"f({', '.join(self.args)}) = {self.funct}"


class ObjectFunctionHelper:
    def __init__(self, object, function_name, function):
        self.object = object
        self.function_name = function_name
        self.function = function

    def __call__(self, *args):
        args_string = ", ".join([f"args[{i}]" for i in range(len(args))])
        return eval(f"self.object.do('{self.function_name}', {args_string})")

    def __repr__(self):
        return repr(self.function)

    def __str__(self):
        return str(self.function)


class Object:
    def __init__(self, name, variables=None, functions=None, static_variables=None, static_functions=None):
        if variables is None:
            variables = []
        if functions is None:
            functions = {}
        if static_variables is None:
            static_variables = {}
        if static_functions is None:
            static_functions = {}

        self.name = name
        self.variables = variables
        self.functions = functions
        self.static_variables = static_variables
        self.static_functions = static_functions

    def __call__(self, *args):
        if len(args) == len(self.variables):
            return Instance(self.name, list(args))
        elif len(args) < len(self.variables):
            return Instance(self.name, list(args) + [None for i in range(len(self.variables)-len(args))])
        else:
            return Instance(self.name, list(args)[:len(self.variables)])

    def __repr__(self):
        return f"Object(\"{self.name}\", {self.variables}, {self.functions}, {self.static_variables}, {self.static_functions})"

    def __str__(self):
        return f"{self.name}({', '.join(self.variables)})"

    def __getattr__(self, item):
        if item in self.static_variables.keys():
            return self.get(item)
        elif item in self.static_functions.keys():
            return ObjectFunctionHelper(self, item, self.static_functions[item])

    def get(self, name):
        return self.static_variables.get(name)

    def do(self, name, *args):
        function = self.static_functions.get(name)
        if function is None:
            return None
        args_string = ", ".join([f"args[{i}]" for i in range(len(args))])
        return eval(f"function({args_string})")

    def API(self):
        api_variables = " -" + ", ".join(self.variables)
        api_functions = "\n".join([f" -{f}({', '.join(self.functions[f].args)}) = {self.functions[f].funct}" for f in self.functions.keys()])
        api_static_variables = "\n".join([f" -{v} = {self.static_variables[v]}" for v in self.static_variables.keys()])
        api_static_functions = "\n".join([f" -{f}({', '.join(self.static_functions[f].args)}) = {self.static_functions[f].funct}" for f in self.static_functions.keys()])
        return f"{self.name} API:" + (f"\nVariables:\n{api_variables}" if len(self.variables) > 0 else "") + (f"\nFunctions:\n{api_functions}" if len(self.functions) > 0 else "") + (f"\nStatic Variables:\n{api_static_variables}" if len(self.static_variables) > 0 else "") + (f"\nStatic Functions:\n{api_static_functions}" if len(self.static_functions) > 0 else "")


class Instance:
    def __init__(self, object, variables=None):
        if variables is None:
            variables = []

        self.object = object
        self.variables = variables

    def __getattr__(self, item):
        if item in objects[self.object].variables:
            return self.get(item)
        elif item in objects[self.object].functions.keys():
            return ObjectFunctionHelper(self, item, objects[self.object].functions[item])

    def get(self, name):
        for i in range(len(objects[self.object].variables)):
            if objects[self.object].variables[i] == name:
                return self.variables[i]
        return None

    def do(self, name, *args):
        function = objects[self.object].functions.get(name)
        if function is None:
            return None
        args_string = ", ".join([f"args[{i}]" for i in range(len(args))])
        return eval(f"function(self, {args_string})")

    def __repr__(self):
        return f"Instance(\"{self.object}\", {self.variables})"

    def __str__(self):
        if objects[self.object].functions.get("str") is None:
            return self.__repr__()
        return objects[self.object].functions["str"](self)

    def __add__(self, other):
        if objects[self.object].functions.get("add") is None:
            return None
        return objects[self.object].functions["add"](self, other)
    def __radd__(self, other):
        if objects[self.object].functions.get("add") is None:
            return None
        return objects[self.object].functions["add"](self, other)

    def __sub__(self, other):
        if objects[self.object].functions.get("sub") is None:
            return None
        return objects[self.object].functions["sub"](self, other)

    def __mul__(self, other):
        if objects[self.object].functions.get("mul") is None:
            return None
        return objects[self.object].functions["mul"](self, other)
    def __rmul__(self, other):
        if objects[self.object].functions.get("mul") is None:
            return None
        return objects[self.object].functions["mul"](self, other)

    def __truediv__(self, other):
        if objects[self.object].functions.get("div") is None:
            return None
        return objects[self.object].functions["div"](self, other)

    def __mod__(self, other):
        if objects[self.object].functions.get("mod") is None:
            return None
        return objects[self.object].functions["mod"](self, other)

    def __pow__(self, other):
        if objects[self.object].functions.get("pow") is None:
            return None
        return objects[self.object].functions["pow"](self, other)

    def __cmp__(self, other):
        if objects[self.object].functions.get("cmp") is None:
            return None
        return objects[self.object].functions["cmp"](self, other)
    def __eq__(self, other):
        return self.__cmp__(other) == 0
    def __lt__(self, other):
        return self.__cmp__(other) < 0
    def __gt__(self, other):
        return self.__cmp__(other) > 0
    def __le__(self, other):
        return self < other or self == other
    def __ge__(self, other):
        return self > other or self == other

    def __neg__(self):
        if objects[self.object].functions.get("neg") is None:
            return None
        return objects[self.object].functions["neg"](self)

    def __invert__(self):
        if objects[self.object].functions.get("invert") is None:
            return None
        return objects[self.object].functions["invert"](self)

    def __abs__(self):
        if objects[self.object].functions.get("abs") is None:
            return None
        return objects[self.object].functions["abs"](self)

    def __len__(self):
        if objects[self.object].functions.get("len") is None:
            return None
        return objects[self.object].functions["len"](self)
    
    def __getitem__(self, key):
        if objects[self.object].functions.get("getitem") is None:
            return None
        return objects[self.object].functions["getitem"](self, key)

    def __getslice__(self, i, j):
        if objects[self.object].functions.get("getslice") is None:
            return None
        return objects[self.object].functions["getslice"](self, i, j)

    def __contains__(self, obj):
        if objects[self.object].functions.get("contains") is None:
            return None
        return objects[self.object].functions["contains"](self, obj)

    def __call__(self, *args):
        if objects[self.object].functions.get("call") is None:
            return None
        args_string = ", ".join([f"args[{i}]" for i in range(len(args))])
        return eval(f"self.do('call', {args_string})")


def SaveData(data, file):
    with open(file, "w") as save:
        for key in data.keys():
            save.write(key + ":" + data[key].__repr__() + "\n")


def LoadData(data, file):
    with open(file, "r") as load:
        for line in load:
            bits = line.split(":", 1)
            data[bits[0]] = (eval(bits[1]))


if os.path.isfile("objects.txt"):
    LoadData(objects, "objects.txt")
    for o in objects.keys():
        for f in objects[o].functions.keys():
            objects[o].functions[f].funct = objects[o].functions[f].funct.replace('\\"', '"')
        for f in objects[o].static_functions.keys():
            objects[o].static_functions[f].funct = objects[o].static_functions[f].funct.replace('\\"', '"')

if os.path.isfile("functions.txt"):
    LoadData(functions, "functions.txt")
    for f in functions.keys():
        functions[f].funct = functions[f].funct.replace('\\"', '"')
if os.path.isfile("variables.txt"):
    LoadData(variables, "variables.txt")


def IsUniqueName(name, ignore):
    if variables != ignore and name in variables.keys():
        return False
    if functions != ignore and name in functions.keys():
        return False
    if objects != ignore and name in objects.keys():
        return False
    if temp_variables != ignore and name in temp_variables.keys():
        return False
    return True


def IsUniqueNameInObject(name, object_name, ignore=None):
    object = objects[object_name]
    if ignore != "variables" and name in object.variables:
        return False
    if ignore != "functions" and name in object.functions.keys():
        return False
    if ignore != "static variables" and name in object.static_variables.keys():
        return False
    if ignore != "static functions" and name in object.static_functions.keys():
        return False
    return True


help = "User Manual:\n" \
       " -[expression] = [result]\n" \
       " -var [x] = [y]\n" \
       " -tempvar [x] = [y]\n" \
       " -funct [f]([x]) = [y]\n" \
       " -obj [o]([x])\n" \
       " -obj add [o] var [x]\n" \
       " -obj add [o] funct [f]([x]) = [y]\n" \
       " -obj add [o] staticvar [x] = [y]\n" \
       " -obj add [o] staticfunct [f]([x]) = [y]\n" \
       " -obj remove [o] [x/f]\n" \
       " -obj import [o]\n" \
       " -remove [x/f/o]\n" \
       " -variables\n" \
       " -functions\n" \
       " -objects\n" \
       " -results\n" \
       " -save\n" \
       " -exit"
print(help)

while True:
    try:
        prompt = input().strip()

        if prompt.startswith("var "):
            data = prompt[len("var "):].split("=")
            if IsValidName(data[0].strip()):
                if IsUniqueName(data[0].strip(), variables):
                    value = eval(ParsePrompt(data[1].strip()))
                    if type(value) == Function or type(value) == Object:
                        print("Variables cannot be of type Function or Object")
                        continue
                    variables[data[0].strip()] = value
                    print(f"Variable {data[0].strip()} created with value {str(value)}")
                else:
                    print("Name is already in use")
            else:
                print("Please use a valid name")

        elif prompt.startswith("tempvar "):
            data = prompt[len("tempvar "):].split("=")
            if IsValidName(data[0].strip()):
                if IsUniqueName(data[0].strip(), temp_variables):
                    value = eval(ParsePrompt(data[1].strip()))
                    if type(value) == Function or type(value) == Object:
                        print("Variables cannot be of type Function or Object")
                        continue
                    temp_variables[data[0].strip()] = value
                    print(f"Temporary variable {data[0].strip()} created with value {str(value)}")
                else:
                    print("Name is already in use")
            else:
                print("Please use a valid name")

        elif prompt.startswith("funct "):
            name = prompt[len("funct "):prompt.find("(")].strip()
            if IsValidName(name):
                if IsUniqueName(name, functions):
                    parameters = [x.strip() for x in prompt[prompt.find("(")+1:FindClosingParenthesis(prompt, prompt.find("("))].split(",")]
                    if "" in parameters:
                        parameters.remove("")
                    value = prompt[prompt.find("=")+1:].strip()
                    functions[name] = Function(value, parameters)
                    print(f"Function {name} created with value {value}")
                else:
                    print("Name is already in use")
            else:
                print("Please use a valid name")

        elif prompt.startswith("obj "):
            if prompt.startswith("obj add "):
                if "staticvar " in prompt:
                    name = prompt[len("obj add "):prompt.find("staticvar ")].strip()
                    if objects.get(name) is not None:
                        variable = prompt[prompt.find("var ")+len("var "):prompt.find("=")].strip()
                        if IsValidName(variable) and IsUniqueNameInObject(variable, name, "static variables"):
                            value = eval(ParsePrompt(prompt[prompt.find("=") + 1:].strip()))
                            objects[name].static_variables[variable] = value
                            print(f"Static variable {variable} with value {str(value)} added to object {name}")
                        else:
                            print("Please use a valid name")
                    else:
                        print("Object does not exist")

                elif "staticfunct " in prompt:
                    name = prompt[len("obj add "):prompt.find("staticfunct ")].strip()
                    if objects.get(name) is not None:
                        function = prompt[prompt.find("staticfunct ")+len("staticfunct "):prompt.find("(")].strip()
                        if IsValidName(function) and IsUniqueNameInObject(function, name, "static functions"):
                            parameters = [x.strip() for x in prompt[prompt.find("(")+1:FindClosingParenthesis(prompt, prompt.find("("))].split(",")]
                            if "" in parameters:
                                parameters.remove("")
                            value = prompt[prompt.find("=")+1:].strip()
                            objects[name].static_functions[function] = Function(value, parameters)
                            print(f"Static function {function} added to object {name} with value {value}")
                        else:
                            print("Please use a valid name")
                    else:
                        print("Object does not exist")

                elif "var " in prompt:
                    name = prompt[len("obj add "):prompt.find("var ")].strip()
                    if objects.get(name) is not None:
                        variable = prompt[prompt.find("var ")+len("var "):].strip()
                        if IsValidName(variable) and IsUniqueNameInObject(variable, name):
                            objects[name].variables.append(variable)
                            for v in variables.keys():
                                if type(variables[v]) == Instance and variables[v].object == name:
                                    variables[v].variables.append(None)
                            print(f"Variable {variable} added to object {name}")
                        else:
                            print("Please use a valid name")
                    else:
                        print("Object does not exist")

                elif "funct " in prompt:
                    name = prompt[len("obj add "):prompt.find("funct ")].strip()
                    if objects.get(name) is not None:
                        function = prompt[prompt.find("funct ")+len("funct "):prompt.find("(")].strip()
                        if IsValidName(function) and IsUniqueNameInObject(function, name, "functions"):
                            parameters = ["self"]+[x.strip() for x in prompt[prompt.find("(")+1:FindClosingParenthesis(prompt, prompt.find("("))].split(",")]
                            if "" in parameters:
                                parameters.remove("")
                            value = prompt[prompt.find("=")+1:].strip()
                            objects[name].functions[function] = Function(value, parameters)
                            print(f"Function {function} added to object {name} with value {value}")
                        else:
                            print("Please use a valid name")
                    else:
                        print("Object does not exist")

                else:
                    print("Only variables or functions can be added to an object")

            elif prompt.startswith("obj remove "):
                remove_bits = prompt[len("obj remove "):].split(" ")
                while "" in remove_bits:
                    remove_bits.remove("")
                if len(remove_bits) != 2:
                    print("Invalid removal selection")
                    continue
                if objects.get(remove_bits[0]) is None:
                    print(f"Object {remove_bits[0]} does not exist")

                if remove_bits[1] in objects[remove_bits[0]].variables:
                    index = -1
                    for i in range(len(objects[remove_bits[0]].variables)):
                        if objects[remove_bits[0]].variables[i] == remove_bits[1]:
                            index = i
                            break
                    for v in variables.keys():
                        if type(variables[v]) == Instance and variables[v].object == remove_bits[0]:
                            variables[v].variables.pop(index)
                    objects[remove_bits[0]].variables.remove(remove_bits[1])
                    print(f"Variable {remove_bits[1]} removed from object {remove_bits[0]}")

                elif remove_bits[1] in objects[remove_bits[0]].functions.keys():
                    objects[remove_bits[0]].functions.pop(remove_bits[1])
                    print(f"Function {remove_bits[1]} removed from object {remove_bits[0]}")

                elif remove_bits[1] in objects[remove_bits[0]].static_variables.keys():
                    objects[remove_bits[0]].static_variables.pop(remove_bits[1])
                    print(f"Static variable {remove_bits[1]} removed from object {remove_bits[0]}")

                elif remove_bits[1] in objects[remove_bits[0]].static_functions.keys():
                    objects[remove_bits[0]].static_functions.pop(remove_bits[1])
                    print(f"Static function {remove_bits[1]} removed from object {remove_bits[0]}")

                else:
                    print(f"Could not find property {remove_bits[1]} in object {remove_bits[0]}")

            elif prompt.startswith("obj import "):
                value = eval(prompt[len("obj import "):].strip())
                if type(value) == Object and IsValidName(value.name):
                    objects[value.name] = value
                    print(f"Object {value.name} created as {str(value)}")
                else:
                    print("Invalid import")

            else:
                name = prompt[len("obj "):prompt.find("(")].strip()
                if IsValidName(name):
                    if IsUniqueName(name, objects):
                        attributes = [x.strip() for x in prompt[prompt.find("(")+1:FindClosingParenthesis(prompt, prompt.find("("))].split(",")]
                        if "" in attributes:
                            attributes.remove("")
                        objects[name] = Object(name, attributes)
                        print(f"Object {name} created as {str(objects[name])}")
                    else:
                        print("Name is already in use")
                else:
                    print("Please use a valid name")

        elif prompt.startswith("remove "):
            for name in [x.strip() for x in prompt[len("remove "):].strip().split(" ")]:
                if name in variables.keys():
                    variables.pop(name)
                    print(f"Variable {name} removed")
                elif name in functions.keys():
                    functions.pop(name)
                    print(f"Function {name} removed")
                elif name in objects.keys():
                    for v in list(variables.keys()):
                        if type(variables[v]) == Instance and variables[v].object == name:
                            variables.pop(v)
                    objects.pop(name)
                    print(f"Object {name} removed and any variables of that type")
                elif name in temp_variables.keys():
                    temp_variables.pop(name)
                    print(f"Temporary variable {name} removed")
                else:
                    print(f"No such thing stored with name {name}")

        elif prompt == "variables":
            print("Variables:\n" + "\n".join([f" -{v} = {str(variables[v])}" for v in variables.keys()]) + ("\nTemp Variables:\n" + "\n".join([f" -{tv} = {str(temp_variables[tv])}" for tv in temp_variables.keys()]) if len(temp_variables) > 0 else ""))

        elif prompt == "functions":
            print("Functions:\n" + "\n".join([f" -{f}({', '.join(functions[f].args)}) = {str(functions[f].funct)}" for f in functions.keys()]))

        elif prompt == "objects":
            print("Objects:\n" + "\n".join([f" -{o} = {str(objects[o])}" for o in objects.keys()]))

        elif prompt == "results":
            print("Results:\n" + "\n".join([f" -{i}: {str(ans[i])}" for i in range(len(ans))]))

        elif prompt.strip() == "":
            continue

        elif prompt == "save":
            SaveData(objects, "objects.txt")
            SaveData(functions, "functions.txt")
            SaveData(variables, "variables.txt")
            print("Data was saved")

        elif prompt == "exit":
            SaveData(objects, "objects.txt")
            SaveData(functions, "functions.txt")
            SaveData(variables, "variables.txt")
            print("Data was saved")
            break

        else:
            if len(ans) >= 10:
                ans.pop()
            ans.insert(0, eval(ParsePrompt(prompt)))
            print(f"Result: {str(ans[0])}")

    except:
        print("Something went wrong")
