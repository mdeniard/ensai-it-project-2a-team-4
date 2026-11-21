import os
from typing import Literal, Optional, Union

import psycopg2
from psycopg2.extras import RealDictCursor


class DBConnector:
    """Connection to the PostgreSQL database: sends the SQL queries of the repositories."""

    def __init__(self, config=None):
        """Create the connector.
        Args:
            config (dict, optional): The connection settings, with the keys host, port, database,
                user, password, schema and timezone. If none is given, the settings are read
                from the environment variables of the .env file (POSTGRES_HOST, POSTGRES_PORT,
                POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_SCHEMA and,
                optionally, POSTGRES_TIMEZONE which is "Europe/Paris" by default).
        """
        if config is not None:
            self.host = config["host"]
            self.port = config["port"]
            self.database = config["database"]
            self.user = config["user"]
            self.password = config["password"]
            self.schema = config["schema"]
            self.timezone = config["timezone"]
        else:
            self.host = os.environ["POSTGRES_HOST"]
            self.port = os.environ["POSTGRES_PORT"]
            self.database = os.environ["POSTGRES_DATABASE"]
            self.user = os.environ["POSTGRES_USER"]
            self.password = os.environ["POSTGRES_PASSWORD"]
            self.schema = os.environ["POSTGRES_SCHEMA"]
            self.timezone = os.environ.get("POSTGRES_TIMEZONE", "Europe/Paris")

    def sql_query(
        self,
        query: str,
        data: Optional[Union[tuple, list, dict]] = None,
        return_type: Union[Literal["one"], Literal["all"]] = "one",
    ):
        """Run an SQL query on the configured schema and return its result.
        Each call opens its own connection, and the changes are saved (committed) at the end of the call.
        Args:
            query (str): The SQL query. The values are not written in it, they are given
                with data and marked by %s or %(name)s, which protects against SQL injection.
            data (tuple, list or dict, optional): The values of the query, a list or tuple
                for %s markers or a dict for %(name)s markers.
            return_type (str): "one" to get only the first row, "all" to get every row (default "one").
        Returns:
            With "one": the first row as a dict (column name: value), or None if the query returns no row.
            With "all": the list of all the rows, each one as a dict (an empty list if there is no row).
        """
        try:
            with psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                options=f"-c search_path={self.schema} -c timezone={self.timezone}",
                cursor_factory=RealDictCursor,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, data)
                    if return_type == "one":
                        return cursor.fetchone()
                    if return_type == "all":
                        return cursor.fetchall()
        except Exception as e:
            print("ERROR")
            print(e)
            raise e
