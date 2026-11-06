import os
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

@st.cache_resource
def get_database():
    client = MongoClient(os.getenv("MONGO_URI"))
    return client["sports_db"]

db = get_database()
players_collection = db["players"]

DELETE_PASSKEY = os.getenv("DELETE_PASSKEY")

# Registered achievements table and delete logic below
# ==================================================
# REGISTERED ACHIEVEMENTS WITH DELETE
# ==================================================

DELETE_PASSKEY = os.getenv("DELETE_PASSKEY")

st.header("Registered Achievements")

students = players_collection.find(
    {},
    {
        "_id": 0,
        "student_id": 1,
        "name": 1,
        "achievements": 1,
    },
)

header = st.columns([3, 2, 2, 2, 2])

header[0].markdown("**Student**")
header[1].markdown("**Competition**")
header[2].markdown("**Level**")
header[3].markdown("**Year**")
header[4].markdown("**Delete**")

st.divider()

found = False

for student in students:

    student_id = student["student_id"]
    student_name = student.get("name", "")

    for index, achievement in enumerate(
        student.get("achievements", [])
    ):

        found = True

        row = st.columns([3, 2, 2, 2, 2])

        row[0].write(student_name)
        row[1].write(achievement.get("competition", ""))
        row[2].write(achievement.get("level", ""))
        row[3].write(achievement.get("year", ""))

        with row[4]:

            with st.popover("🗑️ Delete"):

                passkey = st.text_input(
                    "Enter passkey",
                    type="password",
                    key=f"passkey_{student_id}_{index}",
                )

                if st.button(
                    "Confirm Delete",
                    key=f"delete_{student_id}_{index}",
                    type="primary",
                ):

                    if not DELETE_PASSKEY:
                        st.error("Passkey is not configured.")

                    elif passkey == DELETE_PASSKEY:

                        # Remove achievement from embedded array
                        players_collection.update_one(
                            {"student_id": student_id},
                            {
                                "$unset": {
                                    f"achievements.{index}": ""
                                }
                            },
                        )

                        # Remove null array element
                        players_collection.update_one(
                            {"student_id": student_id},
                            {
                                "$pull": {
                                    "achievements": None
                                }
                            },
                        )

                        st.success("Achievement deleted!")
                        st.rerun()

                    else:
                        st.error("Incorrect passkey.")

if not found:
    st.info("No registered achievements found.")