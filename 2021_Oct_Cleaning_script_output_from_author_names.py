# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 15:53:09 2021

@author: nvwetter
"""

# Script to remove some of the less useful results obtained by means of the script "2021_Oct_DataCite_Find_datasets_from_author_names.py". These "less useful results" include duplicate dataset DOIs and version DOIs.

import pandas as pd
import re
import os

input_file = input("\n\nInput here the path to the input file:")  # for example: C:/Users/nvwetter/OneDrive - Vrije Universiteit Brussel/Documenten/input.xlsx
metadata_harvest = pd.read_excel(input_file)  # read excel input file

metadata_harvest.drop("DataCite_request_API", inplace=True, axis=1)  # drop certain columns
metadata_harvest.drop("author_names", inplace=True, axis=1)

metadata_harvest_reduced = metadata_harvest.drop_duplicates()  # delete duplicate rows

dataset_DOIs = list(metadata_harvest_reduced["found_dataset_DOI"]) # list of dataset DOIs

row_delete = []
for count, doi in enumerate(dataset_DOIs):
    
    abbr_doi = re.sub('.v[0-9](/t\d+)?$', '', doi)
    
    if abbr_doi in dataset_DOIs:  # only delete version DOIs if the concept DOI is present in the metadata
        x = bool(re.search('.v[0-9](/t\d+)?$', doi))   # remove DOIs that end with version-like information
        row_delete.append(x)
    
    else:
        dataset_DOIs[count] = abbr_doi
        row_delete.append(False)

row_delete_2 = [not x for x in row_delete]
metadata_harvest_reduced_2 = metadata_harvest_reduced[row_delete_2]  # delete rows with version DOIs

writer = pd.ExcelWriter((os.path.dirname(input_file) + '/Output_harvested_datasets_from_publication_author_names_reduced.xlsx'))
metadata_harvest_reduced_2.to_excel(writer, index=False, header=True)
writer.save()

print("\n\nOutput file is available in directory of input file.")
print("\nDone.")
