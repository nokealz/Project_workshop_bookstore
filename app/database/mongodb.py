import pymongo

from model.book import (
    createbookModel,
    updatebookModel,
    createcartModel,
    updatecartModel,
)


class MongoDB:
    def __init__(self, host, port, user, password, auth_db, db, collection):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.auth_db = auth_db
        self.db = db
        self.collection = collection
        self.connection = None

    def _connect(self):
        client = pymongo.MongoClient(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            authSource=self.auth_db,
            authMechanism="SCRAM-SHA-1",
        )
        db = client[self.db]
        self.connection = db[self.collection]

    def find(self, sort_by, order):
        mongo_results = self.connection.find({})
        if sort_by is not None and order is not None:
            mongo_results.sort(sort_by, self._get_sort_by(order))

        return list(mongo_results)

    def find_list(self, array_list):
        mongo_results = self.connection.find({"_id": {"$in": array_list}})
        return list(mongo_results)

    def _get_sort_by(self, sort: str) -> int:
        return pymongo.DESCENDING if sort == "desc" else pymongo.ASCENDING

    def find_one(self, id):
        return self.connection.find_one({"_id": id})

    def createcart(self, cart: createcartModel):
        cart_dict = cart.dict(exclude_unset=True)

        insert_dict = {**cart_dict, "_id": cart_dict["id"]}

        inserted_result = self.connection.insert_one(insert_dict)
        cart_id = str(inserted_result.inserted_id)

        return cart_id

    def create(self, book: createbookModel):
        book_dict = book.dict(exclude_unset=True)

        insert_dict = {**book_dict, "_id": book_dict["id"]}

        inserted_result = self.connection.insert_one(insert_dict)
        book_id = str(inserted_result.inserted_id)

        return book_id

    def update(self, book_id, book: updatebookModel):
        updated_result = self.connection.update_one(
            {"id": book_id}, {"$set": book.dict(exclude_unset=True)}
        )
        return [book_id, updated_result.modified_count]

    def delete(self, book_id):
        deleted_result = self.connection.delete_one({"id": book_id})
        return [book_id, deleted_result.deleted_count]

    def deletecart(self, cart_id):
        deleted_result = self.connection.delete_one({"id": cart_id})
        return [cart_id, deleted_result.deleted_count]
