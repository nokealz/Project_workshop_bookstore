import uvicorn
from fastapi import FastAPI, Path, Query, HTTPException
from starlette.responses import JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from database.mongodb import MongoDB
from config.development import config
from model.book import (
    createbookModel,
    updatebookModel,
    createcartModel,
    updatecartModel,
)

mongo_config = config["mongo_config"]
mongo_db = MongoDB(
    mongo_config["host"],
    mongo_config["port"],
    mongo_config["user"],
    mongo_config["password"],
    mongo_config["auth_db"],
    mongo_config["db"],
    mongo_config["collection"],
)
mongo_db._connect()

mongo_config_cart = config["mongo_config_cart"]
mongo_db_cart = MongoDB(
    mongo_config_cart["host"],
    mongo_config_cart["port"],
    mongo_config_cart["user"],
    mongo_config_cart["password"],
    mongo_config_cart["auth_db"],
    mongo_config_cart["db"],
    mongo_config_cart["collection"],
)
mongo_db_cart._connect()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return JSONResponse(content={"message": "book Info"}, status_code=200)


@app.get("/cart/{cart_id}/price/")
def calculate_price(cart_id: str = Path(None, min_length=3, max_length=3)):
    try:
        cart_result = mongo_db_cart.find_one(cart_id)
        results = mongo_db.find_list(cart_result["List"])
        price = 0
        for result in results:
            price += result["price"]

    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if result is None:
        raise HTTPException(status_code=404, detail="book Id not found !!")

    return JSONResponse(
        content={"status": "OK", "price": price},
        status_code=200,
    )


# createlist
@app.post("/cart")
def create_cart(cart: createcartModel):
    try:
        cart_id = mongo_db_cart.createcart(cart)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "cart_id": cart_id,
            },
        },
        status_code=201,
    )


# dele list
@app.delete("/cart/{cart_id}")
def delete_cart_by_id(cart_id: str = Path(None, min_length=3, max_length=3)):
    try:
        deleted_cart_id, deleted_count = mongo_db_cart.deletecart(cart_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if deleted_count == 0:
        raise HTTPException(
            status_code=404, detail=f"cart Id: {deleted_cart_id} is not Delete"
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "cart_id": deleted_cart_id,
                "deleted_count": deleted_count,
            },
        },
        status_code=200,
    )


# findallcart


@app.get("/cart/")
def get_cart(
    sort_by: Optional[str] = None,
    order: Optional[str] = Query(None, min_length=3, max_length=4),
):

    try:
        result = mongo_db_cart.find(sort_by, order)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


# find ID
@app.get("/cart/{cart_id}")
def get_book_by_id(cart_id: str = Path(None, min_length=3, max_length=3)):
    try:
        result = mongo_db_cart.find_one(cart_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if result is None:
        raise HTTPException(status_code=404, detail="book Id not found !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.get("/book/")
def get_book(
    sort_by: Optional[str] = None,
    order: Optional[str] = Query(None, min_length=3, max_length=4),
):

    try:
        result = mongo_db.find(sort_by, order)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.get("/book/{book_id}")
def get_book_by_id(book_id: str = Path(None, min_length=3, max_length=3)):
    try:
        result = mongo_db.find_one(book_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if result is None:
        raise HTTPException(status_code=404, detail="book Id not found !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.post("/book")
def create_book(book: createbookModel):
    try:
        book_id = mongo_db.create(book)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "book_id": book_id,
            },
        },
        status_code=201,
    )


@app.patch("/book/{book_id}")
def update_book(
    book: updatebookModel,
    book_id: str = Path(None, min_length=3, max_length=3),
):
    print("book", book)
    try:
        updated_book_id, modified_count = mongo_db.update(book_id, book)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"book Id: {updated_book_id} is not update want fields",
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "book_id": updated_book_id,
                "modified_count": modified_count,
            },
        },
        status_code=200,
    )


@app.delete("/book/{book_id}")
def delete_book_by_id(book_id: str = Path(None, min_length=3, max_length=3)):
    try:
        deleted_book_id, deleted_count = mongo_db.delete(book_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if deleted_count == 0:
        raise HTTPException(
            status_code=404, detail=f"book Id: {deleted_book_id} is not Delete"
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "book_id": deleted_book_id,
                "deleted_count": deleted_count,
            },
        },
        status_code=200,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3001, reload=True)
