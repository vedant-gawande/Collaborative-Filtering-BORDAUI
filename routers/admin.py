from fastapi import APIRouter


router = APIRouter(
    prefix='/admin_'
)

@router.post('login')
def login():
    pass