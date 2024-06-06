class processXML():
    
    def __init__(self, root):
        self.eid = self.get_eid(root)
        self.doi = self.get_doi(root)
        self.vor_doi = self.get_vor_doi(root)
        self.authors = self.get_authors(root)
        self.pub_year = self.get_pub_date(root)[0]
        self.pub_month = self.get_pub_date(root)[1]
        self.pub_day = self.get_pub_date(root)[2]
        self.main_title = self.get_title(root)[0]
        self.sub_title = self.get_title(root)[1]
        self.abstract = self.get_abstract(root)
        self.publisher = self.get_publisher(root)
        #self.upw_locations = self.get_upw_locations(root)

    def get_eid(self, root):
        return root.find(".//{http://www.elsevier.com/xml/xocs/dtd}eid").text

    def get_doi(self, root):
        if root.find(".//{http://www.elsevier.com/xml/xocs/dtd}doi") != None:
            doi = root.find(".//{http://www.elsevier.com/xml/xocs/dtd}doi").text
        else:
            doi = None

        return doi

    def get_vor_doi(self, root):
        if root.find('.//itemid[@idtype="VORDOI"]') != None:
            vordoi = root.find('.//itemid[@idtype="VORDOI"]').text
        else:
            vordoi = None

        return vordoi

    def get_pub_date(self, root):
        year = root.find(".//publicationdate/year").text
        if root.find(".//publicationdate/month") != None:
            month = root.find(".//publicationdate/month").text
        else:
            month = None
        if root.find(".//publicationdate/day") != None:
            day = root.find(".//publicationdate/day").text
        else:
            day = None

        return year, month, day

    def get_title(self, root):
        if root.find(".//citation-title/titletext") != None:
            full_title = ''           
            for title_elem in list(root.find(".//citation-title/titletext").iter()):
                if title_elem.text != None:
                    full_title = full_title + title_elem.text
                if title_elem.tail != None:
                    full_title = full_title + title_elem.tail
            if ":" in full_title: 
                main_title = full_title.split(":",1)[0]
                sub_title = full_title.split(":",1)[1].lstrip()
            else: 
                main_title = full_title
                sub_title = None   
        else:
            main_title = None
            sub_title = None   
            
        return main_title, sub_title

    def get_abstract(self, root):
        if root.find(".//{http://www.elsevier.com/xml/ani/common}para") != None:
            abstract_text = ''
            for abstract_elem in list(root.find(".//{http://www.elsevier.com/xml/ani/common}para").iter()):
                if abstract_elem.text != None:
                    abstract_text = abstract_text + abstract_elem.text
                if abstract_elem.tail != None:
                    abstract_text = abstract_text + abstract_elem.tail
        else:
            abstract_text = None

        return abstract_text
                                
    def get_publisher(self, root):
        if root.find(".//publishername") != None:
            publisher = root.find(".//publishername").text
        else:
            publisher = None

        return publisher

    def get_upw_locations(self, root):
        upw_locations = root.findall(".//{http://www.elsevier.com/xml/xocs/dtd}upw-oa_location")
        for upw_location in upw_locations:
            print (upw_location)
    
    def get_authors(self, root):

        author_dict = {}
        
        #get unique authors
        authors = root.findall(".//{http://www.elsevier.com/xml/cto/dtd}unique-author")
        for author in authors:
            au_id = author.find(".//{http://www.elsevier.com/xml/cto/dtd}auth-id").text
            au_seq = author.attrib['seq']
            au_surnm = author.find(".//{http://www.elsevier.com/xml/cto/dtd}auth-surname").text
            if author.find(".//{http://www.elsevier.com/xml/cto/dtd}auth-initials") != None:
                au_init = author.find(".//{http://www.elsevier.com/xml/cto/dtd}auth-initials").text
            else:
                au_init = None
            au_index_nm = author.find(".//{http://www.elsevier.com/xml/cto/dtd}auth-indexed-name").text
            if author.find(".//{http://www.elsevier.com/xml/cto/dtd}orcid") != None:
                au_orcid = author.find(".//{http://www.elsevier.com/xml/cto/dtd}orcid").text
            else:
                au_orcid = None
            author_dict[au_id] = {'au-id':au_id,'au-seq':au_seq, 'au-surnm':au_surnm, 'au-init':au_init, 'au-index-nm':au_index_nm, 'au-orcid':au_orcid, 'au-affils':[]}
            
        #parse author groups
        author_groups = root.findall(".//author-group")

        for i, author_gr in enumerate(author_groups):

            #select authors and affiliation(s)
            affiliations = author_gr.findall(".//affiliation")
            authors = author_gr.findall(".//author")

            #get affiliation data
            for affiliation in affiliations:
                
                if 'afid' in affiliation.attrib:
                    afid = affiliation.attrib['afid']
                    aforg = affiliation.findall(".//organization")
                    afid_orig = ""
                    affil_list = []

                    #exception if affiliation in author group has no organization
                    if aforg == []:
                        af_name = "Unknown"
                        afid = "3ca7f9ae-5220-4ef9-a4fe-6dd2ba6f1cef"
                        print (af_name)
                    else:    
                        #if multiple org names select last one - which should be top-level
                        for org_name in aforg:
                            affil_list.append(org_name.text)
                            af_name = org_name.text
                            #exception for Amsterdam UMC affiliation under VU / 60008734
                            if "Amsterdam UMC" in af_name and afid == "60008734":
                                afid = "60001997"
                                afid_orig = "60008734"
                                break

                    #add affiliation to all authors in group   
                    for author in authors:
                        #add affil-id to list in author dict
                        afid_list = [id.get('af-id') for id in author_dict[author.attrib['auid']]['au-affils']]
                        
                        if afid not in afid_list:
                            author_dict[author.attrib['auid']]['au-affils'].append({'af-id':afid, 'af-name': af_name, "af-id_orig": afid_orig, "affil_list": affil_list})
                        else:
                            continue
                        
        return author_dict
