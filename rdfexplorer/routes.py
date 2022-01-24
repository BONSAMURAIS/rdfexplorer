import os
from pathlib import Path

from flask import Blueprint, abort, send_file, render_template, request, current_app
from requests import get

bp = Blueprint('routes', __name__, )


@bp.route('/', defaults={'req_path': ''})
@bp.route('/<path:req_path>')
def dir_listing(req_path):
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

    # Try to run query
    query = f'select * where {{ VALUES ?s {{ <http://rdf.bonsai.uno/{req_path}>}} ?s ?p ?o }}'

    url = f'{current_app.config["SPARQL_HOST"]}/sparql'
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
