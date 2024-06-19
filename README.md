# EPDOS-preprints
What it does:

1) get pandas dataframe of all internal person records in Pure via Pure-API (get_pure_internal persons.py)

2) loop over preprint xml-files in specified directory - for each file:
   
   a) open file and parse xml (process_xml.py)
   [creates dictionary of authors and organizations]
   
   b) match scopus-AUIDs xml to scopus-AUIDs in Pure person records
   
   c) add data to pd-dataframes for analyzing xml-record data on publ record / authors / affiliations
   
   d) create xml-record for Pure-ingest (build_xml_pure.py)

4) save xml-file for pure ingest

5) save pd-dataframes as csv-files


