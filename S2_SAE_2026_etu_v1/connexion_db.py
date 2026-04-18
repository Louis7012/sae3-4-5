#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import g
import pymysql.cursors

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = pymysql.connect(
            host="localhost",
            user="rpeig",
            password="secret",
            database="s2_BDD",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    return db
