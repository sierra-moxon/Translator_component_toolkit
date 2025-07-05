import requests
import json
import pandas as pd

def get_KP_metadata(APInames):

    '''
    This function is used to get the metadata of the KPs in the APInames dictionary.
    Example:
    >>> metaKG = TCT.get_KP_metadata(APInames) 
    >>> All_predicates = list(set(metaKG['KG_category']))
    All_categories = list((set(list(set(metaKG['Subject']))+list(set(metaKG['Object'])))))
    '''

    result_df = pd.DataFrame()
    API_list = []
    URL_list = []
    KG_category_list = []
    subject_list = []
    object_list = []
    url_list = []
    #for KP in KPnames:
    for KP in APInames.keys():
        json_text ={}
        if KP == "RTX KG2 - TRAPI 1.5.0": 
            text =requests.get("https://smart-api.info/api/metakg/consolidated?size=20&q=%28api.x-translator.component%3AKP+AND+api.name%3ARTX+KG2+%5C-+TRAPI+1%5C.4%5C.0%29").text  # This works for the previous version
            json_text = json.loads(text)
        else:   
            text = requests.get(find_link(KP)).text
            json_text = json.loads(text)

        for i in (json_text['hits']):
            KG_category_list.append("biolink:"+i['_id'].split("-")[1])
            API_list.append(KP)
            subject_list.append('biolink:'+i['_id'].split("-")[0])
            object_list.append('biolink:'+i['_id'].split("-")[2])
            url_list.append(APInames[KP])

    result_df = pd.DataFrame({ 'API': API_list, 'KG_category': KG_category_list, "Subject":subject_list, "Object":object_list, "URL":url_list})
    
    return(result_df)


def add_new_API_for_query(APInames, metaKG, newAPIname, newAPIurl, newAPIcategory, newAPIsubject, newAPIobject):

    '''
    This function is used to add a new API beyond the current list of APIs for query
    Example: APInames, metaKG = add_new_API_for_query(APInames, metaKG, "BigGIM_BMG", "http://127.0.0.1:8000/find_path_by_predicate", "Gene-physically_interacts_with-gene", "Gene", "Gene")

    '''
    APInames[newAPIname] = newAPIurl

    new_row = pd.DataFrame({"API":newAPIname,
                            "KG_category":newAPIcategory,
                            "Subject":newAPIsubject, "Object":newAPIobject,
                            "URL":newAPIurl}, index=[0])
    metaKG = pd.concat([metaKG, new_row], ignore_index=True)
    return APInames, metaKG


def add_plover_API(APInames, metaKG):
    '''
    This function is used to add the Plover APIs developed by the CATRAX team to the APInames and metaKG.
    Current APIs include :
    CATRAX BigGIM DrugResponse Performance Phase, 
    CATRAX Pharmacogenomics, 
    Clinical Trials, 
    Drug Approvals, 
    Multiomics, 
    Microbiome, 
    and RTX KG2.
    
    Example: 
    >>> APInames, metaKG = add_plover_API(APInames, metaKG)
    '''
    

    import requests
    url = 'https://multiomics.rtx.ai:9990/BigGIM_DrugResponse_PerformancePhase/meta_knowledge_graph'
    response = requests.get(url)
    data = response.json()
    for i in range(len(data["edges"])):
        APInames, metaKG = add_new_API_for_query(APInames, metaKG, "CATRAX BigGIM DrugResponse Performance Phase KP - TRAPI 1.5.0", "https://multiomics.rtx.ai:9990/BigGIM_DrugResponse_PerformancePhase/query", data["edges"][i]['predicate'], data["edges"][i]['subject'], data["edges"][i]['object'])

        url = 'https://multiomics.rtx.ai:9990/PharmacogenomicsKG/meta_knowledge_graph'
        response = requests.get(url)
        data = response.json()
        for i in range(len(data["edges"])):
            APInames, metaKG = add_new_API_for_query(APInames, metaKG, "CATRAX Pharmacogenomics KP - TRAPI 1.5.0", "https://multiomics.rtx.ai:9990/PharmacogenomicsKG/query", data["edges"][i]['predicate'], data["edges"][i]['subject'], data["edges"][i]['object'])

    url = 'https://multiomics.rtx.ai:9990/ctkp/meta_knowledge_graph'
    response = requests.get(url)
    data = response.json()

    for i in range(len(data["edges"])):
        APInames, metaKG = add_new_API_for_query(APInames, metaKG, "Clinical Trials KP - TRAPI 1.5.0", "https://multiomics.rtx.ai:9990/ctkp/query", data["edges"][i]['predicate'], data["edges"][i]['subject'], data["edges"][i]['object'])

    url = 'https://multiomics.rtx.ai:9990/dakp/meta_knowledge_graph'
    response = requests.get(url)
    data = response.json()
    for i in range(len(data["edges"])):
        APInames, metaKG = add_new_API_for_query(APInames, metaKG, "Drug Approvals KP - TRAPI 1.5.0", "https://multiomics.rtx.ai:9990/dakp/query", data["edges"][i]['predicate'], data["edges"][i]['subject'], data["edges"][i]['object'])

    url = 'https://multiomics.rtx.ai:9990/dakp/meta_knowledge_graph'
    response = requests.get(url)
    data = response.json()
    for i in range(len(data["edges"])):
        APInames, metaKG = add_new_API_for_query(APInames, metaKG, "Multiomics KP - TRAPI 1.5.0", "https://multiomics.rtx.ai:9990/multiomics/query", data["edges"][i]['predicate'], data["edges"][i]['subject'], data["edges"][i]['object'])

    url = 'https://multiomics.rtx.ai:9990/mokp/meta_knowledge_graph'
    response = requests.get(url)
    data = response.json()
    for i in range(len(data["edges"])):
        APInames, metaKG = add_new_API_for_query(APInames, metaKG, "Microbiome KP - TRAPI 1.5.0", "https://multiomics.rtx.ai:9990/mbkp/query", data["edges"][i]['predicate'], data["edges"][i]['subject'], data["edges"][i]['object'])


    url = 'https://kg2cploverdb.ci.transltr.io/kg2c/meta_knowledge_graph'
    response = requests.get(url)
    data = response.json()
    for i in range(len(data["edges"])):
        APInames, metaKG = add_new_API_for_query(APInames, metaKG, "RTX KG2 - TRAPI 1.5.0", "https://kg2cploverdb.ci.transltr.io/kg2c/query", data["edges"][i]['predicate'], data["edges"][i]['subject'], data["edges"][i]['object'])


    
    return APInames, metaKG