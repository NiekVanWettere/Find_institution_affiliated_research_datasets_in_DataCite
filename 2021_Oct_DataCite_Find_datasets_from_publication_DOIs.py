# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 12:21:37 2021

@author: nvwetter
"""


# Script that can be used to search for dataset DOIs and associated metadata on the basis of publication DOIs that are registered as related identifier in the DataCite dataset metadata

import concurrent.futures
import json
import os
import sys
import tkinter
from time import sleep
from tkinter import filedialog

import pandas as pd
import requests


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


#------------------------------------------------------------------------------------------------------------------------

window = tkinter.Tk()  # create dialog box to ask for input file
window.title("Upload file?")
window.geometry("1000x100")
window.minsize(1000, 100)

frame = tkinter.Frame(window)
frame.pack(expand=tkinter.YES)

text_window = tkinter.Label(frame, text="Do you want to upload a file containing all the publication DOIs for which you want to check if there is an associated dataset?")
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
 
DOI_pub_df = pd.read_csv(InputFile, sep=r'\s*,\s*', engine='python')  # read csv input file
DOI_pub = DOI_pub_df['DOI']  # select column with DOIs of related identifiers in csv input file

DataCite_requests = []  # write out request URLs to DataCite API
for x in range(0, len(DOI_pub)):
    DataCite_requests.append(
        "https://api.datacite.org/dois?query=relatedIdentifiers.relatedIdentifier:" + DOI_pub[x])

DataCite_requests_count = len(DataCite_requests) # total number of requests that have to be executed


DataCite_results_prior = main(DataCite_requests, DataCite_requests_count)  # get json metadata from DataCite API
DataCite_results = [DataCite_results_prior[n].result() for n in range(DataCite_requests_count)] # convert to results that can be processed


PID_dataset = []  # overview of lists used in loop below
title_dataset = []
publisher_dataset = []
year_dataset = []
description_dataset = []
rights_1 = []
rights_2 = []
relatedIdentifiers_comb_list = []
relatedIdentifiers_comb_list_2 = []
name_list = []
affiliation_list = []
nameIdentifier_list = []
name_comb_list = []
affiliation_comb_list = []
nameIdentifier_comb_list = []

for dataset_number in range(0, len(DataCite_results)):  # collect certain metadata from json format

    if DataCite_results[dataset_number]['data']:

        for dataset_number_bis in range(0, len(DataCite_results[dataset_number]['data'])):

            name_list = []
            name_comb = []
            affiliation_list = []
            affiliation_comb = []
            nameIdentifier_list = []
            nameIdentifier_comb = []
            relatedIdentifiers = []
            relatedIdentifiers_comb = []
            relatedIdentifiers_comb_list = []

            # PID

            try:
                PID_dataset.append(DataCite_results[dataset_number]['data'][dataset_number_bis]['id'])

            except KeyError:
                PID_dataset.append("no title")

            except IndexError:
                PID_dataset.append("no title")

            # title

            try:
                title_dataset.append(
                    DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes']["titles"][0][
                        "title"])

            except KeyError:
                title_dataset.append("no title")

            except IndexError:
                title_dataset.append("no title")

            # publisher

            try:
                publisher_dataset.append(
                    DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes']["publisher"])

            except KeyError:
                publisher_dataset.append("no year")

            except IndexError:
                publisher_dataset.append("no year")

            # year

            try:
                year_dataset.append(
                    DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes']["publicationYear"])

            except KeyError:
                year_dataset.append("no year")

            except IndexError:
                year_dataset.append("no year")

            # description

            try:
                description_dataset.append(
                    DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes']["descriptions"][0][
                        "description"])

            except KeyError:
                description_dataset.append("no description")

            except IndexError:
                description_dataset.append("no description")

            # rights 1 (note that this does not extract rightsUri)

            try:
                rights_1.append(
                    DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes']["rightsList"][0][
                        "rights"])

            except KeyError:
                rights_1.append("no rights info")

            except IndexError:
                rights_1.append("no rights info")

            # rights 2 (note that this does not extract rightsUri)

            try:
                rights_2.append(
                    DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes']["rightsList"][1][
                        "rights"])

            except KeyError:
                rights_2.append("no rights info")

            except IndexError:
                rights_2.append("no rights info")

            # related identifiers

            for dataset_number_2 in range(0, len(
                    DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes'][
                        "relatedIdentifiers"])):
                relatedIdentifiers = \
                DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes']["relatedIdentifiers"][
                    dataset_number_2].values()
                relatedIdentifiers_comb = " ; ".join(relatedIdentifiers)
                relatedIdentifiers_comb_list.append(relatedIdentifiers_comb)

            relatedIdentifiers_comb_list_2.append(" / ".join(relatedIdentifiers_comb_list))

            # data creator metadata

            for dataset_number_3 in range(0, len(
                    DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes']["creators"])):

                # name data creator

                name = DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes']["creators"][
                    dataset_number_3]["name"]
                name_list.append(name)

                # affiliation data creator

                affiliation_1 = \
                DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes']["creators"][
                    dataset_number_3]["affiliation"]
                if len(affiliation_1) > 1:
                    affiliation_2 = " & ".join(affiliation_1)
                    affiliation_list.append(affiliation_2)

                elif len(affiliation_1) == 1:
                    affiliation_list.append(affiliation_1[0])

                else:
                    affiliation_list.append("no affiliation")

                # identifier data creator

                try:
                    nameIdentifier = \
                    DataCite_results[dataset_number]['data'][dataset_number_bis]['attributes']["creators"][
                        dataset_number_3]["nameIdentifiers"][0]["nameIdentifier"]
                    nameIdentifier_list.append(nameIdentifier)

                except KeyError:
                    nameIdentifier_list.append("no nameIdentifier")

                except IndexError:
                    nameIdentifier_list.append("no nameIdentifier")

            name_comb = " / ".join(name_list)
            name_comb_list.append(name_comb)
            affiliation_comb = " / ".join(affiliation_list)
            affiliation_comb_list.append(affiliation_comb)
            nameIdentifier_comb = " / ".join(nameIdentifier_list)
            nameIdentifier_comb_list.append(nameIdentifier_comb)

# assemble metadata in dataframe and write dataframe to Excel output file (in directory of input file)
df = pd.DataFrame(list(
    zip(PID_dataset, title_dataset, publisher_dataset, year_dataset, description_dataset, rights_1, rights_2,
        relatedIdentifiers_comb_list_2, name_comb_list, affiliation_comb_list, nameIdentifier_comb_list)),
                  columns=["PID", "title", "publisher", "year", "description", "rights_1", "rights_2",
                           "relatedIdentifiers", "name", "affiliation", "nameIdentifier"])
df.to_excel((os.path.dirname(InputFile) + '/Output_harvested_datasets_from_publication_DOIs.xlsx'), index=False, header=True)
print("\n\nOutput file is available in directory of input file.")

print("\nDone.")