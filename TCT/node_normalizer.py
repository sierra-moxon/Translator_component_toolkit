"""
This is a wrapper around the Node Normalizer API.

API docs: https://nodenorm.transltr.io/docs
"""
import urllib.parse

import requests

from .translator_node import TranslatorNode


URL = 'https://nodenorm.transltr.io/'

def get_normalized_nodes(query: str, **kwargs):
    """
    A wrapper around the `get_normalized_nodes` api endpoint. Given a CURIE or a list of CURIEs, this returns a list of normalized identifiers.
    
    Parameters
    ----------
    query : str
        Query CURIE
    **kwargs
        Other arguments to `synonyms`

    Returns
    -------
    Dict of CURIE id : TranslatorNode
    """
    path = urllib.parse.urljoin(URL, 'synonyms')
    # set autocomplete to be false by default
    response = requests.get(path, params={'string': query, **kwargs})
    if response.status_code == 200:
        result = response.json()
        if len(result) == 0:
            raise LookupError('No matching CURIE found for the given string ' + query)
        else:
            all_nodes = {}
            for k, node in result.items():
                curie = node['curie']
                n = TranslatorNode(curie)
                if 'preferred_name' in node:
                    n.label = node['preferred_name']
                if 'types' in node:
                    n.types = node['types']
                if 'names' in node:
                    n.synonyms = node['names']
                all_nodes[k] = n
            return all_nodes
    else:
        raise requests.RequestException('Response from server had error, code ' + str(response.status_code))
