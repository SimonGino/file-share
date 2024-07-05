# api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.auth import authenticate_user, create_access_token
from app.schemas import UserCreate, User as UserSchema
from app.crud.user import create_user, get_user_by_username
from app.storages.database import get_db

router = APIRouter()

@router.post("/register/", response_model=UserSchema)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "status": "ok"}

@router.get("/currentUser")
def login_for_access_token():
    return {
      "success": "true",
      "data": {
        "name": 'Serati Ma',
        "avatar": 'https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png',
        "userid": '00000001',
        "email": 'antdesign@alipay.com',
        "signature": '海纳百川，有容乃大',
        "title": '交互专家',
        "group": '蚂蚁金服－某某某事业群－某某平台部－某某技术部－UED',
        "tags": [
          {
            "key": '0',
            "label": '很有想法的',
          },
          {
            "key": '1',
            "label": '专注设计',
          },
          {
            "key": '2',
            "label": '辣~',
          },
          {
            "key": '3',
            "label": '大长腿',
          },
          {
            "key": '4',
            "label": '川妹子',
          },
          {
            "key": '5',
            "label": '海纳百川',
          },
        ],
        'notifyCount': 12,
        "unreadCount": 11,
        "country": 'China',
        "access": {},
        "geographic": {
          "province": {
            "label": '浙江省',
            "key": '330000',
          },
          "city": {
            "label": '杭州市',
            "key": '330100',
          },
        },
        "address": '西湖区工专路 77 号',
        "phone": '0752-268888888',
      },
    }