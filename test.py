from DataStore import *
from DataStoreExceptions import *
from largeSize import largeJson
import unittest
import os
import json

class DataStoreTest(unittest.TestCase):

    def test_initialize_Obj(self):
        self.datastoreobj = DataStore()                                                     # current working directory is chosen as path if not specified
        self.assertIsInstance(self.datastoreobj,DataStore)                                  # Instance creation wihtout path specified

        with self.assertRaises(IOErrorOccurred):
            self.datastore_obj = DataStore(os.getcwd())                                     # Instance creation of path with elevated priviledges
    

    def test_create(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        createSuccess = self.datastoreobj.create('color','{"color": "red"}','0')           # Instance creation using Create API with optional timeToLive property
        self.assertTrue(createSuccess)
        createSuccess = self.datastoreobj.create('bicycle','{"color": "black"}')           # Instance creation using Create API without timeToLive property
        self.assertTrue(createSuccess)

        with self.assertRaises(KeyLengthExceeded):
            self.datastoreobj.create('abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz','{"color": "red","value": "#f00"}')  # Create API invoked with string of length greater than 32 raises Exception
        with self.assertRaises(InvalidKey):
            self.datastoreobj.create(12,'{"color": "red"}')                                # Create API invoked with non string type
        with self.assertRaises(InvalidJSONobject):
            self.datastoreobj.create('valid','{color: "red"}')                             # Create API invoked with invalid json object
        with self.assertRaises(timeToLiveValueError):
            self.datastoreobj.create('valid','{"color": "red"}','TEN')                     # Create API invoked with invalid type of timeToLive property
        with self.assertRaises(InvalidJSONobject):
            self.datastoreobj.create('valid','[{color:#f00}]')                             # Create API invoked with invalid json object
        with self.assertRaises(DuplicateKey):
            self.datastoreobj.create('color','{"color": "blue"}','1000')                   # Create API invoked for existing key
            
        

    def test_read(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        createSuccess = self.datastoreobj.create('car','{"color": "silver"}','1000')              
        self.assertTrue(createSuccess)
        readSuccess = self.datastoreobj.read('car')                                        # Read API invoked with non expired key
        self.assertTrue(readSuccess)
        self.assertTrue(self.datastoreobj.read('bicycle'))                                 # Read API invoked with no timeToLive property

        with self.assertRaises(KeyLengthExceeded):
            self.datastoreobj.read('abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz') # Read API invoked with string of length greater than 32 raises Exception
        with self.assertRaises(InvalidKey):
            self.datastoreobj.read(12)                                                     # Read API invoked with non string type
        with self.assertRaises(KeyNotExist):
            self.datastoreobj.read('truck')                                                # Read API invoked for non existing key object
        with self.assertRaises(KeyExpired): 
            self.datastoreobj.read('color')                                                # Read API invoked for expired time to live property key


    def test_delete(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        createSuccess = self.datastoreobj.create('bus','{"color": "yellow"}','5000')
        self.assertTrue(createSuccess)
        create_Success = self.datastoreobj.create('ship','{"color":"blue"}')
        self.assertTrue(create_Success)
        
        self.assertIsNone(self.datastoreobj.delete('bus'))                                  # Delete API invoked with non expired key
        self.assertIsNone(self.datastoreobj.delete('ship'))                                 # Delete API invoked with no timeToLive property
        
        with self.assertRaises(KeyLengthExceeded):
            self.datastoreobj.delete('abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz') # Delete API invoked with string of length greater than 32 raises Exception
        with self.assertRaises(InvalidKey):
            self.datastoreobj.delete(12)                                                    # Delete API invoked with non string type
        with self.assertRaises(KeyNotExist):
            self.datastoreobj.delete('truck')                                               # Delete API invoked for non existing key object
        with self.assertRaises(KeyExpired):
            self.datastoreobj.delete('color')                                               # Delete API invoked for expired time to live property key


    def test_time_to_live(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        self.assertTrue(self.datastoreobj.create('bus','{"color": "yellow"}','5000'))      # Create API with timeToLive as string parameter
        self.assertTrue(self.datastoreobj.create('plane','{"color": "white"}',5_000))      # Create API with timeToLive as integer parameter

        with self.assertRaises(timeToLiveValueError):
            self.datastoreobj.create('bus','{"color": "yellow"}','ONE')                    # Create API with timeToLive as non int type parameter

        with self.assertRaises(KeyExpired):
            self.datastoreobj.read('color')                                                # Read API with timeToLive expired

        with self.assertRaises(KeyExpired):
            self.datastoreobj.delete('color')                                              # Delete API with timeToLive expired
        

    def test_json_size(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        with self.assertRaises(ValueSizeExceeded):
            self.datastoreobj.create('sample',largeJson().getJson(),'1000')                # file of size 20KB


    def test_time_to_live_is_alive(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        self.assertTrue(self.datastoreobj.read('bus'))                                     # Read API to check the availabilty of key with timeToLive parameter
        self.assertTrue(self.datastoreobj.read('plane'))
        self.assertTrue(self.datastoreobj.read('car'))  
        self.assertIsNone(self.datastoreobj.delete('bus'))                                 # Delete API to check the availabilty of key with timeToLive parameter
        self.assertIsNone(self.datastoreobj.delete('plane'))
        self.assertIsNone(self.datastoreobj.delete('car'))
        os.remove(self.datastoreobj.optional_file_path)            

    
if __name__ == '__main__':
    unittest.main()