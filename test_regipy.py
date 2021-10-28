from Registry import Registry

reg = Registry.Registry('C:\\Users\\Mankar\\django-env\\skyev\\evidencia\\52-183\\52-183\\Registry\\Hive\\SAM')

def rec(key, depth=0):
    print ("\t" * depth + key.path())

    for subkey in key.subkeys():
        rec(subkey, depth + 1)

rec(reg.root())

try:
    key = reg.open("SAM\\Domains\\Account\\Users\\Names")
except Registry.RegistryKeyNotFoundException:
    print ("Couldn't find Run key. Exiting...")
    sys.exit(-1)
    
for subkey in key.subkeys():
    print (subkey.name())
    for value in [v for v in subkey.values()]:
        print (value.name())
    