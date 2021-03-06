# Find institution-affiliated research datasets via DataCite API

The Python scripts in this repository help you to identify datasets affiliated to your institution via DataCite, on the basis of publication DOIs affiliated to your institution (cf. "2021_Oct_DataCite_Find_datasets_from_publication_DOIs.py") or matching between author names mentioned in relevant publications and DataCite metadata records ("2021_Oct_DataCite_Find_datasets_from_author_names.py").

In the first case, the script relies on a publication DOI that is mentioned in the DataCite dataset metadata as related identifier. Therefore, associated datasets can only be discovered insofar the DataCite metadata of the dataset contains the publication DOI as related identifier. In the second case, the algorithm is based on the following principle: the more there is an overlap between author names of an institution-affiliated publication and a particular DataCite dataset metadata record, the more likely it becomes that the found dataset is relevant for your institution (= higher matching percentage). Moreover, a publication year needs to be specified in order to limit the scope of the search. This second procedure is probabilistic in nature and does not guarantee that all harvested results are relevant.

See the example files to see how the input should be structured and which type of output can be expected.
