## Requirements
- Docker
- Directory with rdf files


## Installation
```
git clone git@github.com:BONSAMURAIS/rdfexplorer.git
cd rdfexplorer
docker build -t rdfexplorer .
```

## Run instructions
###ontology.bonsai.uno
```
docker run --rm --name ontology \
        --volume ontology_data:/rdf_data \
        --env DOMAIN_NAME=http://ontology.bonsai.uno
        -p 5001:5000 rdfexplorer
```
###rdf.bonsai.uno
```
docker run --rm --name rdf \
        --volume rdf_data:/rdf_data \
        --env DOMAIN_NAME=http://rdf.bonsai.uno
        -p 5002:5000 rdfexplorer
```
