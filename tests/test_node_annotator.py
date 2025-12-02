import TCT
import pytest

CURIES_with_annotations = [
    {
        'curie': 'MONDO:0005148',
        'expected': {
            'query': 'MONDO:0005148',
            'disease_ontology.name': 'type 2 diabetes mellitus',
            'sections': ['disease_ontology', 'mondo', 'umls'],
        },
    },
    {
        'curie': 'CHEBI:231601',
        'expected': {
            'query': 'CHEBI:231601',
            'sections': ['chebi'],
        },
    },
    {
        'curie': 'CHEBI:15377',
        'expected': {
            'query': 'CHEBI:15377',
            'boxed_warning': True,
            'sections': ['aeolus', 'chebi', 'chembl', 'clinical_approval', 'clinical_trials', 'drugbank', 'ndc', 'pubchem', 'unichem', 'unii'],
            'chembl.availability_type': 2,
        },
    },
    {
        'curie': 'NCIT:C34373',
        'expected': {},
    },
    {
        'curie': 'MONDO:0004976',
        'expected': {
            'query': 'MONDO:0004976',
            'disease_ontology.name': 'amyotrophic lateral sclerosis',
            'sections': ['disease_ontology', 'mondo', 'umls'],
        },
    },
    {
        'curie': 'NCBIGene:1756',
        'expected': {
            'query': '1756',
            'taxid': 9606,
            'name': 'dystrophin',
            'type_of_gene': 'protein-coding',
            'sections': ['go', 'interpro'],
        },
    },
    {
        'curie': 'UniProtKB:P00395',
        'expected': {
            'query': 'P00395',
            'symbol': 'MT-CO1',
            'taxid': 9606,
            'type_of_gene': 'protein-coding',
            'sections': ['go', 'interpro'],
            'name': 'cytochrome c oxidase subunit I',
        },
    }
]


def test_status():
    result = TCT.node_annotator.status()
    assert result['success']


@pytest.mark.parametrize("curie_with_annotations", CURIES_with_annotations)
def test_curie(curie_with_annotations):
    curie = curie_with_annotations['curie']
    result = TCT.node_annotator.lookup_curie(curie)
    if result == {} and curie_with_annotations['expected'] == {}:
        # We expected no annotations and got no annotations.
        pytest.skip(f"No annotations found for CURIE '{curie}'")

    # Did we get more than one result?
    assert len(result) == 1
    result = result[0]
    expected_result = curie_with_annotations['expected']

    if expected_result == {}:
        assert result == {}

    # Check sections.
    if 'sections' in expected_result:
        for section in expected_result['sections']:
            assert section in result

    # Check some top-level fields.
    if 'query' in expected_result:
        assert result['query'] == expected_result['query']

    if 'name' in expected_result:
        assert result['name'] == expected_result['name']

    if 'taxid' in expected_result:
        assert result['taxid'] == expected_result['taxid']

    if 'type_of_gene' in expected_result:
        assert result['type_of_gene'] == expected_result['type_of_gene']

    if 'boxed_warning' in expected_result:
        assert result['boxed_warning'] == expected_result['boxed_warning']

    # Check some subsection fields.
    if 'disease_ontology.name' in expected_result:
        assert result['disease_ontology']['name'] == expected_result['disease_ontology.name']

    if 'chembl.availability_type' in expected_result:
        assert result['chembl']['availability_type'] == expected_result['chembl.availability_type']
