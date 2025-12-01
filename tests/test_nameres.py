import pytest
import TCT

# Example NameRes searches to use in these tests.
EXAMPLE_SEARCHES = [
    {
        'query': 'diabetes type 2',
        'expect_results': [{
            'curie': 'MONDO:0005148',
            'biolink_type': 'biolink:Disease',
        }]
    },
    {
        'query': 'asthma',
        'expect_results': [{
            'curie': 'MONDO:0004979',
            'biolink_type': 'biolink:Disease',
        }],
    },
    {
        'query': 'Trastuzumab',
        'expect_results': [{
            'curie': 'CHEBI:231601',
            'biolink_type': 'biolink:ChemicalEntity',
        }],
    },
    {
        'query': 'Botulinum toxin type A',
        'expect_results': [{
            'curie': 'DRUGBANK:DB00083',
            'biolink_type': 'biolink:ChemicalEntity',
        }],
    }
]

def test_nameres_status():
    """
    Test that NameRes can return status information.
    """
    status = TCT.name_resolver.status()

    assert status['status'] == 'ok'
    assert status['babel_version'] != ''
    assert status['babel_version_url'] != ''
    assert status['numDocs'] > 425_000_000


def test_nameres_incorrect():
    """
    Test that NameRes returns no results for an incorrect query.
    """
    with pytest.raises(LookupError):
        TCT.name_resolver.lookup("")

    with pytest.raises(LookupError):
        TCT.name_resolver.lookup("supercalifragilisticexpialidocious")

@pytest.mark.parametrize("example_search", EXAMPLE_SEARCHES)
def test_nameres_search(example_search):
    """
    Test some simple NameRes searches with expected results.
    """

    results = TCT.name_resolver.lookup(example_search['query'], return_top_response=False, limit=10)

    # Check if we got any results at all
    assert len(results) > 0

    # Check if one of the top 10 results is the ID we expect.
    results_by_curie = dict([(result.curie, result) for result in results])
    for expect_result in example_search['expect_results']:
        # Is the expected result in the top-10 results?
        assert expect_result['curie'] in results_by_curie

        result_to_check = results_by_curie[expect_result['curie']]
        assert len(result_to_check.types) > 0
        assert result_to_check.types[0] == expect_result['biolink_type']

    # Check if the top response is the one we expect.
    result = TCT.name_resolver.lookup(example_search['query'], return_top_response=True)
    assert result.curie == example_search['expect_results'][0]['curie']


@pytest.mark.parametrize("example_search", EXAMPLE_SEARCHES)
def test_nameres_synonyms(example_search):
    """
    Test that NameRes returns the expected synonyms for a given query.
    """

    # We use the example search, but backwards: we check the expected CURIE(s)
    # to see if we get the query as a synonym.
    for expect_result in example_search['expect_results']:
        curie = expect_result['curie']
        results = TCT.name_resolver.synonyms(curie)
        assert curie in results
        node = results[curie]
        assert isinstance(node, TCT.translator_node.TranslatorNode)

        synonyms_lower = [synonym.lower() for synonym in node.synonyms]
        assert len(synonyms_lower) > 0

        # In most cases this should include the query as a synonym, but
        # this is not the case for "paracetamol".
        # assert example_search['query'].lower() in synonyms_lower
