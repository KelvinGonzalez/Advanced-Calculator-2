# Advanced-Calculator-2
Advanced Calculator 2: The Sequel

This calculator supports the ability to create your own variables, functions and objects (equivalent to classes). Variables are used to store data. Functions are used to generate values based on the given arguments. Objects are used to organize entities into their own data type, which can hold their own variables and functions.

To create a variable, use the format: "var [x] = [y]" where [x] is the variable name and [y] its value. Example: "var x1 = 4".

To create a temp variable, use the format: "tempvar [x] = [y]" where [x] is the variable name and [y] its value. Example: "tempvar x2 = 6".

To create a function, use the format: "funct [f]\([x]) = [y]" where [f] is the function name, [x] is its parameters, and [y] is its definition. Example: "funct f1(x, y) = 4*x - y/5".

To create an object, use the format: "obj [o]\([x])" where [o] is the object name and [x] is its variables. Example: "obj Obj1(x, y)".

Objects have a list of commands used to modify an object:

Use "obj add [o]" to add a property to an object. Properties that can be added are: variables ("var"), functions ("funct"), static variables ("staticvar"), and static functions ("staticfunct"). Example: "obj add Obj1 var z", "obj add Obj1 funct f1(other) = self.x + other.y", "obj add Obj1 staticvar a = 2", "obj add Obj1 staticfunct sf1(x) = x + 3".

Use "obj remove [o] [x/f]" to remove a property from an object. Any property can be removed using the same command. Example: "obj remove Obj1 y", "obj remove Obj1 sf1".

Use "obj import [o]" to import a given class from a copied string. To obtain an importable string, do "repr([o])".

Some functions are coded to override python special functions, such as "\_\_add\_\_". To use this feature, create a function with the appropiate name, in this case "add". Example: "obj add Obj1 funct add(other) = Obj1(self.x + other.x, self.y + other.y)". List of overridable functions: str, add, sub, mul, div, mod, pow, cmp, neg, invert, abs, len, getitem, getslice, contains, call.

To remove a variable, function, or object, use the command "remove [x/f/o]". Example: "remove x1", "remove f1", "remove Obj1".

To view all variables, functions, or objects, use the commands "variables", "functions", or "objects" respectively. You can also do "[o].API()" on any object to display all of its properties. Example: "Obj1.API()".

To view your previous results, use the command "results". To reuse previous results in your new prompt, use "ans[i]". Example: "ans[0] + 4".

To save your data use the command "save". To see the user manual again enter "help". To exit the program use "exit", exiting will automatically save your data.
