# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 08:37:01 2021

@author: Lkappel
"""

import os
from datetime import date
import shutil

Today = date.today()

# Create the directory
DateFolder = Today.strftime("%Y%m%d")
if (not os.path.isdir(f"{DateFolder} Weekly Report")): os.makedirs(f"{DateFolder} Weekly Report")

DateFile = Today.strftime("%m%d%Y")
#For each file in the template folder
for root, dirs, files in os.walk("YYYYMMDD Weekly Report"):
    for name in files:
        NameCopy = str(name)
        FileSource = os.getcwd() + "\\" + os.path.join(root,name)
        FileDestination = os.getcwd() + f"\\{DateFolder} Weekly Report\\" + NameCopy.replace("MMDDYYYY", DateFile)
        
        # If the destination name does not exist already, make a copy
        if (not os.path.isfile(FileDestination)): shutil.copyfile(FileSource, FileDestination)
    
