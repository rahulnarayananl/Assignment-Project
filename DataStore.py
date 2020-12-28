import json
import os
from time import sleep , time
from threading import Lock
from DataStoreExceptions import *

MAX_FILE_SIZE = 1024*1024*1024  # 1GB memory size
MAX_VALUE_SIZE_IN_KB = 16*1024 

class DataStore:
    """
    DataStore class represting the key-value datastore
    """
    def __init__(self, optional_file_path = None):
        """
        Initialize the DataStore
        Optional_file_path should lead to a .json file
        :param optional_file_path: str 
        :return: None
        """
        self.optional_file_path = optional_file_path
        self.lock = Lock()
        
        if self.optional_file_path:
            if not os.access(self.optional_file_path, os.F_OK) : raise FileNotFound
            elif not os.access(self.optional_file_path, os.R_OK) : raise FileNotAccessible

            try: 
                with open(self.optional_file_path): 
                    pass    
            except IOError: raise IOErrorOccurred    
        else:
            self.optional_file_path = os.getcwd() + '\\data_store.json'      # current working directory is chosen as default file path 
        
        with open(self.optional_file_path,'a+') :
            pass                                                            # creates a JSON file if path is None or appends the exisiting file                  

        self.file_size = os.stat(self.optional_file_path).st_size

    def checkKey(self,key):
        """
        Function to check the validity of key
        Raises InvalidKey and KeyLengthExceeded if fail
        :return: None
        """                                              
        self.key = key
        if type(self.key) is not str:                                       # Check if Key is not string 
            raise InvalidKey 
        if len(self.key) > 32 :                                             # Check if Key is exceeding 32 Chars
            raise KeyLengthExceeded
    

    def create(self,key:str,value,timeToLive = None):
        """
        API to create DataStore of key - value pairs
        :param key: str
        :param value : JSON object
        :param timeToValue: int
        :return: bool
        """
        self.key = key
        self.value  = value
        self.timeToLive = timeToLive 
        self.timeCreated = None
        self.file_size = os.stat(self.optional_file_path).st_size 
        self.checkKey(self.key)                                              # Key is validated
        
        try:
            json.loads(self.value)
        except json.JSONDecodeError:
            raise InvalidJSONobject

        with self.lock:                                                      # locks the client process and provide thread safe
            self.json_value_size = self.value.__sizeof__()                   # get size of json Object value

            if self.json_value_size > MAX_VALUE_SIZE_IN_KB :
                raise ValueSizeExceeded
            if self.file_size > MAX_FILE_SIZE :
                raise FileSizeExceeded
            
            if self.timeToLive:
                try: 
                    self.timeToLive = int(self.timeToLive)
                    self.timeCreated = int(time())
                except: 
                    raise timeToLiveValueError
            

            with open(self.optional_file_path,'r+') as self.datastorefile:

                self.data = {self.key : (self.value, self.timeToLive,self.timeCreated)}              # data is python object, dict() and Key has a tuple value          
                if self.file_size == 0 :
                    self.datastorefile.write(json.dumps(self.data))                                  # Serialize python object to a JSON formatted string and added to dataStore file
                    return True
                else:
                    try : self.data_store = json.load(self.datastorefile)                            # Deserialize JSON file to a Python object, dict ()
                    except json.JSONDecodeError:  raise InvalidJSONfile                                
                    
                    if self.key in self.data_store : raise DuplicateKey(self.key)                    # Check if Key already exists
                    else:
                        try : self.data_store.update(self.data)                                      # data added to data_store object containing all data from json file
                        except AttributeError : raise InvalidJSONfile                                # throws exception if json file contains json array, valid json file requires to be a json object
                                
                        self.datastorefile.seek(0)                                                   # to reset the file pointer to position 0 
                        json.dump(self.data_store, self.datastorefile)
                        return True



    def read(self, key:str):
        """
        API to read key of a DataStore
        :param key: str
        :return: JSON Object
        """
        self.key = key
        self.file_size = os.stat(self.optional_file_path).st_size
        self.checkKey(self.key)

        with open(self.optional_file_path,'r') as self.datastorefile:
            if self.file_size == 0:                                                                  # handles Empty file
                raise EmptyFile 
            else:
                    try : self.data_store = json.load(self.datastorefile)                            # deserialize JSON file to a Python object, dict ()
                    except json.JSONDecodeError:  raise InvalidJSONfile                                
                    
                    if self.key in self.data_store :
                        self.data = self.data_store[self.key]
                        if self.data[1] == None:                                                     # time-to-Live value is not provided
                            return json.dumps(self.data[0])
                        else:
                            self.time  = int(time()) - self.data[2]                                  # current time - created time 
                            if self.time < self.data[1]:                                             # check if difference between current time and time of creation is less than time-to-Live value   
                                return json.dumps(self.data[0])
                            else:
                                raise KeyExpired(self.key)
                    else:
                        raise KeyNotExist(self.key)
    

    def delete(self, key:str):
        """
        API to delete a key from a DataStore
        :param key: str
        :return: None
        """
        self.key = key
        self.file_size = os.stat(self.optional_file_path).st_size
        self.checkKey(self.key)

        with open(self.optional_file_path,'r') as self.datastorefile:
            if self.file_size == 0:
                raise EmptyFile                                                                       # handles Empty file
            else:
                    try : self.data_store = json.load(self.datastorefile)                        
                    except json.JSONDecodeError:  raise InvalidJSONfile                                
                    
                    if self.key in self.data_store :
                        self.data = self.data_store[self.key]
                        if self.data[1] == None:
                            del self.data_store[self.key]
                            self.datastorefile.close()                                            # closed the file object
                            os.remove(self.optional_file_path)
                        else:
                            self.time  = int(time()) - self.data[2]  
                            if self.time < self.data[1]:                                             # check if difference between current time and time of creation is less than time-to-Live value 
                                del self.data_store[self.key]
                                self.datastorefile.close()                                            # closed the file object
                                os.remove(self.optional_file_path)                                    # delete the current file and recreate with updated data
                            else:
                                raise KeyExpired(self.key)
                    else:
                        raise KeyNotExist(self.key)
                
                    with open(self.optional_file_path, 'w') as self._datastorefile:
                        json.dump(self.data_store,self._datastorefile)

