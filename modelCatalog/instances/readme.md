TO DO: 
General readme instructions for populating model catalog as we have it.

Explain the organization of the Data folder

Explain the code organization in the repository


1) Generate units
    Summarize main points here
    (connects to Wikidata!)
    
    Assuming you have access to the repository: https://github.com/usc-isi-i2/mint-data-catalog/tree/ccut-dev
    
    1. clone the mint-data-catalog github repository
    2. (move to ccut_docker branch)
    3. cd to ccut_docker
    4. build image
    docker build -t ccut_docker .
    5. run image (a flask server)
    docker run -d -p 5000:5000 ccut_docker run -h 0.0.0.0 -p 5000

    6. cd UnitToRDF
    7. python UnitToRDF.
    
2) Generate SVOs
    Summarize main points here
    (connects to Wikidata!)
    
3) Ongoing: Container descriptions
    
4) Ongoing: layout description files

