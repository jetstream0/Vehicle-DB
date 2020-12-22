#imports
import requests
import time, json
import sys
from ast import literal_eval
"""this program gets information about vehicles and dumps it into files for further use, made by github.com/jetstream0"""

base_url = "https://vpic.nhtsa.dot.gov/api/vehicles"

def get_vtypes():
  print('getting vehicle types')
  page = requests.get(base_url+"/getvehiclevariablevalueslist/Vehicle%20Type?format=json")
  vtypesdict = page.json()["Results"]
  vtypes = list()
  for element in vtypesdict:
    vtypes.append(element["Name"])
  return vtypes

def get_mans(vtype):
   print("getting manufacturers for",vtype)
   mans = list()
   page = requests.get(base_url+"/GetMakesForVehicleType/{}?format=json".format(vtype))
   mansdict = page.json()["Results"]
   for element in mansdict:
     mans.append(element["MakeName"])
   return mans

def GetModelsForMakeYear(make,vtype):
  print("getting models for vtype")
  page = requests.get(base_url+"/GetModelsForMakeYear/make/{}/vehicletype/{}?format=json".format(make,vtype))
  if str(page) != "<Response [200]>":
    return "placeholderkoala"
  try:
   models = page.json()["Results"]
   if models == dict():
     models = None
   return models
  except:
    return "placeholderkoala"

def Type_Search(vtype,filename):
  print("starting search")
  mans = get_mans(vtype)
  i = 1
  for man in mans:
     man = man.rstrip()
     print("\033[92m New man:",man,"\033[00m")
     results = GetModelsForMakeYear(man,vtype=vtype)
     if results == "placeholderkoala":
       continue
     print("sorting through results")
     if results != None:
       for result in results:
         try:
           f = open(filename,"r")
         except:
           f=open(filename,"w")
           f.close()
           f = open(filename,"r")
         try:
           vehicle_dict = literal_eval(f.read())
         except SyntaxError:
           vehicle_dict = {}
         f.close()
         image = "Not Found"
         rurl = "Not Found"
         make = result["Make_Name"]
         model = result["Model_Name"]
         make = make.rstrip()
         model = model.rstrip()
         name = make+" "+model
         name = name.lower()
         print(str(i),"\033[94m"+model+"\033[00m")
         i+=1
         try:
           #check to see if vehicle is already there
           vehicle_dict[name]
         except:
           type_v=result["VehicleTypeName"]
           vehicle_dict[name] = {"type":type_v,"make":make, "model":model,"name": name}
           f = open(filename,"w")
           f.write(str(vehicle_dict))
           f.close()
           print("wrote to file")
  return vehicle_dict

print(vtypes := get_vtypes())

for vtype in vtypes:
 vtype = vtype.rstrip()
 filen = str("db/"+vtype+".db").rstrip().replace(" ","_")
 #complete dictionary of vehicles from type, do whatever you want with it, but is already safely written to file
 vehicle_dict = Type_Search(vtype,filen)
