FROM python:3.10.2-buster

# set work directory
ENV WD=/usr/src/app
WORKDIR ${WD}

# install dependencies
COPY requirements.txt ${WD}/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY rdfexplorer ${WD}/rdfexplorer
COPY app.py config.py ${WD}/

# Create the rdf data volume
VOLUME ["/rdf_data"]

# set Flask environment
ENV FLASK_APP app.py
ENV FLASK_ENV production
ENV RDF_DATA_DIR /rdf_data
ENV SPARQL_HOST http://new.odas.aau.dk

EXPOSE 5000/tcp

CMD ["gunicorn", "-w", "9", "--bind", "0.0.0.0:5000", "app:app", "--log-level=info"]
