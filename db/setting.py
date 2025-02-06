# -*- coding: utf-8 -*-
from dotenv import load_dotenv
import os

# DB操作用にsqlalchemyライブラリインポート
from sqlalchemy import create_engine
# DBの存在確認とDB作成を行うためにインポート
from sqlalchemy_utils import database_exists, create_database
# セッション定義用にインポート
from sqlalchemy.orm import sessionmaker, scoped_session

# モデル定義ファイルインポート
from db.models import Base

load_dotenv()

DATABASE = {
    'drivername': 'mysql+pymysql',
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get("DB_PORT", "3306"),
    'username': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME'),
}

DATABASE_URL = (
    f"{DATABASE['drivername']}://{DATABASE['username']}:{DATABASE['password']}@"
    f"{DATABASE['host']}:{DATABASE['port']}/{DATABASE['database']}?charset=utf8mb4"
)

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# session変数にsessionmakerインスタンスを格納
session = scoped_session(
    # ORマッパーの設定。自動コミットと自動反映はオフにする
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)
# DBが存在しなければ
if not database_exists(engine.url):
    # DBを新規作成する
    create_database(engine.url)

# 定義されているテーブルを一括作成
Base.metadata.create_all(bind=engine)

# DB接続用のセッションクラス、インスタンスが作成されると接続する
Base.query = session.query_property()
