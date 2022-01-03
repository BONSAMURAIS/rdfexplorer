import os
from pathlib import Path

from flask import Blueprint, abort, send_file, render_template, request, current_app

bp = Blueprint('routes', __name__, )


@bp.route('/', defaults={'req_path': ''})
@bp.route('/<path:req_path>')
def dir_listing(req_path):
    base_dir = Path(current_app.config['RDF_DATA_DIR'])

    # Joining the base and the requested path
    abs_path = base_dir / req_path

    # Return 404 if path doesn't exist
    if not abs_path.exists():
        return abort(404)

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

    # Show directory contents
    current_path = Path(req_path)
    parent = '/' + str(current_path.parent)
    files = os.listdir(abs_path)
    return render_template('files.html', files=files, parent=parent)
