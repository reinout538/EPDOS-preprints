# EPDOS-preprints
What it does:

1) get pandas dataframe of all internal person records in Pure via Pure-API (get_pure_internal persons.py)

2) loop over preprint xml-files in specified directory
  a) open file and parse xml (process_xml.py)
  b) add data to pd-dataframes for analyzing data in xml-records
  c) create xml-record for Pure-ingest 


