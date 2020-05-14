"""molecule.one API Interface

This is an attempt to make a python api for the [molecule.one](https://molecule.one) batch API
"""

import json
import urllib

from urllib.error import HTTPError
from urllib.request import Request

"""## Molecule.one API Interface"""

# URLS to use with molecule.one API
URL_SEARCH = "https://app.molecule.one/api/v1/batch-search"
URL_RESULT = "https://app.molecule.one/api/v1/batch-search-result"


class BatchError(HTTPError):
    pass


class BatchForbiddenError(BatchError):
    pass


class BatchUnauthorizedError(BatchError):
    pass


class Batch(object):
    """ The Batch base class of the molecule.one package """
    def __init__(self, api_key):
        self._api_key = api_key

    def api_key(self):
        return self._api_key


def query_http_api(url, api_key, data=None):
    """ Queries the molecule.one API with a HTTP request

        if data is present, it will automatically change the method to POST

        :param str url: the URL of the API to use
        :param str api_key: the API key to use
        :param data: string of encoded data to supply with the request
    """
    method = None
    if data is not None:
        method = "POST"
    
    R = Request(url,
                data = data,
                headers = {"Content-Type": "application/json",
                           "Authorization": "ApiToken-v1 {}".format(api_key),
                           "User-Agent": "curl/7.64.1"},
                method = method
    )
    try:
        with urllib.request.urlopen(R) as f:
            response = f.read().decode('utf-8')
    except urllib.request.HTTPError as e:
        if e.code == 401:
            raise BatchUnauthorizedError(e.url, e.code, e.msg, e.hdrs, e.fp)
        elif e.code == 403:
            raise BatchForbiddenError(e.url, e.code, e.msg, e.hdrs, e.fp)
        elif e.code == 500:
            raise BatchServerError(e.url, e.code, e.msg, e.hdrs, e.fp)
        else:
            raise
    else:
        return json.loads(response)


class BatchRequest(Batch):
    """ Submits a batch scoring request """
    def __init__(self, smiles, api_key):
        Batch.__init__(self, api_key)
        self._smiles = smiles[:]
        self._was_submitted = False
        self._batch = {}

    @classmethod
    def from_id(cls, id, api_key):
        br = cls([], api_key)
        br._was_submitted = True
        br._batch["id"] = id
        return br

    def add_smiles(self, smiles):
        self._smiles.extend(smiles)

    def _encode_smiles(self):
        smiles_string = "\", \"".join(self._smiles)
        return "{\"targets\": " + "[\"{}\"]".format(smiles_string) + "}"

    def submit(self):
        data = self._encode_smiles().encode('ascii')
        self._batch = query_http_api(URL_SEARCH, self.api_key(), data=data)
        self._was_submitted = True

    def get_id(self):
        if not self.was_submitted():
            raise ValueError("BatchRequest was not submitted.")

        if "id" not in self._batch:
            raise ValueError("BatchRequest error. Key 'id' not found in response.")
        return self._batch['id']

    def was_submitted(self):
        return self._was_submitted


class BatchStatus(Batch):
    """ Submits a batch status requests to get information about all jobs """
    def __init__(self, api_key):
        Batch.__init__(self, api_key)
        self._query = {}

    def query(self):
        self._query = query_http_api(URL_SEARCH, self.api_key())

    def get_job_ids(self):
        if "data" not in self._query:
            raise ValueError("No data in BatchStatus.")
        return [item["id"] for item in self._query["data"]]

    def get_num_jobs(self):
        if "total" not in self._query:
            raise ValueError("No data in BatchStatus.")
        return self._query["total"]

    def __str__(self):
        s = "Number of Jobs: {}\n".format(self.get_num_jobs())
        s += "\n".join(self.get_job_ids())
        return s


class BatchJobStatus(Batch):
    """ Submits a batch job status request for a single job """
    def __init__(self, batch_request, api_key):
        if not batch_request.was_submitted():
            raise ValueError("Invalid BatchRequest. Not submitted.")
        Batch.__init__(self, api_key)
        self._id = batch_request.get_id()
        self._has_queried = False
        self._query = self.query()

    def query(self):
        self._has_queried = False
        url = URL_SEARCH + "/{}".format(self._id)
        query = query_http_api(url, self.api_key())
        self._has_queried = True
        return query

    def get_num_finished(self):
        if not self._has_queried:
            self.query()
        return self._query['finished']

    def is_finished(self):
        if not self._has_queried:
            self.query()
        return self._query['running'] == 0 and self._query['queued'] == 0

    def has_errors(self):
        if not self._has_queried:
            self.query()
        return self._query['error'] > 0

    def __str__(self):
        s  = "id       : {}\n".format(self._id)
        s += "finished : {}\n".format(self._query['finished']) 
        s += "running  : {}\n".format(self._query['running'])
        s += "queued   : {}\n".format(self._query['queued'])
        s += "error    : {}\n".format(self._query['error'])
        return s


class BatchResult(Batch):
    def __init__(self, batch_request, api_key):
        Batch.__init__(self, api_key)
        self._id = batch_request.get_id()
        self._query = self.query()

        self._index = -1

    def query(self):
        url = URL_RESULT + "/{}".format(self._id)
        return query_http_api(url, self.api_key())

    def __iter__(self):
        return iter(self._query)

    def get(self):
        return self._query