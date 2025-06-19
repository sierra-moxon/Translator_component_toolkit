"""
This is a wrapper around the Name Resolver API.

API docs: https://name-lookup.ci.transltr.io/doc
"""
import urllib.parse

import requests

from .translator_node import TranslatorNode

"""This is the root URL for the API."""
URL = 'https://name-lookup.ci.transltr.io/'


def lookup(query: str, return_top_response:bool=True, return_synonyms:bool=False, **kwargs):
    """
    A wrapper around the `lookup` api endpoint. Given a query string, this returns a TranslatorNode object or a list of TranslatorNode objects corresponding to the given name. 

    Parameters
    ----------
    query : str
        Query string
    return_top_response : bool
        If true, this returns only the top response. If false, this returns a list of all responses.
    return_synonyms : bool
        If true, the resulting TranslatorNode objects contain a list of synonyms. If false, they do not include synonyms.
    **kwargs
        Other arguments to `lookup`

    Returns
    -------
    TranslatorNode object if return_top_response is True, list of TranslatorNode objects if return_top_response is False
    """
    path = urllib.parse.urljoin(URL, 'lookup')
    # set autocomplete to be false by default
    if 'autocomplete' not in kwargs:
        kwargs['autocomplete'] = False
    response = requests.get(path, params={'string': query, **kwargs})
    if response.status_code == 200:
        result = response.json()
        if len(result) == 0:
            raise LookupError('No matching CURIE found for the given string ' + query)
        else:
            if return_top_response:
                node = result[0]
                n = TranslatorNode(node['curie'])
                if 'label' in node:
                    n.label = node['label']
                if 'types' in node:
                    n.types = node['types']
                if return_synonyms and 'synonyms' in node:
                    n.synonyms = node['synonyms']
                return n
            else:
                all_nodes = []
                for node in result:
                    curie = node['curie']
                    n = TranslatorNode(curie)
                    if 'label' in node:
                        n.label = node['label']
                    if 'types' in node:
                        n.types = node['types']
                    if return_synonyms and 'synonyms' in node:
                        n.synonyms = node['synonyms']
                    all_nodes.append(n)
                return all_nodes
    else:
        raise requests.RequestException('Response from server had error, code ' + str(response.status_code))


def synonyms(query: str, **kwargs):
    """
    A wrapper around the `synonyms` api endpoint. Given a query string, this returns a TranslatorNode object or a list of TranslatorNode objects corresponding to the given name. 

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


