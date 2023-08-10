from constructed import Sap2000, SapObject

class sap:
    def __init__(self):
        # set up api hooks and everything
        api = "API GOES HERE"
        
        self.api = api
        self.Sap2000 = Sap2000(api) # some analyze methods and some other methods use this instead of the sapobject
        self.SapObject = SapObject(api)

        