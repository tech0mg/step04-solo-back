from dotenv import load_dotenv
import os
from fastapi import FastAPI, Depends, Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
from db.setting import SessionLocal, DATABASE
from db.models import ProductMaster
from db.models import Transaction, TransactionDetail

# 作成したモデル定義ファイルと設定ファイルをインポート
import db.models as m
import db.setting as s

load_dotenv()

# データクラス定義
# POSTとPUTで使うデータクラス
class UserBase(BaseModel):
    name : str
    mail : str
    sex : str

class Product(BaseModel):
    prd_id: int
    code: str
    name: str
    price: int

app = FastAPI()

# ① CORS ミドルウェアの設定（フロントエンドのIPを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.environ.get('API_URL_01'),
        os.environ.get('API_URL_02')
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# DBセッション取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# データのスキーマを定義するためのクラス
class EchoMessage(BaseModel):
    message: str | None = None

@app.get("/")
def hello():
    return {"message": "FastAPI hello!"}

# 商品検索API
@app.get("/api/product")
def get_product(code: str, db: Session = Depends(get_db)):
    product = db.query(ProductMaster).filter(ProductMaster.code == code).first()
    if product is None:
        return {"error": "商品が見つかりません"}
    return {"prd_id":product.prd_id, "code": product.code, "name": product.name, "price": product.price}  

class TransactionRequest(BaseModel):
    total_amt: float
    emp_cd: int
    store_cd: int
    pos_no: int

# カート内の商品を購入
# ①取引情報の登録
@app.post("/api/transaction")
def save_transaction(transaction: TransactionRequest, db: Session = Depends(get_db)):
    try:
        new_transaction = Transaction(
            emp_cd=transaction.emp_cd,
            store_cd=transaction.store_cd,
            pos_no=transaction.pos_no,
            total_amt=transaction.total_amt
        )
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)

        return {"trd_id": new_transaction.trd_id}
    
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        return {"error": "Failed to save transaction"}, 500

    

# ②取引明細をDBに登録
@app.post("/api/transaction_details")
async def save_transaction_details(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    details = data["details"]

    try:
        for detail in details:
            new_detail = TransactionDetail(
                trd_id=detail["trd_id"],
                prd_id=detail["prd_id"],
                prd_code=detail["prd_code"],
                prd_name=detail["prd_name"],
                prd_price=detail["prd_price"]
            )
            db.add(new_detail)

        db.commit()

        return {"message": "Transaction details saved successfully!"}
    
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        return {"error": "Failed to save transaction details"}, 500
