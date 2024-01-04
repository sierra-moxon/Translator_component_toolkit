# Translator component toolkit (TCT)

## What is TCT?
Translator Component Toolkit is a python library and related jupyter notebooks allowing users to explore and use KGs in the Translator ecosystems. 

## Key features for TCT
Allowing users to select APIs, predicates according to the user's intention. <br>
Parallel and fast quering of the selected APIs.<br>
Providing reproducible results by setting contraints.<br>
Allowing testing whether a user defined API follows a [TRAPI](https://github.com/NCATSTranslator/ReasonerAPI) standard or not. <br>
Faciliting to explore knowledge graphs from both Translator ecosystem and user defined APIs.<br>
Connecting large language models to convert user's questions into TRAPI queries. <br>

## How to use TCT
### Install Requirments
Follow the **[requirements](./requirements.txt)** to be able to run all the notebooks.  
pip install -r requirements.txt

### Please follow the example notebooks (three utilities) below to explore the Translator APIs.

#### Connection finder
Example notebook for **[ConnectionFinder](./notebooks/Connecting_userAPI.ipynb)**

#### Path finder
Example notebook for **[PathFinder](./notebooks/Path_finder.ipynb)**

#### Network finder
Example notebook for **[NetworkFinder](./notebooks/Network_finder.ipynb)**

#### Translate users' questions into TRAPI queries
Example notebook for translating users' questions into TRAPI queries can be found [here](./notebooks/Question2Query_chatGPT.ipynb). 

#### Connecting to a user's API
API should be developed following the standard from [TRAPI](https://github.com/NCATSTranslator/ReasonerAPI). <br>
An example notebook for add a user's API can be find [here](./notebooks/Connecting_userAPI.ipynb).<br>
**Warning: It does not work if no user' API is established**<br>

## Contributing
TCT is a tool that helps to explore knowledge graphs developed in the Biomedical Data Translator Consortium. Consortium members and external contributors are encouraged to submit issues and pull requests. 

## Contact info
Guangrong Qin, gqin@isbscience.org