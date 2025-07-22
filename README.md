Introduction
==================================

## What is TCT?
Translator Component Toolkit is a python library that allowing users to explore and use KGs in the Translator ecosystem.
Users can check out the key function documentations here: https://ncatstranslator.github.io/Translator_component_toolkit/ 

## Key features for TCT
Allowing users to select APIs, predicates according to the user's intention. <br>
Parallel and fast quering of the selected APIs.<br>
Providing reproducible results by setting contraints.<br>
Allowing testing whether a user defined API follows a [TRAPI](https://github.com/NCATSTranslator/ReasonerAPI) standard or not. <br>
Faciliting to explore knowledge graphs from both Translator ecosystem and user defined APIs.<br>
Connecting large language models to convert user's questions into TRAPI queries. <br>

## How to use TCT
### Install Requirments

To install TCT as a python library, you can install the library using `pip install TCT` from the command line. The current released version is TCT.0.1.0. This the recommended approach for installation. 

The TCT is continuously updated, if you would like to use the latest functions, you can also  clone this repository, and then run `pip install -e .` from this folder.


### Please follow the example notebooks (four utilities) below to explore the Translator APIs.

#### KG overview
Explore different KGs **[KG overview](./notebooks/overview_of_KGs.ipynb)**

#### Connection finder
Example notebook for **[ConnectionFinder](./notebooks/Connection_finder.ipynb)**

#### Path finder
Example notebook for **[PathFinder](./notebooks/Path_finder.ipynb)**

#### Network finder
Example notebook for **[NetworkFinder](./notebooks/Network_finder.ipynb)**

#### Translate users' questions into TRAPI queries
Example notebook for translating users' questions into TRAPI queries can be found [here](./notebooks/Question2Query_chatGPT.ipynb). 

#### Connecting to a user's API
API should be developed following the standard from [TRAPI](https://github.com/NCATSTranslator/ReasonerAPI). <br>
An example notebook for add a user's API can be found [here](./notebooks/Connecting_userAPI.ipynb).<br>
**Warning: It does not work if no user' API is established**<br>

## Key Translator components
Connecting to key Translator components can be found [here](./TranslatorComponentsIntroduction.md)

### Contributing
TCT is a tool that helps to explore knowledge graphs developed in the Biomedical Data Translator Consortium. Consortium members and external contributors are encouraged to submit issues and pull requests. 

### Contact info
Guangrong Qin, guangrong.qin@isbscience.org