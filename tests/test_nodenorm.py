import pytest
import TCT

# Some example queries for these tests.
EXAMPLE_QUERIES = [
    {
        'query': 'MESH:D003924',
        'curie': 'MONDO:0005148',
        'biolink_type': 'biolink:Disease',
    },
    {
        'query': 'UMLS:C0004096',
        'curie': 'MONDO:0004979',
        'biolink_type': 'biolink:Disease',
    },
    {
        'query': 'UNII:S6002H6J9F',
        'curie': 'CHEBI:32635',
        'biolink_type': 'biolink:SmallMolecule',
    },
    {
        'query': 'DRUGBANK:DB00083',
        'curie': 'UMLS:C0006050',
        'biolink_type': 'biolink:Protein',
    }
]

def test_nodenorm_status():
    """
    Test that NodeNorm can return status information.
    """
    status = TCT.node_normalizer.status()

    assert status['status'] == 'running'
    assert status['babel_version'] != ''
    assert status['babel_version_url'] != ''
    assert status['databases']['eq_id_to_id_db']['count'] > 650_000_000


def test_nodenorm_invalid():
    """
    Test that NodeNorm can handle invalid queries.
    """
    assert TCT.node_normalizer.get_normalized_nodes('') is None
    assert TCT.node_normalizer.get_normalized_nodes('MONDO:0000000') is None
    assert TCT.node_normalizer.get_normalized_nodes(['', 'MONDO:0000000']) == {
        '': None,
        'MONDO:0000000': None,
    }


@pytest.mark.parametrize("example_normalization", EXAMPLE_QUERIES)
def test_nodenorm_normalization(example_normalization):
    """
    Test some NodeNorm normalization with expected results.
    """

    result = TCT.node_normalizer.get_normalized_nodes(example_normalization['query'], return_equivalent_identifiers=True)

    assert result.curie == example_normalization['curie']
    assert result.types[0] == example_normalization['biolink_type']
