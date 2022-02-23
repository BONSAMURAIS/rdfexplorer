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
    query = None

    # Check if the url is a graph
    is_graph_query = f'ASK WHERE {{ GRAPH <{domain_name}/{req_path}> {{ ?s ?p ?o }} }}'
    is_graph_response = get(url, params=get_graph_params(is_graph_query, 'text/json'))

    if is_graph_response.ok and is_graph_response.json() is True:
        query = f'CONSTRUCT {{ ?s ?p ?o}} WHERE {{ GRAPH <{domain_name}/{req_path}>{{?s ?p ?o }} }}'
    else:
        # Check if the url is a value
        is_value_query = f'ASK WHERE {{ VALUES ?s {{ <{domain_name}/{req_path}>}} ?s ?p ?o }}'
        is_value_response = get(url, params=get_graph_params(is_value_query, 'text/json'))

        if is_value_response.ok and is_value_response.json() is True:
            query = f'SELECT * WHERE {{ VALUES ?s {{ <{domain_name}/{req_path}>}} ?s ?p ?o }}'

    # Return 404 if nothing matches
    if query is None:
        return abort(404)

    # Run graph or node query
    sparql_response = get(url, params=get_graph_params(query, request.accept_mimetypes.to_header()))
    if sparql_response.ok:
        return sparql_response.content

    return abort(404)


def get_graph_params(query, format):
    return {
        'default-graph-uri': '',
        'query': query,
        'format': f'{format}',
        'timeout': 0,
        'debug': 'on',
        'run': 'Run Query'
    }
