from DataStore import *
from DataStoreExceptions import *
from largeSize import largeJson
import unittest
import os
import json

class DataStoreTest(unittest.TestCase):

    def test_initialize_Obj(self):
        self.datastoreobj = DataStore()
        self.assertIsInstance(self.datastoreobj,DataStore)

        with self.assertRaises(IOErrorOccurred):
            self.datastore_obj = DataStore(os.getcwd())
    

    def test_create(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        createSuccess = self.datastoreobj.create('color','{"color": "red"}','0')
        self.assertTrue(createSuccess)
        createSuccess = self.datastoreobj.create('bicycle','{"color": "black"}')
        self.assertTrue(createSuccess)

        with self.assertRaises(KeyLengthExceeded):
            self.datastoreobj.create('abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz','{"color": "red","value": "#f00"}')
        with self.assertRaises(InvalidKey):
            self.datastoreobj.create(12,'{"color": "red"}')
        with self.assertRaises(InvalidJSONobject):
            self.datastoreobj.create('valid','{color: "red"}')
        with self.assertRaises(timeToLiveValueError):
            self.datastoreobj.create('valid','{"color": "red"}','TEN')
        with self.assertRaises(InvalidJSONobject):
            self.datastoreobj.create('valid','[{color:#f00}]')
        with self.assertRaises(DuplicateKey):
            self.datastoreobj.create('color','{"color": "blue"}','1000')
            
        

    def test_read(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        createSuccess = self.datastoreobj.create('car','{"color": "silver"}','1000')
        self.assertTrue(createSuccess)
        readSuccess = self.datastoreobj.read('car')
        self.assertTrue(readSuccess)
        self.assertTrue(self.datastoreobj.read('bicycle'))

        with self.assertRaises(KeyLengthExceeded):
            self.datastoreobj.read('abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz')
        with self.assertRaises(InvalidKey):
            self.datastoreobj.read(12)
        with self.assertRaises(KeyNotExist):
            self.datastoreobj.read('truck')
        with self.assertRaises(KeyExpired):
            self.datastoreobj.read('color')


    def test_delete(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        createSuccess = self.datastoreobj.create('bus','{"color": "yellow"}','5000')
        self.assertTrue(createSuccess)
        create_Success = self.datastoreobj.create('ship','{"color":"blue"}')
        self.assertTrue(create_Success)
        
        self.assertIsNone(self.datastoreobj.delete('bus'))        
        self.assertIsNone(self.datastoreobj.delete('ship'))
        
        with self.assertRaises(KeyLengthExceeded):
            self.datastoreobj.delete('abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz')
        with self.assertRaises(InvalidKey):
            self.datastoreobj.delete(12)
        with self.assertRaises(KeyNotExist):
            self.datastoreobj.delete('truck')
        with self.assertRaises(KeyExpired):
            self.datastoreobj.delete('color')


    def test_time_to_live(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        self.assertTrue(self.datastoreobj.create('bus','{"color": "yellow"}','5000'))
        self.assertTrue(self.datastoreobj.create('plane','{"color": "white"}',5_000))

        with self.assertRaises(timeToLiveValueError):
            self.datastoreobj.create('bus','{"color": "yellow"}','ONE')

        with self.assertRaises(KeyExpired):
            self.datastoreobj.read('color') 

        with self.assertRaises(KeyExpired):
            self.datastoreobj.delete('color')
        

    def test_json_size(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        with self.assertRaises(ValueSizeExceeded):
            self.datastoreobj.create('sample',largeJson().getJson(),'1000')              # file of size 20KB


    def test_time_to_live_is_alive(self):
        success = self.datastoreobj = DataStore()
        self.assertTrue(success)

        self.assertTrue(self.datastoreobj.read('bus'))
        self.assertTrue(self.datastoreobj.read('plane'))
        self.assertTrue(self.datastoreobj.read('car'))
        self.assertIsNone(self.datastoreobj.delete('bus'))
        self.assertIsNone(self.datastoreobj.delete('plane'))
        self.assertIsNone(self.datastoreobj.delete('car'))
        os.remove(self.datastoreobj.optional_file_path)            

    
if __name__ == '__main__':
    unittest.main()