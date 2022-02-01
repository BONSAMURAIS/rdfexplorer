import os
from pathlib import Path

from flask import Blueprint, abort, send_file, render_template, request, current_app
from requests import get

bp = Blueprint('routes', __name__, )


@bp.route('/', defaults={'req_path': ''})
@bp.route('/<path:req_path>')
def file_query_or_dir(req_path):
    base_dir = Path(current_app.config['RDF_DATA_DIR'])

    # Joining the base and the requested path
    abs_path = base_dir / req_path

    # Find best media type (default 'text/turtle')
    best = request.accept_mimetypes.best_match(['text/turtle', 'application/rdf+xml'])

    mimetype_to_extension = {
        'text/turtle': 'ttl',
        'application/rdf+xml': 'rdf'
    }

    # Get files with specific extension in current directory
    files = sorted(abs_path.glob(f'*.{mimetype_to_extension[best]}'))

    if files:
        # Send the latest version of the file (last in alphanumeric order)
        return send_file(files[-1])

    # Check if path is a file and serve
    if abs_path.is_file():
        return send_file(abs_path)

    if abs_path.exists():
        # Show directory contents
        current_path = Path(req_path)
        parent = '/' + str(current_path.parent)
        files = os.listdir(abs_path)
        return render_template('files.html', files=files, parent=parent)

    url = f'{current_app.config["SPARQL_HOST"]}/sparql'
    domain_name = current_app.config['DOMAIN_NAME']

    # Check if the url is a graph
    is_graph_query = f'ASK WHERE {{ GRAPH <{domain_name}/{req_path}> {{ ?s ?p ?o }} }}'
    is_graph_data = {
        'default-graph-uri': '',
        'query': is_graph_query,
        'format': 'text/json',
        'timeout': 0,
        'debug': 'on',
        'run': 'Run Query'
    }
    is_graph_response = get(url, params=is_graph_data)
    if is_graph_response.ok and is_graph_response.content == 'true':
        query = f'SELECT * WHERE {{ GRAPH <{domain_name}/{req_path}>{{?s ?p ?o }} }}'
    else:
        query = f'SELECT * WHERE {{ VALUES ?s {{ <{domain_name}/{req_path}>}} ?s ?p ?o }}'
    
    # Run graph or node query
    data = {
        'default-graph-uri': '',
        'query': query,
        'format': 'text/html',
        'timeout': 0,
        'debug': 'on',
        'run': 'Run Query'
    }
    sparql_response = get(url, params=data)
    if sparql_response.ok:
        return sparql_response.content

    # Return 404 if nothing matches
    return abort(404)
