# -- coding utf-8 --

Created on Tue Mar 22 154452 2022
@author lkapp


import sqlite3, re, copy
from datetime import datetime

class SQL_Database
    
    #### Class parameters ####################################################
    
    SQL_Connection = None
    
    #### Class __ methods ####################################################
    
    def __init__(self, SQL_URL)
        try
            self.SQL_Connection = sqlite3.connect(SQL_URL)
        except BaseException as err
            print(fUnexpected {err=}, {type(err)=})
        
    def __del__(self)
        try
            self.SQL_Connection.close()
        except BaseException as err
            print(fUnexpected {err=}, {type(err)=})
            
    def __commit__(self)
        try
            self.SQL_Connection.commit()
        except BaseException as err
            print(fUnexpected {err=}, {type(err)=})
    
    #### Class methods #######################################################
    
    def dbExecute(self, SQL_Command, SQL_Parameters = (), debug = False)
        '''Executes a generic query on the database connection, returning any results.'''
        if debug
            print(f'{SQL_Command}n{SQL_Parameters}')
        SQL_Cursor = self.SQL_Connection.cursor()
        Query_Results = SQL_Cursor.execute(SQL_Command, SQL_Parameters).fetchall()
        SQL_Cursor.close()
        self.__commit__()
        return Query_Results
    
    def dbGetTableList(self) 
        '''Returns a list of ALL the table definitions in the database connection.'''
        
        TableList = []
        for Table in self.dbExecute(rSELECT  FROM sqlite_master WHERE type='table';)
            if Table[1] == 'sqlite_sequence' continue
            TableList.append(Table)
        return TableList
    
    def dbGetTableNameList(self)
        '''Retrieve a list of all the table names from the database connection.'''
        return [Table[1] for Table in self.dbGetTableList()]
    
    def dbTableExists(self, Table_Name)
        '''Returns 1 if a table with Table_Name exists in the database connection.'''
        Return_Value = 0
        if Table_Name in self.dbGetTableNameList() 
            Return_Value = 1
        return Return_Value
    
    def dbTableCreate(self, Table_Name, Column_Definitions=())
        '''Create a table with name Table_Name.
        Optional Column_Definitions as per SQL_Database.dbTableAddColumn(self, Table_Name, Column_Definition)'''
        self.dbExecute(f'CREATE TABLE IF NOT EXISTS {Table_Name};')
        if len(Column_Definitions)  0
            for Definition in Column_Definitions
                self.dbTableAddColumn(Table_Name, Definition)
        return
    
    def dbTableDrop(self, Table_Name)
        '''Remove a table from the database'''
        return self.dbExecute(f'DROP TABLE {Table_Name};')
    
    def dbGetTableDefinition(self, Table_Name)
        '''Returns the full table definition of the table in the database connection matching the Table_Name input.'''
        for Table in self.dbGetTableList()
            if Table[1] == Table_Name return Table
        raise Exception(f'Table {Table_Name} not found in the database connection.')
    
    def dbGetTableColumnDefinition(self, Table_Name)
        '''Get the column definitions of Table_Name.
        
        Returns a tuple of tuples which contain, in order, 
            (Column_Name, Column_Type, Attribute_1, Attribute_2...Attribute_N)
            
        Where Attributes are things like PRIMARY KEY, UNIQUE, CHECK, etc.'''
        Table_Definition = self.dbGetTableDefinition(Table_Name)[-1]
        Regex_Results = re.compile(r'((.))', re.DOTALL).search(Table_Definition).group(1)
        Regex_Results = Regex_Results.replace('n', ' ').strip().split(', ')
        Column_Definition = [Column_Definition.split(' ') for Column_Definition in Regex_Results]
        
        for Definition in Column_Definition
            if 'PRIMARY' in Definition and 'KEY' in Definition
                Primary_Key_Index = Definition.index('PRIMARY')
                Definition[Primary_Key_Index] = 'PRIMARY KEY'
                Definition.pop(Primary_Key_Index + 1)
        return tuple([tuple(Column) for Column in Column_Definition])
        
    def dbGetTableColumnNames(self, Table_Name)
        return [Column[0] for Column in self.dbGetTableColumnDefinition(Table_Name)]
            
    def dbTableAddColumn(self, Table_Name, Column_Definition)
        '''Add the column defined by Column_Definition to Table_Name.
        
        Column_Definition takes the format
            (Column_Name, Column_Type, Attribute_1, Attribute_2...Attribute_N)
            
        Where Attributes are things like PRIMARY KEY, UNIQUE, CHECK, etc.'''
        
        # Check first if the column exists within the table already.
        if Table_Name in self.dbGetTableColumnNames(Table_Name)
            raise Exception(f'Column {Column_Definition[0]} already exists in table {Table_Name}')
    
        return self.dbExecute(f'ALTER TABLE {Table_Name} ADD COLUMN { .join(Column_Definition)};')
    
    def dbTableDropColumn(self, Table_Name, Column_Name)
        return self.dbExecute(f'ALTER TABLE {Table_Name} DROP COLUMN {Column_Name};')
    
    def dbGetTableRecords(self, Table_Name, Columns = (), Parameters=())
        '''Collect records from Table_Name whose parameters match Parameters.
        
        Columns is a one dimensional tuple of the column names to be collected.
        Do not define Columns if all columns are desired (SELECT )
        
        Parameters is a two dimensional tuple, where its elements are tuple pairs that define the constraints to filter the search by (AND).
            (
                ('Header_Name_1', 'Header_Value_1'),
                ('Header_Name_2', 'Header_Value_2'),
                .
                .
                .
                ('Header_Name_N', 'Header_Value_N')
            )
            Do not define Parameters if all records are desired.'''
        
        Column_Collation = ''
        if len(Columns)  0 
            Column_Collation = ' , '.join(Columns)
        
        Parameter_Collation = ''
        Parameter_List = ()
        if len(Parameters)  0
            Parameter_Collation = f WHERE {' AND '.join([f'{Param[0]}=' for Param in Parameters])}
            Parameter_List = tuple([Param[1] for Param in Parameters])
            
        return self.dbExecute(f'SELECT {Column_Collation} FROM {Table_Name}{Parameter_Collation};', Parameter_List)
    
    def dbRecordDelete(self, Table_Name, Record_Definition)
        '''Deletes records which match all the given parameters of Record_Definition.
        Record definition format is
            (
                (Column_1, Value_1),
                (Column_2, Value_2),
                ...
                (Column_N, Value_N)
            )
        '''
        SQL_Command_sub = ' AND '.join([f'{record[0]}=' for record in Record_Definition])
        SQL_Command = fDELETE FROM {Table_Name} WHERE {SQL_Command_sub}
        
        return self.dbExecute(SQL_Command, tuple([record [1] for record in Record_Definition]))
    
    def dbRecordInsert(self, Table_Name, Record_Definition, Replace_Existing = False)
        '''Inserts a record into the table whose values are defined by Record_Definition
        Record definition format is
            (
                (Column_1, Value_1),
                (Column_2, Value_2),
                ...
                (Column_N, Value_N)
            )
        '''
        SQL_Command_Sub1 = ' , '.join([Record[0] for Record in Record_Definition])
        SQL_Command_Sub2 = ' , '.join(['' for Record in Record_Definition])
        SQL_Command_Sub3 = ''
        if Replace_Existing
            SQL_Command_Sub3 = ' OR REPLACE'
            
        SQL_Command = fINSERT{SQL_Command_Sub3} INTO {Table_Name} 
            ({SQL_Command_Sub1}) 
            VALUES({SQL_Command_Sub2});
            
        return self.dbExecute(SQL_Command, tuple([Record[1] for Record in Record_Definition]))
    
    def dbRecordUpdate(self, Table_Name, Record_Definition_Location, Record_Definition_Update)
        '''Inserts a record into the table whose values are defined by Record_Definition
        Record_Definition_Location defines the parameters (AND join) by which to identify which records are to be updated.
        Record_Definition_Update defines the actual values to be changed.
        Record definition format is
            (
                (Column_1, Value_1),
                (Column_2, Value_2),
                ...
                (Column_N, Value_N)
            )
        '''
        
        SQL_Command_Locate = ' AND '.join([f'{Record[0]}=' for Record in Record_Definition_Location])
        SQL_Command_Update = ' , '.join([f'{Record[0]}=' for Record in Record_Definition_Update])
        SQL_Command = f'''UPDATE {Table_Name} SET {SQL_Command_Update} WHERE {SQL_Command_Locate}'''
        
        Joined_Record_Values = [Record[1] for Record in Record_Definition_Update] + [Record[1] for Record in Record_Definition_Location]
        return self.dbExecute(SQL_Command, tuple(Joined_Record_Values))
    
######## End of Class SQL_Database ###########################################

######## Utility Stuff #######################################################

def compareListContents(list1,list2)
    '''Compare to see if two lists have all the same contents, regardless of elements' order.'''
    #create list to remember the removed elements.
    compareList = []
    list2_copy = copy.deepcopy(list2)
    
    for elem in list1
        # if elem is in list2, remove it and put it in comparelist
        if elem in list2_copy
            compareList.append(list2_copy.pop(list2_copy.index(elem)))
            
    # if the two lists had the same contents, then compareList should be exactly
    # the same as list1, and there should be no elements left in list2.
    return (list1 == compareList) and len(list2_copy) == 0

def writeDebugLog(DebugText, filepath = '')
    Timestamp = datetime.now()
    if filepath == ''
        filepath = Timestamp.strftime('%Y%m%d%H%M%S_Debug.txt')
    with open(filepath, 'w+') as debugfile
        debugfile.write(f'{Timestamp.strftime(%Y.%m.%d)}n{Timestamp.strftime(%H%M%S)}nn{DebugText}')
    return
    

######## End Utility Stuff ###################################################

db = SQL_Database(r'CUserslkappDesktopIKOCatalogue_release.db')
print(db.dbRecordDelete('MXC', (('id', 'MXC 15'),)))
print(db.dbGetTableRecords('MXC', ('wah','id','l3'), (('id', 'MXC 15'),)))
print(db.dbRecordInsert('MXC', (('id', 'MXC 15'),)))
print(db.dbGetTableRecords('MXC', ('wah','id','l3'), (('id', 'MXC 15'),)))
writeDebugLog(Hello, World!)