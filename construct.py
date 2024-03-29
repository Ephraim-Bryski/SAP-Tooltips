import json
from dataclasses import dataclass


f = open("documentation.json")
docs = json.load(f)

f = open("template_class.txt","r")
template_class = f.read()

f = open("template_method.txt","r")
template_method = f.read()

@dataclass
class DefaultArgs:
    full_name: str
    args: dict


# NOTE: default strings need to have nested quotes '"like this"'

all_default_arguments = [
    DefaultArgs("SapObject.SapModel.PointObj.AddCartesian", {"CSys": '"GLOBAL"', "MergeOff": False, "MergeNumber": False}),
    DefaultArgs("SapObject.SapModel.PointObj.SetRestraint", {"ItemType": 0}),
    DefaultArgs("SapObject.SapModel.PointObj.SetLoadForce", {"Replace": True, "CSys": '"GLOBAL"',"ItemType": 0})
]


def parse_method(method_info):


    method_full_name = method_info["full_name"]



    all_layers = method_full_name.split(".")


    base_layer = f"{all_layers[0]}.{all_layers[1]}"
    
    
    if base_layer == "SapObject.SapModel":
        model_layers = all_layers[1:]
    else:

        if base_layer not in unknown_bases:
            print(f"unknown method base: {base_layer}")
            unknown_bases.append(base_layer)

        return [None, None, None]


    method_short_name = model_layers[-1]
    class_short_name = model_layers[-2]
    
    return [model_layers, class_short_name, method_short_name]


classes = {}

unknown_bases = []

for method_info in docs:


    [method_layers, _, method_short_name] = parse_method(method_info)

    if method_layers == None:
        continue

    for i in range(len(method_layers)-1):
        
        class_name = method_layers[i]

        class_names = classes.keys()



        sub_component = method_layers[i+1]

        class_info = {}
        if i+2 == len(method_layers):
            relevant_key = "methods"
            irrelevant_key = "components"
        else:
            relevant_key = "components"
            irrelevant_key = "methods"

        if class_name in class_names:
            class_info = classes[class_name]

            if sub_component not in class_info[relevant_key]:
                class_info[relevant_key].append(sub_component)
        else:
            class_info = {}
            class_info[relevant_key] = [sub_component]
            class_info[irrelevant_key] = []
            classes[class_name] = class_info


def get_method_info(class_name, method_name):

    found = False
    for method_info in docs:

        [method_layers, class_short_name, method_short_name] = parse_method(method_info)

        if class_short_name == None:
            continue

        if class_short_name == class_name and method_short_name == method_name:
            if found:
                print(f"{class_name}.{method_name} appears multiple times")
                return None
            else:
                found = True
                method_info["truncated_name"] = ".".join(method_layers)
                method_info["short_name"] = method_short_name
                method_info_found = method_info

    return method_info_found

def construct_argument_info(arguments):

    info_txt = ""
    for name in arguments:
        about = arguments[name]
        info_txt += f"\n{name}: {about}"
    
    return info_txt

def construct_method(method_info):
    
    method_txt = template_method

    short_name = method_info["short_name"].replace(" ","")

    if not short_name.isidentifier():
        raise Exception("should have been checked")
        print(f"invalid method name: {short_name}")
        return ""

    method_txt = method_txt.replace("SHORT_METHOD",short_name)
    method_txt = method_txt.replace("ABOUT",method_info["about"])
    method_txt = method_txt.replace("FULL_METHOD",method_info["truncated_name"]) # doesn't have SapObject

    arguments = method_info["arguments"]

    def replace_invalid_keys(key):
        if key == "lambda":
            return "Lambda"
        return key

    new_keys = map(replace_invalid_keys,arguments.keys())
    new_values = arguments.values()

    arguments = dict(zip(new_keys, new_values))


    boop = list(filter(lambda x:(x.full_name == method_info["full_name"]), all_default_arguments))

    assert len(boop)<=1

    if len(boop) == 1:

        default_arguments = boop[0].args

    else:
        default_arguments = {}



    argument_names = arguments.keys()

    full_argument_names = ["self"]



    for argument in argument_names:
        if not argument.isidentifier():
            raise Exception("should have been checked")
            print(f"invalid argument name: {argument}")
            return None
        

        if argument in default_arguments:
            full_argument_names.append(f"{argument} = {default_arguments[argument]}")
        else:
            full_argument_names.append(f"{argument} = None")


    method_txt = method_txt.replace("SHORT_ARGUMENTS",", ".join(argument_names))
    method_txt = method_txt.replace("FULL_ARGUMENTS",", ".join(full_argument_names)) # just has self too

    method_txt = method_txt.replace("ARGUMENT_INFO",construct_argument_info(arguments))

    return method_txt

def construct_class(class_name, components, methods_names):
    
    if not class_name.isidentifier():
        raise Exception("should have been checked")
        print(f"invalid class name: {class_name}")
        return ""
    
    class_txt = template_class

    sp = " "

    component_txt = ""
    for component in components:
        component_txt += f"{sp*8}self.{component} = {component}(strict, api)\n"

    methods_txt = ""
    for method_name in methods_names:
        method_info = get_method_info(class_name, method_name)
        if method_info == None:
            continue
        methods_txt += construct_method(method_info)

    class_txt = class_txt.replace("CLASS",class_name)
    class_txt = class_txt.replace("COMPONENTS",component_txt)
    class_txt = class_txt.replace("METHODS",methods_txt)

    return class_txt


wrapper_txt = "" # TODO need to get the initial base function



for class_name in classes:
    class_info = classes[class_name]

    class_txt = construct_class(class_name, class_info["components"],class_info["methods"])
    
    wrapper_txt += class_txt


def fix_typos(method_layers):

    corrections = {
        "SapMdel": "SapModel",
        "SapMoel": "SapModel"
    }
        

    for i in range(len(method_layers)):
        layer = method_layers[i]
        if layer in corrections.keys():
            method_layers[i] = corrections[layer]
    


with open("base_class.txt") as f:
    base_txt = f.read()

full_text = f"{base_txt}\n\n{wrapper_txt}"

with open("new_tooltips.py","w",encoding="utf8") as f:
    f.write(full_text)