import requests
import json
import pandas as pd
from TCT import translator_metakg
from TCT import translator_kpinfo

def find_link(name):
    #pre = "https://dev.smart-api.info/api/metakg/consolidated?size=2000&q=%28api.x-translator.component%3AKP+AND+api.name%3A" # This works for the previous version
    pre = "https://smart-api.info/api/metakg/consolidated?size=2000&q=%28api.x-translator.component%3AKP+AND+api.name%3A" 
    end = "%5C%28Trapi+v1.5.0%5C%29%29"
    if '(Trapi v1.5.0)' in name:
        url = pre
        name_raw = name.split("(")[0]
        words = name_raw.split(" ")
    
        length = len(words)
        if length == 1:
            url = url + words[0] + end
        else:
            for i in range(0,length-1):
                url = url + words[i] + "+"
            url = url+words[length-1]+end
    
    else:
        words = name.split(" ")
        url = pre
        length = len(words)
        
        for i in range(0,length-1):
            url = url + words[i] + "+"
        url = url+words[length-1]+"%29"
    return(url)

def get_KP_metadata(APInames:dict[str, str]) -> pd.DataFrame:
    '''
    This function is used to get the metadata of the KPs in the APInames dictionary.

    Parameters
    ----------
    APInames : dict
        This is the second output of `TCT.translator_kpinfo.get_translator_kpinfo()`. This is a dict of API name to API URL.

    Returns
    -------
    metaKG : pandas.DataFrame
        This is a dataframe that represents the meta KG for the KPs in the APInames input - columns include [TODO].

    Examples
    --------
    >>> metaKG = TCT.get_KP_metadata(APInames) 
    >>> All_predicates = list(set(metaKG['Predicate']))
    All_categories = list((set(list(set(metaKG['Subject']))+list(set(metaKG['Object'])))))
    '''

    result_df = pd.DataFrame()
    API_list = []
    URL_list = []
    Predicate_list = []
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
            Predicate_list.append("biolink:"+i['_id'].split("-")[1])
            API_list.append(KP)
            subject_list.append('biolink:'+i['_id'].split("-")[0])
            object_list.append('biolink:'+i['_id'].split("-")[2])
            url_list.append(APInames[KP])

    result_df = pd.DataFrame({ 'API': API_list, 'Predicate': Predicate_list, "Subject":subject_list, "Object":object_list, "URL":url_list})
    
    return(result_df)


def add_new_API_for_query(APInames:dict[str, str], metaKG:pd.DataFrame, newAPIname:str, newAPIurl:str, newAPIpredicate:str, newAPIsubject:str, newAPIobject:str):
    '''
    This function is used to add a new API beyond the current list of APIs for query

    Parameters
    ----------
    APInames : dict
        This is the second output of `TCT.translator_kpinfo.get_translator_kpinfo()`.

    metaKG : pandas.DataFrame
        This is the output of `get_kp_metadata`.

    newAPIname : str

    newAPIurl : str

    newAPIpredicate : str

    newAPIsubject : str

    newAPIobject : str


    Returns
    -------

    Examples
    --------
    >>> APInames, metaKG = add_new_API_for_query(APInames, metaKG, "BigGIM_BMG", "http://127.0.0.1:8000/find_path_by_predicate", "Gene-physically_interacts_with-gene", "Gene", "Gene")

    '''
    APInames[newAPIname] = newAPIurl

    new_row = pd.DataFrame({"API":newAPIname,
                            "Predicate":newAPIpredicate,
                            "Subject":newAPIsubject, "Object":newAPIobject,
                            "URL":newAPIurl}, index=[0])
    metaKG = pd.concat([metaKG, new_row], ignore_index=True)
    return APInames, metaKG


def add_plover_API(APInames:dict[str, str], metaKG:pd.DataFrame):
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

    Parameters
    ----------
    APInames : dict
        This is the second output of `TCT.translator_kpinfo.get_translator_kpinfo()`. This is a dict of API name to API URL.

    metaKG : pandas.DataFrame
        This is the output of `get_kp_metadata`.




    Examples
    --------
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

    url = 'https://multiomics.rtx.ai:9990/mokp/meta_knowledge_graph'
    response = requests.get(url)
    data = response.json()
    for i in range(len(data["edges"])):
        APInames, metaKG = add_new_API_for_query(APInames, metaKG, "Multiomics KP - TRAPI 1.5.0", "https://multiomics.rtx.ai:9990/multiomics/query", data["edges"][i]['predicate'], data["edges"][i]['subject'], data["edges"][i]['object'])

    url = 'https://multiomics.rtx.ai:9990/mbkp/meta_knowledge_graph'
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
