import os
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import PyMongoError


class MongoStore:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
        self.database_name = os.getenv("MONGO_DB", "caseworker_morning")
        self.client = None
        self.db = None
        self.error = None
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=1500)
            self.client.admin.command("ping")
            self.db = self.client[self.database_name]
        except PyMongoError as error:
            self.error = str(error)

    @property
    def connected(self):
        return self.db is not None

    def seed_or_load(self, cases, residents, documents, eligibility, certificates):
        if not self.connected:
            return
        if self.db.cases.count_documents({}) == 0:
            if cases:
                self.db.cases.insert_many([dict(case) for case in cases])
            if residents:
                self.db.residents.insert_many([{"resident_id": key, **value} for key, value in residents.items()])
            if documents:
                self.db.documents.insert_many([{"case_id": key, **value} for key, value in documents.items()])
            if eligibility:
                self.db.eligibility.insert_many([{"case_id": key, **value} for key, value in eligibility.items()])
            if certificates:
                self.db.certificates.insert_many([{"case_id": key, **value} for key, value in certificates.items()])
            return
        cases[:] = self._without_id(self.db.cases.find())
        residents.clear()
        residents.update({item["resident_id"]: self._without_keys(item, "resident_id") for item in self.db.residents.find()})
        documents.clear()
        documents.update({item["case_id"]: self._without_keys(item, "case_id") for item in self.db.documents.find()})
        eligibility.clear()
        eligibility.update({item["case_id"]: self._without_keys(item, "case_id") for item in self.db.eligibility.find()})
        certificates.clear()
        certificates.update({item["case_id"]: self._without_keys(item, "case_id") for item in self.db.certificates.find()})

    def log(self, event):
        if self.connected:
            self.db.audit_logs.insert_one(dict(event))

    def save_case(self, case):
        if self.connected:
            self.db.cases.replace_one({"case_id": case["case_id"]}, dict(case), upsert=True)

    def save_resident(self, resident_id, resident):
        if self.connected:
            self.db.residents.replace_one({"resident_id": resident_id}, {"resident_id": resident_id, **resident}, upsert=True)

    def save_documents(self, case_id, documents):
        if self.connected:
            self.db.documents.replace_one({"case_id": case_id}, {"case_id": case_id, **documents}, upsert=True)

    def save_eligibility(self, case_id, result):
        if self.connected:
            self.db.eligibility.replace_one({"case_id": case_id}, {"case_id": case_id, **result}, upsert=True)

    def save_certificate(self, case_id, certificate):
        if self.connected:
            self.db.certificates.replace_one({"case_id": case_id}, {"case_id": case_id, **certificate}, upsert=True)

    @staticmethod
    def _without_id(items):
        return [MongoStore._without_keys(item) for item in items]

    @staticmethod
    def _without_keys(item, *keys):
        return {key: value for key, value in item.items() if key != "_id" and key not in keys}


store = MongoStore()
