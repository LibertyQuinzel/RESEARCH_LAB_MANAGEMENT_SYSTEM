import pytest
import types

import database

class DummyCursor:
    def __init__(self, should_fetch=None, fetch_result=None, raise_on_execute=False):
        self._should_fetch = should_fetch
        self._fetch_result = fetch_result or []
        self.raise_on_execute = raise_on_execute
        self.closed = False
    def execute(self, query, params=None):
        if self.raise_on_execute:
            raise Exception('execute failed')
    def fetchall(self):
        return self._fetch_result
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False

class DummyConn:
    def __init__(self, cursor_obj):
        self._cursor = cursor_obj
        self.committed = False
        self.rolled_back = False
        self.closed = False
    def cursor(self, cursor_factory=None):
        return self._cursor
    def commit(self):
        self.committed = True
    def rollback(self):
        self.rolled_back = True
    def close(self):
        self.closed = True


def test_execute_query_fetch_success(monkeypatch):
    cursor = DummyCursor(fetch_result=[{'a':1}])
    conn = DummyConn(cursor)
    monkeypatch.setattr(database.psycopg2, 'connect', lambda **k: conn)
    db = database.Database('db','u','p')
    res = db.execute_query('select 1', fetch=True)
    assert res == [{'a':1}]
    db.close()
    assert conn.closed


def test_execute_query_commit_success(monkeypatch):
    cursor = DummyCursor()
    conn = DummyConn(cursor)
    monkeypatch.setattr(database.psycopg2, 'connect', lambda **k: conn)
    db = database.Database('db','u','p')
    res = db.execute_query('update table', fetch=False)
    assert res is True
    assert conn.committed
    db.close()


def test_execute_query_raises_and_rolls_back(monkeypatch):
    cursor = DummyCursor(raise_on_execute=True)
    conn = DummyConn(cursor)
    monkeypatch.setattr(database.psycopg2, 'connect', lambda **k: conn)
    db = database.Database('db','u','p')
    with pytest.raises(Exception):
        db.execute_query('bad query', fetch=False)
    assert conn.rolled_back
    db.close()
