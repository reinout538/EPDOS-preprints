import os, sys
import csv
from xml.etree import ElementTree
from xml.etree.ElementTree import (Element, SubElement, Comment, tostring)
import pandas as pd

file_dir = sys.path[0]
vu_af_ids = ['60008734','60029124', '60117141', '60109852', '60014594']
df_missing_persons = pd.DataFrame(columns=['eid', 'au-id', 'au-surnm','au-init', 'af-ids'])

class buildXMLpreprint():
    
    def __init__(self, xml_record, xml_publications, int_person_df):
        pub_record = SubElement(xml_publications,'v1:workingPaper', subType='preprint', id='epdos_pp_'+xml_record.eid)

        self.peer_rev = self.build_peer_rev(pub_record)
        self.pub_cat = self.build_pub_cat(pub_record)
        self.publ_status = self.build_publication_status(pub_record, xml_record)
        self.workflow = self.build_workflow(pub_record)
        self.language = self.build_language(pub_record)
        self.main_title = self.build_main_title(pub_record, xml_record)
        self.sub_title = self.build_sub_title(pub_record, xml_record)
        self.abstract = self.build_abstract(pub_record, xml_record)
        self.contribution = self.build_persons(pub_record, xml_record, int_person_df)
        self.owner = self.build_owner(pub_record)
        #self.build_urls = self.build_urls()
        self.electr_version = self.build_electronic_version(pub_record, xml_record)
        self.visibility = self.build_visibility(pub_record)
        self.external_ids = self.build_external_ids(pub_record, xml_record)
        self.comments = self.build_comments(pub_record)
        #self.pages = self.build_pages()
        self.publisher = self.build_publisher(pub_record, xml_record)
        

    def build_peer_rev(self, pub_record):
        peer_reviewed = SubElement(pub_record, 'v1:peerReviewed')
        peer_reviewed.text = 'false'
            
    def build_pub_cat(self, pub_record):
        publ_cat = SubElement(pub_record, 'v1:publicationCategory')
        publ_cat.text = 'academic'
            
    def build_publication_status(self, pub_record, xml_record):
        publication_statuses = SubElement(pub_record, 'v1:publicationStatuses')
        publication_status = SubElement(publication_statuses, 'v1:publicationStatus')
        status_type = SubElement(publication_status, 'v1:statusType')
        status_type.text = 'published'
        status_date = SubElement(publication_status, 'v1:date')
        status_year = SubElement(status_date, 'v3:year')
        status_year.text = xml_record.pub_year
        if xml_record.pub_month != None:
            status_month = SubElement(status_date, 'v3:month')
            status_month.text = xml_record.pub_month
        if xml_record.pub_day != None:
            status_day = SubElement(status_date, 'v3:day')
            status_day.text = xml_record.pub_day

    def build_workflow(self, pub_record):
        workflow = SubElement(pub_record, 'v1:workflow')
        workflow.text = 'forApproval'    
        
    def build_language(self, pub_record):
        language = SubElement(pub_record, 'v1:language')
        language.text = 'en_GB'
    
    def build_main_title(self, pub_record, xml_record):
        main_title = SubElement(pub_record, 'v1:title')
        main_title_text = SubElement (main_title, 'v3:text')
        main_title_text.text = xml_record.main_title
        
    def build_sub_title(self, pub_record, xml_record):
        sub_title = SubElement(pub_record, 'v1:subTitle')
        sub_title_text = SubElement (sub_title, 'v3:text')
        sub_title_text.text = xml_record.sub_title

    def build_abstract(self, pub_record, xml_record):
        abstract = SubElement(pub_record, 'v1:abstract')
        abstract_text = SubElement (abstract, 'v3:text')
        abstract_text.text = xml_record.abstract
    
    def build_persons(self, pub_record, xml_record, int_person_df):
        persons = SubElement(pub_record, 'v1:persons')

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
            
            author = SubElement(persons, 'v1:author')
            role = SubElement(author, 'v1:role')
            role.text = 'author'
            person = SubElement(author, 'v1:person', id=author_rec['au-id'], origin=origin)
            firstname = SubElement(person, 'v1:firstName')
            firstname.text = author_rec['au-init']
            lastname = SubElement(person, 'v1:lastName')
            lastname.text = author_rec['au-surnm']

            #create author organisations
            if author_rec['au-affils'] != []:
                organisations = SubElement(author, 'v1:organisations')

                #external author
                if origin == 'external':
                    for affil in author_rec['au-affils']:   
                        organisation = SubElement (organisations, 'v1:organisation', id=affil['af-id'], origin='external')
                        
                        if 'af-name' in affil:
                            org_name = SubElement (organisation, 'v1:name')
                            org_name_text = SubElement (org_name, 'v3:text')
                            org_name_text.text = affil['af-name']
                        #missing person 
                        if affil['af-id'] in vu_af_ids:        
                            df_missing_persons.loc[len(df_missing_persons.index)] = [xml_record.eid, author_rec['au-id'], author_rec['au-surnm'], author_rec['au-init'], author_rec['au-affils']]
                            df_missing_persons.to_csv(os.path.join(file_dir, "missing_persons.csv"), encoding='utf-8', index = False)

                #internal author
                if origin == 'internal':
                    for affil in author_rec['au-affils']:
                        #vu affiliations
                        if affil['af-id'] in vu_af_ids:
                            yr_diff = 1000
                            affil_ct = 0
                            most_recent = None
                            #get pure affils from pure person df
                            pure_affil_match = int_person_df.loc[int_person_df['scopus_ids'] == author_rec['au-id'],'personaffiliations']
                            #select pure affil based on pub year
                            for pure_affils in pure_affil_match:
                                
                                for affil in pure_affils:
                                    
                                    #pub yr within affil -> add
                                    if affil['af_start'].year <= int(xml_record.pub_year) <= affil['af_end'].year:
                                        organisation = SubElement (organisations, 'v1:organisation', id=affil['af_org_id'], origin='internal')
                                        affil_ct += 1
                                    #evaluate as most recent
                                    else:
                                        yr_diff_affil = int(xml_record.pub_year) - affil['af_end'].year
                                        if yr_diff_affil < yr_diff and yr_diff_affil > 0:
                                            yr_diff = int(xml_record.pub_year) - affil['af_end'].year
                                            most_recent = affil['af_org_id']
                                    
                                #add most recent past affil
                                if affil_ct == 0 and most_recent != None:
                                    organisation = SubElement (organisations, 'v1:organisation', id=most_recent, origin='internal')
                                #before VU-affil so add VU as external org
                                elif affil_ct == 0 and most_recent == None:
                                    organisation = SubElement (organisations, 'v1:organisation', id='60008734', origin='external')
                                    
                        #add external affil
                        else:
                            organisation = SubElement (organisations, 'v1:organisation', id=affil['af-id'], origin='external')
                    
                    
    def build_owner(self, pub_record):
        
        owner_id = '971a8f57-d401-4e8b-9b1a-a1b97e46e0ea' #Vrije Universiteit - whole - library = owner
        
        """
        #find first HR-dept in contributor list to use as owner
        for contrib in json.contrib:
                        
            if contrib['origin'] == 'internal':
                for affil in contrib['auth_affil']:
                    if affil['affil_orig'] == 'internal' and  affil['affil_source_id'][0] == 'P':
                        owner_id = affil['affil_id']
                        pass
        """
        owner = SubElement(pub_record, 'v1:owner', id=owner_id)
        
    def build_urls(self):
        
        urls = SubElement(pub_record, 'v1:urls')    
        url = SubElement(urls, 'v1:url')
        url_value = SubElement(url, 'v1:url')
        url_value.text = f"http://www.scopus.com/inward/record.url?scp={EID}&partnerID=8YFLogxK"
        url_descr = SubElement(url, 'v1:description')
        descr_text = SubElement(url_descr, 'v3:text')
        descr_text.text = 'scopuspublication'
        url_type = SubElement(url, 'v1:type')
        url_type.text = 'scopuspublication'
    
    def build_electronic_version(self, pub_record, xml_record):
        if xml_record.doi != None:
            electronic_versions = SubElement(pub_record, 'v1:electronicVersions')    
            electronic_version_DOI = SubElement (electronic_versions, 'v1:electronicVersionDOI')
            DOI_version = SubElement (electronic_version_DOI, 'v1:version')
            DOI_version.text = 'publishersversion'
            #DOIlicense = SubElement (electronicVersionDOI, 'v1:license')
            DOI_access = SubElement (electronic_version_DOI, 'v1:publicAccess')
            DOI_access.text = 'open'
            DOI_value = SubElement (electronic_version_DOI, 'v1:doi')
            DOI_value.text = xml_record.doi
    
    def build_visibility(self, pub_record):
        visibility = SubElement(pub_record, 'v1:visibility')
        visibility.text = 'Public'

    def build_external_ids(self, pub_record, xml_record):
        external_ids = SubElement(pub_record, 'v1:externalIds')
        external_id_EID = SubElement(external_ids, 'v1:id', type='Scopus') 
        external_id_EID.text = xml_record.eid
    
    def build_comments(self, pub_record):
        comments = SubElement(pub_record, 'v1:comments')
        comment = SubElement(comments, 'v3:comment')
        comment_user = SubElement(comment, 'v3:username')
        comment_user.text = 'sync_user'
        comment_text = SubElement(comment, 'v3:text')
        comment_text.text = 'Library automated entry - source = EPDOS preprint xml'
   
    def build_pages(self):
        if json.pages != None:
            pages = SubElement(pub_record, 'v1:pages')
            pages.text = json.pages

        
    def build_publisher(self, pub_record, xml_record):
        if xml_record.publisher != None:
            publisher = SubElement(pub_record, 'v1:publisher')
            publ_name = SubElement(publisher, 'v1:name')
            publ_name.text = xml_record.publisher
        else: publisher = None
        
