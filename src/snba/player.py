import os
import streamlit as st

from dotenv import load_dotenv
from pymongo import MongoClient
from gridfs import GridFS


load_dotenv()

@st.cache_resource
def get_database():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["sports_db"]
    return db, GridFS(db)

db, fs = get_database()
players_collection = db["players"]
# ==================================================
# REGISTERED STUDENTS
# ==================================================

st.header("Registered Students")

students = players_collection.find(
    {},
    {
        "_id": 0,
        "name": 1,
    },
)

for student in students:
    st.write(student.get("name", "Unknown"))