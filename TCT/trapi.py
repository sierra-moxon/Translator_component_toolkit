"""
This is a wrapper around making calls to the Translator Reasoner API (TRAPI).

API Documentation: https://github.com/NCATSTranslator/ReasonerAPI

Additional API Documentation: https://github.com/NCATSTranslator/ReasonerAPI/blob/master/docs/reference.md
"""
import json
import urllib.parse

import requests

# TODO: implement...

def build_query(subject_ids:list[str],
        object_categories:list[str], predicates:list[str],
        return_json:bool=True,
        object_ids=None, subject_categories=None):
    """
    This constructs a query json for use with TRAPI. Queries are of the form [subject_ids]-[predicates]-[object_categories].
    The output for the query contains all the subject-predicate-object triples where the subject is in subject_ids,
    the object's category is in object_categories, and the predicate for the edge is in predicates.

    For a description of the existing biolink categories and predicates, see https://biolink.github.io/biolink-model/

    Params
    ------
    subject_ids
        A list of subject CURIE IDs - example: ["NCBIGene:3845"]

    object_categories
        A list of strings representing the object categories that we are interested in. Example: ["biolink:Gene"]

    predicates
        A list of predicates that we are interested in. Example: ["biolink:positively_correlated_with", "biolink:physically_interacts_with"].

    return_json
        If true, returns a json string; if false, returns a dict.

    object_ids
        None by default
    subject_categories
        None by default

    Returns
    -------
    A json string

    Examples
    --------
    >>> build_query(['NCBIGene:3845'], ['biolink:Gene'], ['biolink:physically_interacts_with'])
    """
    query_dict = {
        'message': {
            'query_graph': {
                'edges': {
                    'e00': {
                        'subject': 'n00',
                        'object': 'n01',
                        'predicates': predicates
                    }
                },
                'nodes': {
                    'n00': {
                        'ids': subject_ids
                    },
                    'n01': {
                        'categories': object_categories
                    }
                },
            }
        }
    }
    if return_json:
        return json.dumps(query_dict)
    else:
        return query_dict


def query(url:str):
    """
    TODO: unimplemented

    Params
    ------
    url : str
        The URL for the API endpoint.

    Returns
    -------
    TODO
    """
