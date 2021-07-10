from rest_framework import renderers
from rest_framework.status import is_client_error, is_server_error


class Renderer(renderers.JSONRenderer):

    def render(self, data, media_type=None, renderer_context=None):
        success = True if 200 <= renderer_context['response'].status_code < 300 else False
        error_messages = []
        if not success:
            if isinstance(data, dict):
                for val in data.values():
                    if isinstance(val, (list, tuple)):
                        for v in val:
                            error_messages.append(v)
                    else:
                        error_messages.append(val)
            elif isinstance(data, (list, tuple)):
                for d in data:
                    if isinstance(d, dict):
                        for val in d.values():
                            if isinstance(val, (list, tuple)):
                                for v in val:
                                    error_messages.append(v)
                            else:
                                error_messages.append(val)
                    else:
                        error_messages.append(d)
            else:
                error_messages.append(data)

        resp = {
            'success': success,
            'data': data if success else '',
            'error_messages': error_messages
        }
        return super(Renderer, self).render(resp, media_type, renderer_context)

