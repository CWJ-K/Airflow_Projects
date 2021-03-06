import requests

from airflow.hooks.base_hook import BaseHook


class MovielensHook(BaseHook):
    '''
    Hook for the MovieLens API

    Parameters
    -----------
    conn_id: str
        ID of the connection is used to connect to the Movielens API.
        Connection is expected to include authentication details (login/password) 
        and the host serving the API
    config.login:
        Username. It can be seen in Airflow UI.
    '''
    DEFAULT_SCHEMA = 'http'
    DEFAULT_PORT = 5000

    def __init__(self, conn_id, retry=3):
        super().__init__()
        self._conn_id = conn_id
        self._retry = retry

        self._session = None
        self._base_url = None

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


    def get_conn(self):
        if self._session is None:
            config = self.get_connection(self._conn_id)
            
            if not config.host:
                raise ValueError(f'No host specified in connection {self._conn_id}')
            
            schema = config.schema or self.DEFAULT_SCHEMA
            port = config.port or self.DEFAULT_PORT

            self._base_url = f'{schema}://{config.host}:{port}'

            self.session = requests.Session()

            if config.login:
                self._session.auth = (config.login, config.password)

        return self._session, self._base_url 


    def close(self):
        if self._session:
            self._session.close()
        self.session = None
        self._base_url = None

    # API methods:

    def get_movies(self):
        """Fetches a list of movies."""
        raise NotImplementedError()

    def get_users(self):
        """Fetches a list of users."""
        raise NotImplementedError()

    def get_ratings(self, start_date=None, end_date=None, batch_size=100):
        """
        Fetches ratings between the given start/end date.

        Parameters
        ----------
        start_date : str
            Start date to start fetching ratings from (inclusive). Expected
            format is YYYY-MM-DD (equal to Airflow's ds formats).
        end_date : str
            End date to fetching ratings up to (exclusive). Expected
            format is YYYY-MM-DD (equal to Airflow's ds formats).
        batch_size : int
            Size of the batches (pages) to fetch from the API. Larger values
            mean less requests, but more data transferred per request.
        """

        yield from self._get_with_pagination(
            endpoint='/ratings',
            params={'start_date': start_date, 'end_date': end_date},
            batch_size=batch_size
        )


    def _get_with_pagination(self, endpoint, params, batch_size=100):
        session, base_url = self.get_conn()
        url = base_url + endpoint

        offset = 0
        total = None
        while total is None or offset < total:
            response = session.get(
                url, params={**params, **{'offset': offset, 'limit': batch_size}}
            )
            response.raise_for_status()
            response_json = response.json()

            yield from response_json['result']
            
            offset += batch_size
            total = response_json['total']



    

    



