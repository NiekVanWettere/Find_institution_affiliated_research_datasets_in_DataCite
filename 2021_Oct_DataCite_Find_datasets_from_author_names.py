# -*- coding: utf-8 -*-
"""
Created on Fri Sep  3 11:33:03 2021

@author: nvwetter
"""

#---------------------------------------------------------------------------------------------------------------------------------------------
# import libraries

import tkinter
from tkinter import filedialog
from time import sleep

import json
import os
import pandas as pd
import requests
import concurrent.futures
import sys
import re
import csv

#-----------------------------------------------------------------------------------------------------------------------------------------------

def SelectInput():
    my_filetypes = [('comma separated value file', '.csv')]  # input file in csv format
    global InputFile
    InputFile = filedialog.askopenfilename(initialdir=os.getcwd(), title="Please select a file:", filetypes=my_filetypes)
    window.destroy()


def ExitApp():
    global InputFile
    InputFile = None
    window.destroy()


def GetResponses(requests_to_DataCite, request_number):   # perform requests with requests library
    sleep(5)  # wait a bit before the api request is launched
    
    try:
        response = requests.get(requests_to_DataCite[request_number], timeout=120)  # timeout is specified so that the loop can continue if the server does not respond after a certain amount of time
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return "error"
    
    except requests.Timeout:
        return "error"
 

def main(requests_to_DataCite, count):  
    with concurrent.futures.ThreadPoolExecutor(12) as executor:
        DataCite_results = [executor.submit(GetResponses, requests_to_DataCite, n) for n in range(count)]  # asynchronous processing with concurrent library
              
        for i,x in enumerate(concurrent.futures.as_completed(DataCite_results), 1):
            sys.stdout.write("\rCurrent loop - DataCite API requests: %d of %d" % (i, count))
           
        sys.stdout.flush()
        
    return DataCite_results


def unpack(DataCite_results, n):
    try:  
        return DataCite_results[n].result()

    except:
        return "error"


def flatten(t):
    return [item for sublist in t for item in sublist]


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


#------------------------------------------------------------------------------------------------------------------------

window = tkinter.Tk()  # create dialog box to ask for input file
window.title("Upload file?")
window.geometry("1000x100")
window.minsize(1000, 100)

frame = tkinter.Frame(window)
frame.pack(expand=tkinter.YES)

text_window = tkinter.Label(frame, text="Do you want to upload a file containing all the publication author names for which you want to check if there is an associated dataset?")
text_window.pack()

bottom_frame = tkinter.Frame(window)
bottom_frame.pack(side=tkinter.BOTTOM)

bottom_frame_left = tkinter.Frame(bottom_frame)
bottom_frame_left.pack(side=tkinter.LEFT)
bottom_frame_right = tkinter.Frame(bottom_frame)
bottom_frame_right.pack(side=tkinter.RIGHT)

btn_side = tkinter.Button(bottom_frame_left, text="Yes", command=SelectInput)
btn_side.pack(padx=20)
btn_side_2 = tkinter.Button(bottom_frame_right, text="No", command=ExitApp)
btn_side_2.pack(padx=20)

window.mainloop()

#------------------------------------------------------------------------------------------------------------------------

if bool(InputFile) == tkinter.FALSE:  # abort if there is no input file
    sys.exit()
    
#------------------------------------------------------------------------------------------------------------------------    
    
source_df = pd.read_csv(InputFile, sep=r';', engine='python') # the uploaded csv should contain, for each publication, a row 
source_df_list = source_df.values.tolist()   

for i in range(len(source_df_list)):  # fetch author names
    without_NA = [x for x in source_df_list[i] if str(x) != 'nan'] # remove any nan-values from the list (nan-values caused by empty cells in source file)
     
    if (len(without_NA) % 2) != 0 and hasNumbers(without_NA[-1]) == True:  # check whether number of list elements is uneven and whether the last element (= DOI) contains numbers 
        n = 2
        without_NA = [without_NA[i * n:(i + 1) * n] for i in range((len(without_NA) + n - 1) // n )]  # create sublists per 2, so that name and family name are grouped per author
        source_df_list[i] = without_NA
    else:
        print("Record {0} does not have correct input structure.".format(i)) # warning if the input structure does not adhere to the conditions listed above

publication_year_input = input("\n\nInput here the dataset publication year that you want to examine:")

DataCite_requests = []  # write out request URLs to DataCite API
tracking_author = []
for authors in range(len(source_df_list)):
    for author in range(len(source_df_list[authors])):
        if len(source_df_list[authors][author]) == 2:
            DataCite_requests.append("https://api.datacite.org/dois?query=" + source_df_list[authors][author][0] + "+" + source_df_list[authors][author][1] + "+" + "publicationYear:" + publication_year_input)
            tracking_author.append((authors, author))

df_look_up = pd.DataFrame(list(zip(DataCite_requests, tracking_author)), columns =['DataCite_requests', 'tracking_author']) # datframe with all potential requests, as well as index information that allows to track the author in the original input data, for example source_df_list[0][0] for tracking_author (0,0)

DataCite_requests = list(set(DataCite_requests)) # filter out duplicates among the DataCite requests (if the same author is mentioned twice or more in the input data)

DataCite_requests_count = len(DataCite_requests) # total number of requests that have to be executed

DataCite_results_prior = main(DataCite_requests, DataCite_requests_count)  # get json metadata from DataCite API
DataCite_results = [DataCite_results_prior[n].result() for n in range(DataCite_requests_count)] # convert to results that can be processed
DataCite_results = [unpack(DataCite_results_prior, n) for n in range(DataCite_requests_count)] # convert to results that can be processed (to avoid errors)


#--------------------------------------------------------------------------------------------------------------------------

working_dir_input = input("\n\nInput here the path to the directory where the output files have to be saved:")  # for example: C:/Users/nvwetter/OneDrive - Vrije Universiteit Brussel/Documenten
os.chdir(working_dir_input)  # set working directory where output files are to be saved

column_header = ['publication_DOI_from_CRIS_system', 'DataCite_request_API', 'author_names', 'number_of_author_names', 'total_length_author_names', 'found_dataset_DOI', 'match_percentage_authors']
with open('Output_harvested_datasets_from_publication_author_names.csv', 'w') as myfile:  # create file to write our results
    wr = csv.writer(myfile, delimiter = ";")
    wr.writerow(column_header)

with open('Output_harvested_datasets_from_publication_author_names_raw_metadata.txt', 'w') as myfile: # create file to write harvested DataCite metadata records
    wr = csv.writer(myfile, delimiter = ";")
    
for result in range(len(DataCite_results)):
        
    if DataCite_results[result] != 'error': # DataCite requests that gave an error from the server, are excluded
        
        if len(DataCite_results[result]['data']) != 0:  # DataCite requests that did not yield a result ("metadata record"), are excluded
    
            number_of_records_within_request = len(DataCite_results[result]['data'])  # each request leads to a response that might contain multiple datasets
            range_of_records_within_request = range(len(DataCite_results[result]['data']))
            
            actual_request_authors =  df_look_up['DataCite_requests'] == DataCite_requests[result]  # go back to the original data to check which "author groups" (= all authors associated with a particular publication) are associated with this DataCite request
            actual_request_authors = df_look_up[actual_request_authors]
            
            author_groups = list(actual_request_authors['tracking_author'])
            author_groups = ([x[0] for x in author_groups]) # list with indexes that can be used to find the author group in source_df_list, for example source_df_list[3]
        
            for author_group in range(len(author_groups)): # per author group: establish search terms and look in DataCite response for matches
                search_terms = flatten(source_df_list[author_groups[author_group]]) # flatten the list (no sublists), to establish all the search terms
                publication_DOI = search_terms[-1]
                del search_terms[-1] # do not take into consideration DOI for matching
                number_search_terms = len(search_terms)
                char_length_search_terms = len("".join(search_terms))  # total number of characters for all names in the "author group" combined: with longer strings, it can be expected that matching is more meaningful 
            
                for DataCite_record in range_of_records_within_request: # the result of the DataCite request can contain multiple metadata records
                    
                    DataCite_record_string = str(DataCite_results[result]['data'][DataCite_record]).lower() # string of DataCite metadata record (lowercase) to base matching on
                    
                    matches = {x for x in search_terms if x.lower() in DataCite_record_string} # check whether any of the search terms (= author names) match with a (sub)string in the DataCite metadata record 
                    match_percentage = len(matches)/number_search_terms  # calculate match percentage: how many matches where found compared to the total number of search terms?
                    
                    stringified_json = json.dumps(DataCite_results[result]['data'][DataCite_record])
                    found_dataset_DOI = re.findall('"doi": "(.+?)",', stringified_json)  # extract dataset DOI out of DataCite metadata record
                    found_dataset_DOI = "".join(found_dataset_DOI) 
                    
                    
                    results_matching = [publication_DOI, DataCite_requests[result], search_terms, number_search_terms, char_length_search_terms, found_dataset_DOI, match_percentage]
                    df_final = pd.DataFrame([results_matching])
                    df_final.to_csv('Output_harvested_datasets_from_publication_author_names.csv', mode='a', index = False, header=False, sep = ";") # write to output file
                    
                    
                    df_metadata = pd.DataFrame([DataCite_record_string.replace(";", ",").replace("\\t", " ").replace("\\n", " ")])
                    df_metadata.to_csv('Output_harvested_datasets_from_publication_author_names_raw_metadata.txt', mode='a', index = False, header=False, sep = ";") # write harvested DataCite metadata to output file
                    
print("\n\nOutput files are available in the directory you specified.")
                    
                    
                    
                    
   



