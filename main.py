from math import *
import os

objects = {}
functions = {}
variables = {}


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
    while i >= 0 and IsValidChar(prompt[i]):
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
    return result_prompt


class Function:
    def __init__(self, funct):
        self.funct = funct

    def __call__(self, *x):
        return eval(ParsePrompt(self.funct))

    def __repr__(self):
        return f"Function(\"{self.funct}\")"

    def __str__(self):
        return f"f(x) = {self.funct}"

    def __add__(self, other):
        return Function(f"{self.funct} + {other.funct}")

    def __sub__(self, other):
        return Function(f"{self.funct} - ({other.funct})")

    def __mul__(self, other):
        return Function(f"({self.funct}) * ({other.funct})")

    def __truediv__(self, other):
        return Function(f"({self.funct}) / ({other.funct})")

    def composite(self, other):
        return Function(self.funct.replace("x", f"({other.funct})"))


class Object:
    def __init__(self, name, variables=None, functions=None):
        if variables is None:
            variables = []
        if functions is None:
            functions = {}

        self.name = name
        self.variables = variables
        self.functions = functions

    def __call__(self, *args):
        if len(args) == len(self.variables):
            return Instance(self.name, list(args))
        elif len(args) < len(self.variables):
            return Instance(self.name, list(args) + [None for i in range(len(self.variables)-len(args))])
        else:
            return Instance(self.name, list(args)[:len(self.variables)])

    def __repr__(self):
        functions_copy = {}
        for key in self.functions.keys():
            functions_copy[key] = Function(self.functions[key].funct.replace('"', '\\"'))
        return f"Object(\"{self.name}\", {self.variables}, {functions_copy})"

    def __str__(self):
        return f"{self.name}({', '.join(self.variables)})"

    def API(self):
        api_variables = " -" + ", ".join(self.variables)
        api_functions = "\n".join([f" -{f} = {self.functions[f].funct}" for f in self.functions.keys()])
        return f"{self.name} API:\n" \
               f"Variables:\n" \
               f"{api_variables}\n" \
               f"Functions:\n" \
               f"{api_functions}"


class ObjectFunctionHelper:
    def __init__(self, instance, function):
        self.instance = instance
        self.function = function

    def __call__(self, *args):
        args_string = ", ".join([f"args[{i}]" for i in range(len(args))])
        return eval(f"self.instance.do('{self.function}', {args_string})")

    def __repr__(self):
        return repr(objects[self.instance.object].functions.get(self.function))

    def __str__(self):
        return str(objects[self.instance.object].functions.get(self.function))


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
            return ObjectFunctionHelper(self, item)

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

    def __sub__(self, other):
        if objects[self.object].functions.get("sub") is None:
            return None
        return objects[self.object].functions["sub"](self, other)

    def __mul__(self, other):
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

if os.path.isfile("functions.txt"):
    LoadData(functions, "functions.txt")
if os.path.isfile("variables.txt"):
    LoadData(variables, "variables.txt")


def ParseFunctionParameters(function_text, parameters):
    result_function_text = function_text
    for i in range(len(parameters)):
        j = 0
        while j < len(result_function_text):
            if result_function_text[j:j+len(parameters[i])] == parameters[i] and IsCorrectName(j, parameters[i], result_function_text):
                replacement_text = f"x[{i}]"
                result_function_text = result_function_text[:j] + replacement_text + result_function_text[j+len(parameters[i]):]
                j += len(replacement_text) - len(parameters[i])
            j += 1
    return result_function_text


def IsUniqueName(name, ignore):
    if variables != ignore and name in variables.keys():
        return False
    if functions != ignore and name in functions.keys():
        return False
    if objects != ignore and name in objects.keys():
        return False
    return True


def IsUniqueNameInObject(name, object_name, ignore=None):
    object = objects[object_name]
    if ignore != "variables" and name in object.variables:
        return False
    if ignore != "functions" and name in object.functions.keys():
        return False
    return True


help = "User Manual:\n" \
       " -[expression] = [result]\n" \
       " -var [x] = [y]\n" \
       " -funct [f]([x]) = [y]\n" \
       " -obj [o]([x])\n" \
       " -obj add [o] var [x]\n" \
       " -obj add [o] funct [f]([x]) = [y]\n" \
       " -obj remove [o] var [x]\n" \
       " -obj remove [o] funct [f]\n" \
       " -obj import [o]\n" \
       " -remove [x/f/o]\n" \
       " -variables\n" \
       " -functions\n" \
       " -objects \n" \
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

        elif prompt.startswith("funct "):
            name = prompt[len("funct "):prompt.find("(")].strip()
            if IsValidName(name):
                if IsUniqueName(name, functions):
                    parameters = [x.strip() for x in prompt[prompt.find("(")+1:FindClosingParenthesis(prompt, prompt.find("("))].split(",")]
                    if "" in parameters:
                        parameters.remove("")
                    value = ParseFunctionParameters(prompt[prompt.find("=")+1:].strip(), parameters)
                    functions[name] = Function(value)
                    print(f"Function {name} created with value {value}")
                else:
                    print("Name is already in use")
            else:
                print("Please use a valid name")

        elif prompt.startswith("obj "):
            if prompt.startswith("obj add "):
                if "var " in prompt:
                    name = prompt[len("obj add "):prompt.find("var ")].strip()
                    if IsValidName(name):
                        variable = prompt[prompt.find("var ")+len("var "):].strip()
                        if IsUniqueNameInObject(variable, name):
                            objects[name].variables.append(variable)
                            for v in variables.keys():
                                if type(variables[v]) == Instance and variables[v].object == name:
                                    variables[v].variables.append(None)
                            print(f"Variable {variable} added to object {name}")
                        else:
                            print("Name is already in use")
                    else:
                        print("Object does not exist")

                elif "funct " in prompt:
                    name = prompt[len("obj add "):prompt.find("funct ")].strip()
                    if IsValidName(name):
                        function = prompt[prompt.find("funct ")+len("funct "):prompt.find("(")].strip()
                        if IsUniqueNameInObject(function, name, "functions"):
                            parameters = ["self"]+[x.strip() for x in prompt[prompt.find("(")+1:FindClosingParenthesis(prompt, prompt.find("("))].split(",")]
                            if "" in parameters:
                                parameters.remove("")
                            value = ParseFunctionParameters(prompt[prompt.find("=")+1:].strip(), parameters)
                            objects[name].functions[function] = Function(value)
                            print(f"Function {function} added to object {name} with value {value}")
                        else:
                            print("Name is already in use")
                    else:
                        print("Object does not exist")

                else:
                    print("Only variables or functions can be added to an object")

            elif prompt.startswith("obj remove "):
                if "var " in prompt:
                    name = prompt[len("obj remove "):prompt.find("var ")].strip()
                    variable = prompt[prompt.find("var ") + len("var "):].strip()
                    index = -1
                    for i in range(len(objects[name].variables)):
                        if objects[name].variables[i] == variable:
                            index = i
                            break
                    for v in variables.keys():
                        if type(variables[v]) == Instance and variables[v].object == name:
                            variables[v].variables.pop(index)
                    objects[name].variables.remove(variable)
                    print(f"Variable {variable} removed from object {name}")

                elif "funct " in prompt:
                    name = prompt[len("obj remove "):prompt.find("funct ")].strip()
                    function = prompt[prompt.find("funct ") + len("funct "):].strip()
                    objects[name].functions.pop(function)
                    print(f"Function {function} removed from object {name}")

                else:
                    print("Only variables or functions can be removed from an object")

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
                        objects[name] = Object(name, attributes)
                        print(f"Object {name} created as {str(objects[name])}")
                    else:
                        print("Name is already in use")
                else:
                    print("Please use a valid name")

        elif prompt.startswith("remove "):
            name = prompt[len("remove "):]
            if name in variables.keys():
                variables.pop(name)
                print(f"Variable {name} removed")
            elif name in functions.keys():
                functions.pop(name)
                print(f"Function {name} removed")
            elif name in objects.keys():
                objects.pop(name)
                print(f"Object {name} removed")
            else:
                print("No such thing stored with that name")

        elif prompt == "variables":
            print("Variables:\n" + "\n".join([f" -{v} = {variables[v]}" for v in variables.keys()]))

        elif prompt == "functions":
            print("Functions:\n" + "\n".join([f" -{f} = {functions[f].funct}" for f in functions.keys()]))

        elif prompt == "objects":
            print("Objects:\n" + "\n".join([f" -{o} = {str(objects[o])}" for o in objects.keys()]))

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
            print(f"Result: {str(eval(ParsePrompt(prompt)))}")

    except:
        print("Something went wrong")
