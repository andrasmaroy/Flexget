from flask.helpers import send_file
from flask_restplus import inputs
from requests import RequestException

from flexget.api import api, APIResource
from flexget.api.app import APIError, BadRequest
from flexget.utils.cache import cached_resource

cached_api = api.namespace('cached', description='Cache remote resources')

cached_parser = api.parser()
cached_parser.add_argument('url', required=True, help='URL to cache')
cached_parser.add_argument('force', type=inputs.boolean, default=False, help='Force fetching remote resource')


@cached_api.route('/')
@api.doc(description='Returns a cached copy of the requested resource, matching its mime type')
class CachedResource(APIResource):
    @api.response(200, description='Cached resource')
    @api.response(BadRequest)
    @api.response(APIError)
    @api.doc(parser=cached_parser)
    def get(self, session=None):
        """ Cache remote resources """
        args = cached_parser.parse_args()
        url = args.get('url')
        force = args.get('force')
        try:
            file_path, mime_type = cached_resource(url, self.manager.config_base, force=force)
        except RequestException as e:
            raise BadRequest(f'Request Error: {e}')
        except OSError as e:
            raise APIError(f'Error: {e}')
        return send_file(file_path, mimetype=mime_type)
