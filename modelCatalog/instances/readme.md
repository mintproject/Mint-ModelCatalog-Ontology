#Model catalog: Population and linking

This repository contains the resources necessary to populate and curate the model catalog.

Explain the organization of the Data folder

Explain the code organization in the repository


1) Extract units from labels and connect to WikiData: 
    
    You need to have access to the CCUT repository with the docker file: https://github.com/usc-isi-i2/mint-data-catalog/tree/ccut-dev
    
    1. clone the mint-data-catalog github repository 
    2. (move to ccut_docker branch)
    3. cd to ccut_docker
    4. build image
        docker build -t ccut_docker .
    5. run image (a flask server)
        docker run -d -p 5000:5000 ccut_docker run -h 0.0.0.0 -p 5000
    6. cd UnitToRDF (folder in this repository)
    7. run the following query:
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX mc: <https://w3id.org/mint/modelCatalog#>
    PREFIX dc: <http://purl.org/dc/terms/>

    SELECT distinct ?units where {
        ?a mc:usesUnit ?u.
        ?u rdfs:label ?units
    }
    On https://endpoint.mint.isi.edu/dataset.html?tab=query&ds=/provenance and download the results as JSON in the /run folder replacing "Units.ttl"
    7. Run python UnitToRDF. This is an interactive process where the program will ask the user in case of ambiguous terms.
    
2) Generate Scientific Variable Links.
    Summarize main points here
    TBD
    
3) Ongoing: Container descriptions
    
4) Ongoing: layout description files

