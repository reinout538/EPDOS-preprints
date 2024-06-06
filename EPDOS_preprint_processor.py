import os, sys
import csv
import math
import pandas as pd
from xml.etree import ElementTree
from xml.etree.ElementTree import (Element, SubElement, Comment, tostring)
from xml.dom import minidom

from get_pure_persons.get_pure_internal_persons import get_pure_internal_persons
from process_xml import  processXML
from build_xml_pure import buildXMLpreprint

file_dir = sys.path[0]
xml_file = 'xml_pure_preprints.xml'

vu_af_ids = ['60008734','60029124', '60117141', '60109852', '60014594']

#df logs
df_records = pd.DataFrame(columns=['eid', 'doi', 'pub-year', 'pub-month', 'pub-day', 'main-title', 'sub_title', 'abstract', 'publisher', 'vor-doi'])
df_authors = pd.DataFrame(columns=['eid', 'au-id', 'au-seq', 'au-surnm','au-init', 'au-orcid', 'af-ids', 'pure-uuid'])
df_author_affils = pd.DataFrame(columns=['eid', 'au-id', 'af-id', 'af-id original', 'af-name', 'af-namelist', 'internal/external'])

#main

#get internal person records from Pure as df
int_person_df = get_pure_internal_persons()[5]

#header xml for Pure
xml_publications = Element('v1:publications', {'xmlns:v1':"v1.publication-import.base-uk.pure.atira.dk", "xmlns:v3":"v3.commons.pure.atira.dk"})

#load the XML files
for n, file in enumerate(os.listdir(os.path.join(file_dir, 'source_xml'))[0:]):

    print(f"{file} - {n} of {len(os.listdir(os.path.join(file_dir, 'source_xml')))}")
    
    tree = ElementTree.parse(os.path.join(file_dir, 'source_xml',file))
    root = tree.getroot()

    #parse xml file
    xml_record = processXML(root)

    #add xml-data to dataframes
    for author in xml_record.authors:
        
        author_rec = xml_record.authors[author]

        #match scopus au-id with pure person records df 
        pure_match = int_person_df.loc[int_person_df['scopus_ids'] == author_rec['au-id']]
        if not pure_match.empty:
            #create as internal author
            origin = 'internal'
            for row_label, row in pure_match.iterrows():
                uuid_pure = row['person_uuid']
                matches = len(pure_match.index)
                    
        else:
            #create as external author
            uuid_pure = None
            origin = 'external'
        
        df_authors.loc[len(df_authors.index)] = [xml_record.eid, author_rec['au-id'], author_rec['au-seq'], author_rec['au-surnm'], author_rec['au-init'],author_rec['au-orcid'], author_rec['au-affils'],uuid_pure]
        for affil in author_rec['au-affils']:
            if affil['af-id'] in vu_af_ids:
                affil_orig = 'internal'
            else:
                affil_orig = 'external'
            df_author_affils.loc[len(df_author_affils.index)] = [xml_record.eid, author_rec['au-id'], affil['af-id'], affil['af-id_orig'], affil['af-name'], affil['affil_list'], affil_orig]
    
    df_records.loc[len(df_records.index)] = [xml_record.eid, xml_record.doi, xml_record.pub_year, xml_record.pub_month, xml_record.pub_day, xml_record.main_title, xml_record.sub_title, xml_record.abstract, xml_record.publisher, xml_record.vor_doi]
    
    #build xml for Pure
    buildXMLpreprint(xml_record, xml_publications, int_person_df)

xmlstr = minidom.parseString(tostring(xml_publications)).toprettyxml(indent="   ")
                                                                                                                           
xml_file = open(os.path.join(file_dir, xml_file), "w", encoding = 'UTF-8')
xml_file.write(xmlstr)
xml_file.close()

#save dataframes to csv
df_records.to_csv(os.path.join(file_dir, "log_pp_records.csv"), encoding='utf-8', index = False)
df_authors.to_csv(os.path.join(file_dir, "log_authors.csv"), encoding='utf-8', index = False)
df_author_affils.to_csv(os.path.join(file_dir, "log_author_affils.csv"), encoding='utf-8', index = False)        

