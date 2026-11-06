
import os
import streamlit as st

from datetime import datetime, date
from dotenv import load_dotenv
from pymongo import MongoClient
from gridfs import GridFS

load_dotenv()

# ==================================================
# DATABASE
# ==================================================

@st.cache_resource
def get_database():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["sports_db"]
    return db, GridFS(db)


db, fs = get_database()
players_collection = db["players"]

ADMIN_PASSKEY = os.getenv("ADMIN_PASSKEY") or os.getenv("DELETE_PASSKEY")

# ==================================================
# PAGE
# ==================================================

st.title("Registered Students")
st.caption("View and manage student registrations")

students = list(
    players_collection.find(
        {},
        {"_id": 0}
    )
)

if not students:
    st.info("No registered students found.")

# ==================================================
# STUDENT LIST
# ==================================================

for student in students:

    student_id = student["student_id"]
    student_name = student.get("name", "Unknown")

    # Session state
    details_key = f"details_{student_id}"
    unlocked_key = f"unlocked_{student_id}"

    if details_key not in st.session_state:
        st.session_state[details_key] = False

    if unlocked_key not in st.session_state:
        st.session_state[unlocked_key] = False

    st.markdown("---")

    # Show only name initially
    col1, col2 = st.columns([4, 1])

    with col1:
        st.subheader(student_name)

    with col2:

        if st.button(
            "Get Details",
            key=f"details_button_{student_id}",
            use_container_width=True,
        ):
            st.session_state[details_key] = (
                not st.session_state[details_key]
            )
            st.rerun()

    # ==================================================
    # STUDENT DETAILS
    # ==================================================

    if st.session_state[details_key]:

        with st.container(border=True):

            st.markdown("### Student Details")

            st.write("**Student ID:**", student_id)
            st.write("**Name:**", student_name)
            st.write("**Gender:**", student.get("gender", ""))

            dob = student.get("dob")

            if isinstance(dob, datetime):
                st.write("**Date of Birth:**", dob.date())
            elif isinstance(dob, date):
                st.write("**Date of Birth:**", dob)

            # Student photograph
            photo_file_id = student.get("photo_file_id")

            if photo_file_id:

                try:
                    photo_data = fs.get(photo_file_id).read()

                    st.image(
                        photo_data,
                        caption=student_name,
                        width=180,
                    )

                except Exception:
                    st.warning("Student photograph unavailable.")

            # ==================================================
            # ACHIEVEMENTS
            # ==================================================

            st.markdown("### Sports Achievements")

            achievements = student.get("achievements", [])

            if not achievements:

                st.info("No achievements registered.")

            for index, achievement in enumerate(achievements, 1):

                st.markdown(f"#### Achievement {index}")

                st.write(
                    "**Organization:**",
                    achievement.get("organization", "")
                )

                st.write(
                    "**Category:**",
                    achievement.get("category", "")
                )

                st.write(
                    "**Gender Category:**",
                    achievement.get("gender_category", "")
                )

                st.write(
                    "**Competition Level:**",
                    achievement.get("level", "")
                )

                st.write(
                    "**Result:**",
                    achievement.get("result", "")
                )

                st.write(
                    "**Competition:**",
                    achievement.get("competition", "")
                )

                st.write(
                    "**Year:**",
                    achievement.get("year", "")
                )

                st.divider()

            # ==================================================
            # ADMIN ACCESS
            # ==================================================

            st.markdown("### Admin Actions")

            if not st.session_state[unlocked_key]:

                passkey = st.text_input(
                    "Enter Admin Secret Key",
                    type="password",
                    key=f"admin_passkey_{student_id}",
                )

                if st.button(
                    "Unlock Actions",
                    key=f"unlock_{student_id}",
                ):

                    if not ADMIN_PASSKEY:

                        st.error(
                            "ADMIN_PASSKEY is not configured."
                        )

                    elif passkey == ADMIN_PASSKEY:

                        st.session_state[unlocked_key] = True

                        st.success("Admin access granted.")

                        st.rerun()

                    else:

                        st.error("Incorrect secret key.")

            # ==================================================
            # EDIT / DELETE
            # ==================================================

            if st.session_state[unlocked_key]:

                st.success("Admin actions unlocked.")

                if st.button(
                    "Lock Actions",
                    key=f"lock_{student_id}",
                ):

                    st.session_state[unlocked_key] = False
                    st.rerun()

                # ----------------------------------------------
                # EDIT STUDENT
                # ----------------------------------------------

                with st.expander("✏️ Edit Student Details"):

                    current_dob = student.get("dob")

                    if isinstance(current_dob, datetime):
                        current_dob = current_dob.date()

                    if not isinstance(current_dob, date):
                        current_dob = date.today()

                    with st.form(
                        key=f"edit_student_{student_id}"
                    ):

                        updated_name = st.text_input(
                            "Student Name",
                            value=student.get("name", ""),
                        )

                        updated_gender = st.selectbox(
                            "Gender",
                            ["Male", "Female", "Other"],
                            index=[
                                "Male",
                                "Female",
                                "Other",
                            ].index(
                                student.get("gender", "Male")
                            )
                            if student.get("gender", "Male")
                            in ["Male", "Female", "Other"]
                            else 0,
                        )

                        updated_dob = st.date_input(
                            "Date of Birth",
                            value=current_dob,
                        )

                        st.markdown("### Edit Achievements")

                        updated_achievements = []

                        for i, achievement in enumerate(
                            achievements
                        ):

                            st.markdown(
                                f"#### Achievement {i + 1}"
                            )

                            organization = st.text_input(
                                "Organization",
                                value=achievement.get(
                                    "organization", ""
                                ),
                                key=f"org_edit_{student_id}_{i}",
                            )

                            category = st.text_input(
                                "Category",
                                value=achievement.get(
                                    "category", ""
                                ),
                                key=f"cat_edit_{student_id}_{i}",
                            )

                            gender_category = st.text_input(
                                "Gender Category",
                                value=achievement.get(
                                    "gender_category", ""
                                ),
                                key=f"gender_edit_{student_id}_{i}",
                            )

                            level = st.text_input(
                                "Competition Level",
                                value=achievement.get(
                                    "level", ""
                                ),
                                key=f"level_edit_{student_id}_{i}",
                            )

                            result = st.text_input(
                                "Result",
                                value=achievement.get(
                                    "result", ""
                                ),
                                key=f"result_edit_{student_id}_{i}",
                            )

                            competition = st.text_input(
                                "Competition",
                                value=achievement.get(
                                    "competition", ""
                                ),
                                key=f"competition_edit_{student_id}_{i}",
                            )

                            year = st.number_input(
                                "Year",
                                min_value=1900,
                                max_value=2100,
                                value=int(
                                    achievement.get(
                                        "year",
                                        datetime.now().year
                                    )
                                ),
                                key=f"year_edit_{student_id}_{i}",
                            )

                            updated_achievements.append({
                                "organization": organization,
                                "category": category,
                                "gender_category": gender_category,
                                "level": level,
                                "result": result,
                                "competition": competition,
                                "year": int(year),
                            })

                        if st.form_submit_button(
                            "Update Student"
                        ):

                            if not updated_name.strip():

                                st.error(
                                    "Student name cannot be empty."
                                )

                            else:

                                players_collection.update_one(
                                    {
                                        "student_id": student_id
                                    },
                                    {
                                        "$set": {
                                            "name": updated_name.strip(),
                                            "gender": updated_gender,
                                            "dob": datetime.combine(
                                                updated_dob,
                                                datetime.min.time()
                                            ),
                                            "achievements": (
                                                updated_achievements
                                            ),
                                        }
                                    },
                                )

                                st.success(
                                    "Student updated successfully!"
                                )

                                st.rerun()

                # ----------------------------------------------
                # DELETE ACHIEVEMENT
                # ----------------------------------------------

                with st.expander("🗑️ Delete Achievement"):

                    if achievements:

                        achievement_to_delete = st.selectbox(
                            "Select Achievement",
                            range(len(achievements)),
                            format_func=lambda i: (
                                f"Achievement {i + 1}: "
                                f"{achievements[i].get('competition', '')}"
                            ),
                            key=f"delete_achievement_select_{student_id}",
                        )

                        if st.button(
                            "Delete Selected Achievement",
                            key=f"delete_achievement_{student_id}",
                            type="secondary",
                        ):

                            updated_achievements = [
                                a for i, a in enumerate(achievements)
                                if i != achievement_to_delete
                            ]

                            players_collection.update_one(
                                {"student_id": student_id},
                                {
                                    "$set": {
                                        "achievements": (
                                            updated_achievements
                                        )
                                    }
                                },
                            )

                            st.success(
                                "Achievement deleted successfully!"
                            )

                            st.rerun()

                    else:

                        st.info("No achievements to delete.")

                # ----------------------------------------------
                # DELETE STUDENT
                # ----------------------------------------------

                with st.expander("⚠️ Delete Entire Student"):

                    st.warning(
                        "This permanently deletes the student "
                        "and all registered achievements."
                    )

                    confirm_delete = st.checkbox(
                        "I confirm that I want to delete this student.",
                        key=f"confirm_delete_{student_id}",
                    )

                    if st.button(
                        "Delete Student Permanently",
                        key=f"delete_student_{student_id}",
                        type="primary",
                    ):

                        if confirm_delete:

                            players_collection.delete_one(
                                {"student_id": student_id}
                            )

                            st.session_state.pop(
                                details_key, None
                            )

                            st.session_state.pop(
                                unlocked_key, None
                            )

                            st.success(
                                "Student deleted successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Please confirm before deleting."
                            )
