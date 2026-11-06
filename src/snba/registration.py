
import os
import uuid

from datetime import datetime, date

import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from gridfs import GridFS


# ==================================================
# CONFIGURATION
# ==================================================

load_dotenv()

st.set_page_config(
    page_title="SNBA Sports Achievement Registration",
    page_icon="🏆",
    layout="wide",
)

st.title("🏆SNBA Sports Achievement Registration")
st.caption("Student Registration and Achievement Management")


# ==================================================
# MONGODB CONNECTION
# ==================================================

@st.cache_resource
def get_database():

    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise ValueError("MONGO_URI not found in .env file")

    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=10000,
    )

    client.admin.command("ping")

    db = client["sports_db"]

    return db, GridFS(db)


try:
    db, fs = get_database()

    players_collection = db["players"]

    players_collection.create_index(
        "student_id",
        unique=True,
    )

except Exception as e:
    st.error(f"MongoDB connection failed: {e}")
    st.stop()


# ==================================================
# CATEGORY CONFIGURATION
# ==================================================

CATEGORY_OPTIONS = {
    "SGF": ["Youth", "Mini", "Juniors"],
    "BFI": ["Youth", "Mini", "Juniors", "Seniors"],
    "University Games": ["University"],
    "Other": ["Other"],
}

GENDER_OPTIONS = {
    "SGF": ["Boys", "Girls"],
    "BFI": ["Men", "Women"],
    "University Games": ["Men", "Women"],
    "Other": ["Boys", "Girls", "Men", "Women"],
}

LEVEL_OPTIONS = [
    "State",
    "National",
    "South Zone University Games",
]

RESULT_OPTIONS = [
    "First",
    "Second",
    "Third",
    "Participation",
]


# ==================================================
# SESSION STATE
# ==================================================

if "achievements" not in st.session_state:
    st.session_state.achievements = [0]

if "next_achievement_id" not in st.session_state:
    st.session_state.next_achievement_id = 1


def add_achievement():

    new_id = st.session_state.next_achievement_id

    st.session_state.achievements.append(new_id)

    st.session_state.next_achievement_id += 1


def remove_achievement(achievement_id):

    st.session_state.achievements.remove(
        achievement_id
    )


def reset_category(achievement_id):

    organization = st.session_state[
        f"organization_{achievement_id}"
    ]

    categories = CATEGORY_OPTIONS[organization]

    st.session_state[
        f"category_{achievement_id}"
    ] = categories[0]


# ==================================================
# PAGE 1: STUDENT DETAILS
# ==================================================

st.header("Page 1: Student Personal Details")

with st.container(border=True):

    col1, col2 = st.columns(2)

    with col1:

        student_name = st.text_input(
            "Student Full Name *",
            key="student_name",
        )

        dob = st.date_input(
            "Date of Birth *",
            value=None,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            key="dob",
        )

    with col2:

        gender = st.selectbox(
            "Gender *",
            ["Male", "Female", "Other"],
            key="gender",
        )

    photo = st.file_uploader(
        "Upload Student Photograph * (Less than 5 MB)",
        type=["jpg", "jpeg", "png"],
        key="photo",
    )

    MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB

    if photo:
        if photo.size >= MAX_PHOTO_SIZE:
            st.error(
                "❌ Photo size must be less than 5 MB. "
                "Please re-upload a smaller photograph."
            )
            photo = None
        else:
            st.image(
                photo,
                caption="Student Photograph",
                width=180,
            )


# ==================================================
# PAGE 2: ACHIEVEMENTS
# ==================================================

st.header("Page 2: Sports Achievements")

st.info(
    "Add multiple achievements for this student "
    "using the Add Achievement button."
)

available_years = [
    None,
    *range(
        date.today().year + 5,
        1899,
        -1,
    ),
]

for display_number, achievement_id in enumerate(
    st.session_state.achievements,
    start=1,
):

    st.markdown("---")

    st.subheader(
        f"Achievement {display_number}"
    )

    with st.container(border=True):

        organization = st.selectbox(
            "Organization *",
            list(CATEGORY_OPTIONS.keys()),
            key=f"organization_{achievement_id}",
            on_change=reset_category,
            args=(achievement_id,),
        )

        categories = CATEGORY_OPTIONS[organization]

        category = st.selectbox(
            "Category *",
            categories,
            key=f"category_{achievement_id}",
        )

        if organization == "Other":

            category = st.text_input(
                "Specify Category *",
                key=f"custom_category_{achievement_id}",
            )

        gender_category = st.selectbox(
            "Gender Category *",
            GENDER_OPTIONS[organization],
            key=f"gender_category_{achievement_id}",
        )

        level = st.selectbox(
            "Competition Level *",
            LEVEL_OPTIONS,
            key=f"level_{achievement_id}",
        )

        result = st.selectbox(
            "Achievement *",
            RESULT_OPTIONS,
            key=f"result_{achievement_id}",
        )

        # ==================================================
        # COMPETITION LOCATION
        # ==================================================

        INDIAN_STATES = [
            "Andhra Pradesh",
            "Arunachal Pradesh",
            "Assam",
            "Bihar",
            "Chhattisgarh",
            "Goa",
            "Gujarat",
            "Haryana",
            "Himachal Pradesh",
            "Jharkhand",
            "Karnataka",
            "Kerala",
            "Madhya Pradesh",
            "Maharashtra",
            "Manipur",
            "Meghalaya",
            "Mizoram",
            "Nagaland",
            "Odisha",
            "Punjab",
            "Rajasthan",
            "Sikkim",
            "Tamil Nadu",
            "Telangana",
            "Tripura",
            "Uttar Pradesh",
            "Uttarakhand",
            "West Bengal",
        ]

        state = st.selectbox(
            "Competition State",
            options=INDIAN_STATES,
            key=f"state_{achievement_id}",
        )

        city = st.text_input(
            "Competition City",
            placeholder="Enter competition city",
            key=f"city_{achievement_id}",
        )

        competition = f"{city}, {state}"

        year = st.selectbox(
            "Competition Year *",
            available_years,
            format_func=lambda y: (
                "Select competition year"
                if y is None
                else str(y)
            ),
            key=f"year_{achievement_id}",
        )

        if len(st.session_state.achievements) > 1:

            st.button(
                "🗑️ Remove Achievement",
                key=f"remove_{achievement_id}",
                on_click=remove_achievement,
                args=(achievement_id,),
            )


st.button(
    "➕ Add Another Achievement",
    on_click=add_achievement,
)


# ==================================================
# SUBMIT REGISTRATION
# ==================================================

st.markdown("---")

if st.button(
    "💾 Submit Student Registration",
    type="primary",
    use_container_width=True,
):

    # Validate student details

    if not student_name.strip():
        st.error("Please enter the student name.")
        st.stop()

    if dob is None:
        st.error("Please select date of birth.")
        st.stop()

    if photo is None:
        st.error("Please upload student photograph.")
        st.stop()

    # Validate achievements

    achievements = []

    for display_number, achievement_id in enumerate(
        st.session_state.achievements,
        start=1,
    ):

        organization = st.session_state[
            f"organization_{achievement_id}"
        ]

        if organization == "Other":

            category = st.session_state.get(
                f"custom_category_{achievement_id}",
                "",
            )

            if not category.strip():

                st.error(
                    f"Please specify category for "
                    f"Achievement {display_number}."
                )

                st.stop()

        else:

            category = st.session_state[
                f"category_{achievement_id}"
            ]

        year = st.session_state[
            f"year_{achievement_id}"
        ]

        if year is None:

            st.error(
                f"Please select competition year for "
                f"Achievement {display_number}."
            )

            st.stop()

        achievement = {

            "organization": organization,

            "category": category,

            "gender_category": st.session_state[
                f"gender_category_{achievement_id}"
            ],

            "level": st.session_state[
                f"level_{achievement_id}"
            ],

            "result": st.session_state[
                f"result_{achievement_id}"
            ],

            "competition": st.session_state.get(
                f"competition_{achievement_id}",
                "",
            ),

            "year": int(year),

        }

        achievements.append(achievement)

    # Generate student ID

    student_id = str(uuid.uuid4())

    photo_file_id = None

    try:

        # Upload photo to GridFS

        photo_file_id = fs.put(
            photo.getvalue(),
            filename=photo.name,
            content_type=photo.type,
        )

        # Student document

        player_document = {
            "student_id": student_id,
            "name": student_name.strip(),

            # Convert Python date to MongoDB-compatible datetime
            "dob": datetime.combine(
                dob,
                datetime.min.time()
            ),

            "gender": gender,
            "photo_file_id": photo_file_id,
            "achievements": achievements,
            "created_at": datetime.utcnow(),
        }
        # Save to MongoDB

        players_collection.insert_one(
            player_document
        )

        st.success(
            "Student registered successfully!"
        )

        st.write(
            "Student ID:",
            student_id,
        )

        st.balloons()

    except Exception as e:

        if photo_file_id is not None:
            fs.delete(photo_file_id)

        st.error(
            f"Registration failed: {e}"
        )

