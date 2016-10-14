import requests

from .tasks import Task

DEFAULT_FIELDS = {'callback_url', 'instruction', 'urgency', 'metadata'}
ALLOWED_FIELDS = {'categorization': {'attachment', 'attachment_type', 'categories',
                                     'category_ids', 'allow_multiple'},
                  'transcription': {'attachment', 'attachment_type',
                                    'fields', 'row_fields'},
                  'phonecall': {'attachment', 'attachment_type', 'phone_number',
                                'script', 'entity_name', 'fields', 'choices'},
                  'comparison': {'attachments', 'attachment_type',
                                 'fields', 'choices'},
                  'annotation': {'attachment', 'attachment_type', 'instruction',
                                 'objects_to_annotate', 'with_labels'}}


def validate_payload(task_type, kwargs):
    allowed_fields = DEFAULT_FIELDS + ALLOWED_FIELDS[task_type]
    for k in kwargs:
        if k not in allowed_fields:
            raise ScaleInvalidRequest('Illegal parameter %s for task_type %s'
                                      % (k, task_type), None)


class ScaleException(Exception):
    def __init__(self, message, errcode):
        super(ScaleException, self).__init__(message)
        self.code = errcode


class ScaleInvalidRequest(ScaleException, ValueError):
    pass


class ScaleClient(object):
    def __init__(self, api_key, endpoint='https://api.scaleapi.com/v1/'):
        self.api_key = api_key
        self.endpoint = endpoint

    def _getrequest(self, endpoint):
        """Makes a get request to an endpoint.

        If an error occurs, assumes that endpoint returns JSON as:
            { 'status_code': XXX,
              'error': 'I failed' }
        """
        r = requests.get(self.endpoint + endpoint,
                         headers={"Content-Type": "application/json"},
                         auth=(self.api_key, ''))

        if r.status_code == 200:
            return r.json()
        raise ScaleException(r.json()['error'], r.status_code)

    def _postrequest(self, endpoint, payload=None):
        """Makes a post request to an endpoint.

        If an error occurs, assumes that endpoint returns JSON as:
            { 'status_code': XXX,
              'error': 'I failed' }
        """
        payload = payload or {}
        r = requests.post(self.endpoint + endpoint, json=payload,
                          headers={"Content-Type": "application/json"},
                          auth=(self.api_key, ''))

        if r.status_code == 200:
            return r.json()
        if r.status_code == 400:
            raise ScaleInvalidRequest(r.json()['error'], r.status_code)
        raise ScaleException(r.json()['error'], r.status_code)

    def fetch_task(self, task_id):
        """Fetches a task.

        Returns the associated task.
        """
        return Task(self._getrequest('task/%s' % task_id), self)

    def cancel_task(self, task_id):
        """Cancels a task.

        Returns the associated task.
        Raises a ScaleException if it has already been canceled.
        """
        return Task(self._postrequest('task/%s/cancel' % task_id), self)

    def tasks(self):
        """Returns a list of all your tasks."""
        return [Task(json, self) for json in self._getrequest('tasks')]

    def create_categorization_task(self, **kwargs):
        validate_payload('categorization', kwargs)
        taskdata = self._postrequest('task/categorize', payload=kwargs)
        return Task(taskdata, self)

    def create_transcription_task(self, **kwargs):
        validate_payload('transcription', kwargs)
        taskdata = self._postrequest('task/transcription', payload=kwargs)
        return Task(taskdata, self)

    def create_phonecall_task(self, **kwargs):
        validate_payload('phonecall', kwargs)
        taskdata = self._postrequest('task/phonecall', payload=kwargs)
        return Task(taskdata, self)

    def create_comparison_task(self, **kwargs):
        validate_payload('comparison', kwargs)
        taskdata = self._postrequest('task/comparison', payload=kwargs)
        return Task(taskdata, self)

    def create_annotation_task(self, **kwargs):
        validate_payload('annotation', kwargs)
        taskdata = self._postrequest('task/annotation', payload=kwargs)
        return Task(taskdata, self)