#imports
import requests
import time, json
from mediawiki import MediaWiki
import sys
from ast import literal_eval
"""this program gets information about vehicles and dumps it into files for further use"""
wikipedia = MediaWiki()

start_time = time.time()

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
    return "koala"
  try:
   models = page.json()["Results"]
   if models == dict():
     models = None
   return models
  except:
    return "koala"

def Type_Search(vtype,filename):
  print("starting search")
  mans = get_mans(vtype)
  i = 1
  for man in mans:
     man = man.rstrip()
     print("\033[92m New man:",man,"\033[00m")
     results = GetModelsForMakeYear(man,vtype=vtype)
     if results == "koala":
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
         pvariable = False
         if vtype == "Passenger Car" or vtype == "Truck":
            pvariable = True
         print(str(i),"\033[94m"+model+"\033[00m")
         i+=1
         try:
           vehicle_dict[name]
         except:
           type_v=result["VehicleTypeName"]
           try:
             print("getting images")
             wikipage = wikipedia.page(name)
             print(wikipage.title)
             image = wikipage.images[0]
           except:
             print("image not found")
           if pvariable:
             url = "https://www.caranddriver.com/{}/{}".format(str(make).replace(" ","-").lower(),str(model).replace(" ","-").lower())
             if str(requests.get(url)) == "<Response [200]>":
               rurl = url
               print("got review link")
             vehicle_dict[name] = {"type":type_v,"make":make, "model":model,"image": image, "name": name,"review_link":rurl}
           else:
             vehicle_dict[name] = {"type":type_v,"make":make, "model":model,"image": image, "name": name}
           f = open(filename,"w")
           f.write(str(vehicle_dict))
           f.close()
           print("wrote to file")
  return vehicle_dict

print(vtypes := get_vtypes())
print(vtypes)
#to get passenger cars first
vtypes.remove('Incomplete Vehicle')
vehicle_dict = Type_Search("Passenger Car","db/Passenger_Car.db")
sys.exit()

"""
n = 0
a = 0
for vtype in vtypes:
 needs_lower = list()
 vtype = vtype.rstrip()
 filen = str("db/"+vtype+".db").rstrip().replace(" ","_")
 f = open(filen,"r")
 vehicle_dict = literal_eval(f.read())
 f.close()
 for vehicle in vehicle_dict:
   if vehicle.islower():
     pass
   else:
     n += 1
     needs_lower.append(vehicle)
 for vehicle in needs_lower:
    a += 1
    lower_vehicle = vehicle.lower()
    vehicle_dict[lower_vehicle] = vehicle_dict[vehicle]
    del vehicle_dict[vehicle]
    vehicle_dict[lower_vehicle]["name"] = vehicle_dict[lower_vehicle]["name"].lower()
 f = open(filen,"w")
 f.write(str(vehicle_dict))
 f.close()
"""
"""
 vtype = vtype.rstrip()
 filen = str("db/"+vtype+".db").rstrip().replace(" ","_")
 f = open(filen,"r")
 vehicle_dict = literal_eval(f.read())
 f.close()
 print(len(vehicle_dict))
 a = 0
 for vehicle in vehicle_dict:
    if vehicle.islower():
      print(vehicle)
      break
    else:
     lower_vehicle = vehicle.lower()
     vehicle_dict[lower_vehicle] = vehicle_dict[vehicle]
     del vehicle_dict[vehicle]
     vehicle_dict[lower_vehicle]["name"] = vehicle_dict[lower_vehicle]["name"].lower()
     a+=1
 print(a)
 print(len(vehicle_dict))
 f = open(filen,"w")
 f.write(str(vehicle_dict))
 f.close()
"""
for vtype in vtypes:
 vtype = vtype.rstrip()
 filen = str("db/"+vtype+".db").rstrip().replace(" ","_")
 vehicle_dict = Type_Search(vtype,filen)
 #check if image is correct
 idict = dict()
 for v in vehicle_dict:
   if v["image"] != "Not Found" and v["name"] not in v["image"]:
     idict[v["name"]] = {image:v["image"],name:v["name"]}
 for i in idict:
   while True:
     q = input("Is",i["image"],"a photo of",i["make"],i["name"]+"? (y,n)")
     if q.lower().rstrip() == "y":
       break
     elif q.lower().rstrip() == "n":
       vehicle_dict[i["name"]]["image"] = input("Paste in link for image or write Not Found.")
       break
   f=open(filen,"w")
   f.write(str(vehicle_dict))
   f.close()



print("Program took", time.time() - start_time, "to run")