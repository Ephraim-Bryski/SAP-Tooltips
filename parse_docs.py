from bs4 import BeautifulSoup
import json

def get_parameter_info(div_group):

    parameter_names = []
    parameter_info = []

    info = []

    for div in div_group:

        div_txt = div.get_text().replace("\xa0","")

        if div_txt in ["None","None.","None "]:
            return {}
        
        is_name = div.has_attr("class") and div["class"][0].lower() == "parametername" # some are lower case
        is_blank = len(div_txt) == 0
        if is_name and not is_blank: 
            parameter_names.append(div_txt)
            if len(info)!=0:
                parameter_info.append("\n".join(info))
                info = []
        else:
            info.append(div_txt)
    parameter_info.append("\n".join(info)) # TODO redundant

    if len(parameter_info) != len(parameter_names):
        print(f"parameter mismatch")
        return None

    inserted_names = []
    inserted_info = []
    
    
    flat_parameter_names = []
    flat_parameter_info = []

    for parameter in zip(parameter_names, parameter_info):
        [name, info] = parameter

        name = name.replace(" ","")

        subnames = name.split(",")
        

        for subname in subnames:
            flat_parameter_names.append(subname)
            flat_parameter_info.append(info)
        

            
    parameter_names = flat_parameter_names
    parameter_info = flat_parameter_info

    for i in range(len(parameter_names)):
        name = parameter_names[i].replace(" ","")
        if not name.isidentifier():
            return None
        info = parameter_info[i]

        split_names = name.split(",")

        if len(split_names) > 1:
            pass

        for split_name in split_names:
            inserted_names.append(split_name)
            inserted_info.append(info)

    def flatten(arr):
        return arr
        # CHATGPT CODE
        flattened = []
        for item in arr:
            if isinstance(item, list):
                flattened.extend(flatten(item))
            else:
                flattened.append(item)
        return flattened


        #raise Exception("parameter mismatch")

    parameter_names = flatten(inserted_names)
    parameter_info = flatten(inserted_info)

    return dict(zip(parameter_names, parameter_info))


def get_method_info(file_name):

    if file_name != desired_path:
        pass
        # return

    if ".htm" not in file_name:
        return None
    f = open(file_name)
    example = f.read()
    html = BeautifulSoup(example)
    divs = html.findAll()

    group = []
    prev_div = None
    method = None
    description = None

    arguments = None
    
    for div in divs:
        type = div.name
        if type == "p":
            group.append(div)
        elif type == "h2":           
            if prev_div == None:
                header = None
            else:
                header = prev_div.get_text()
            if  header == "Syntax":
                method = group[0].get_text()
            elif header == "Parameters":
                arguments = get_parameter_info(group)
            elif header == "Remarks":
                group_txt = [div.get_text() for div in group]
                description = "\n".join(group_txt)
            group = []
            prev_div = div

    if method == None:
        return None
    
    success = True

    if description == None:
        description = ""
        success = False
    
    if arguments == None:
        arguments = {}
        description += "\n Failed to parse arguments, start with '.api.' to call method"
        success = False



    method_parts = method.split(".")
    for part in method_parts:
        if not part.isidentifier():
            return None

    method_data = {
        "full_name": method,
        "file":file_name, # just used for reference
        "about": description,
        "arguments":arguments,
        "fully_parsed": success
    }
    return method_data

desired_path = "CSI_OAPI_Documentation\\SAP2000_API_Fuctions\\Edit\\Edit_Point\\ChangeCoordinates_1_{Point}.htm"

def get_docs():

    import os


    docs = []
    base_path = "CSI_OAPI_Documentation\SAP2000_API_Fuctions"
    def search_down_dir(path):    

        contents = os.listdir(path)
        files = []
        folders = []
        for content in contents:
            
            if "." not in content:
                folders.append(content)
                continue

            full_name = f"{path}\\{content}"
            method_info = get_method_info(full_name)


            if method_info == None:
                cant_parse_files.append(full_name)
                continue
            else:
                files.append(method_info)

            if not method_info["fully_parsed"]: 
                cant_parse_arguments_files.append(full_name)

        for folder in folders:
            search_down_dir(path+"\\"+folder)

        methods = files

        for method in methods:
            docs.append(method)
        


    search_down_dir(base_path)

    return docs



cant_parse_files = []
cant_parse_arguments_files = []

docs = get_docs()

json_object = json.dumps(docs, indent=4)
 
with open("documentation.json", "w") as outfile:
    outfile.write(json_object)

with open("cant_parse.txt","w") as outfile:
    outfile.write("\n".join(cant_parse_files))

with open("cant_parse_arguments.txt","w") as outfile:
    outfile.write("\n".join(cant_parse_arguments_files))




