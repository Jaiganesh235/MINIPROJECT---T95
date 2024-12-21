import streamlit as st
import pandas as pd
import json
import datetime
import warnings
import os
from PIL import Image
from streamlit_option_menu import option_menu
warnings.filterwarnings("ignore")



def set_page_config():
    st.set_page_config(
        page_title="Hostel Management System",
        page_icon="🏠",
        layout="centered"
    )


    st.markdown("""
        <style>
        .stApp {
       background-color: #ffffff;
        background-size: cover;  /* Make sure the background image covers the whole area */
        background-position: center;  /* Center the background image */
        background-repeat: no-repeat;  /* Prevent the background image from repeating */
            
        }
        /* Login and Logout Page Background */
        .login-page, .logout-page {
          background-color: #ffffff;  /* White background */
          color: #00008b;  /* Dark blue text for contrast */
          padding: 20px;
          border-radius: 10px;
          box-shadow: 0px 4px 6px rgba(0, 0, 139, 0.3);  /* Slight dark blue shadow */
        }

         /* Input Fields: Username and Password */
        .stTextInput>div>input {
          background-color: #e6f2ff;  /* Light blue input fields */
          color: #00008b;  /* Dark blue text color */
          border: 2px solid #4169e1;  /* Royal blue border */
          padding: 10px;
          border-radius: 5px;
        }

        
        
        }

        
        .stButton>button {
          background-color: #00BFFF;  /* Medium blue button background */
          color: #ffffff;  /* White button text */
          font-weight: bold;
          padding: 10px 20px;
          border: none;
          border-radius: 5px;
          cursor: pointer;
        }

        .stButton>button:hover {
          background-color: #1e90ff;  /* Dodger blue background on hover */
        }

        /* Sidebar Icons */
        .sidebar .sidebar-content .stButton>button {
          color: #ffffff;  /* White icon color */
          background-color: #4169e1;  /* Royal blue background for icons */
          border-radius: 50%;
          padding: 10px;
          border: none;
          box-shadow: 0px 2px 4px rgba(0, 0, 139, 0.4);  /* Dark blue shadow */
        }

        .sidebar .sidebar-content .stButton>button:hover {
          background-color: #1e90ff;  /* Dodger blue background on hover */
        }

        /* Sidebar Content Text */
        .sidebar .sidebar-content {
          background-color: #00008b;  /* Dark blue for sidebar background */
        }
        .sidebar .sidebar-content .stSelectbox label {
          color: #ffffff !important;  /* White text color in sidebar */
        }

        .sidebar .sidebar-content .stButton>button {
          width: 100%;
        }   
        </style>
        """, unsafe_allow_html=True)


def add_logo_and_title():
    col1, col2 = st.columns([1, 4])  # Increased the size of col2
    with col1:
        st.image("D:/MINIPROJECT/logo_1.jpg", width=125)
    with col2:
        st.title("Digitalized Hostel System")




# Data storage
def load_data():
    try:
        with open('hostel_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    required_keys = ['students', 'rooms', 'canteen_menu', 'complaints', 'inout_times',
                     'visitors', 'notices', 'outing_requests', 'service_requests', 'users']

    for key in required_keys:
        if key not in data:
            if key == 'service_requests':
                data[key] = []
            elif key == 'users':
                data[key] = {'admin': 'admin123', 'security': 'security123'}
            elif key == 'notices':
                data[key] = []  # Initializing as an empty list
            else:
                data[key] = {}

    return data

def save_data(data):
    with open('hostel_data.json', 'w') as f:
        json.dump(data, f)

def analytics_dashboard(data):
    st.subheader("Analytics Dashboard")

    # Room Occupancy Analytics
    room_occupancy = {room: len(details.get('occupants', [])) for room, details in data['rooms'].items()}
    occupancy_df = pd.DataFrame.from_dict(room_occupancy, orient='index', columns=['Occupants'])
    st.bar_chart(occupancy_df)

    # Service Requests Analytics
    service_counts = pd.DataFrame.from_dict(
        {'Pending': sum(1 for r in data['service_requests'] if r['status'] == 'Pending'),
         'Completed': sum(1 for r in data['service_requests'] if r['status'] == 'Completed')}, orient='index', columns=['Count'])
    st.write("### Service Request Summary")
    st.bar_chart(service_counts)

    # Outing Requests Analytics
    outing_counts = pd.DataFrame.from_dict(
        {'Pending': sum(1 for r in data['outing_requests'] if r['status'] == 'Pending'),
         'Accepted': sum(1 for r in data['outing_requests'] if r['status'] == 'Accepted'),
         'Rejected': sum(1 for r in data['outing_requests'] if r['status'] == 'Rejected')}, orient='index', columns=['Count'])
    st.write("### Outing Request Summary")
    st.bar_chart(outing_counts)


def view_student_list_with_attendance(data):


    current_date = st.date_input("Date", value=datetime.date.today(), key="view_date")

    if str(current_date) in data.get('attendance', {}):
        attendance_data = data['attendance'][str(current_date)]
    else:
        st.warning("No attendance data found for the selected date.")
        return

    # Display the student list with their attendance status
    for student_id, student_info in data['students'].items():
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.write(f"ID: {student_id}")
        with col2:
            st.write(f"Name: {student_info['name']}")
        with col3:
            status = attendance_data.get(student_id, "Absent")
            st.write(status)


# Authentication
def login(data):
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    user_type = st.sidebar.selectbox("User Type", ["Admin", "Student", "Security"])

    if st.sidebar.button("Login"):
        if user_type == "Admin":
            if username == "admin" and password == "admin123":
                st.session_state["logged_in"] = True
                st.session_state["user_type"] = "Admin"
                return True
            else:
                st.sidebar.error("Incorrect username or password")

        elif user_type == "Security":
            if username == "security" and password == "security123":
                st.session_state["logged_in"] = True
                st.session_state["user_type"] = "Security"
                return True
            else:
                st.sidebar.error("Incorrect username or password")

        elif user_type == "Student":
            # Search for the username in the students' data
            for student_id, student_info in data["students"].items():
                if student_info.get("username") == username and student_info.get("password") == password:
                    st.session_state["logged_in"] = True
                    st.session_state["user_type"] = "Student"
                    st.session_state["student_id"] = student_id  # Store the student_id for reference
                    
                    # Log the student's login activity
                    log_student_activity(data, student_id, "Login")
                    return True

            st.sidebar.error("Incorrect username or password")

    return False


def logout(data):
    """
    Logs the user out and records the logout activity if a student is logged in.
    """
    if "student_id" in st.session_state:
        log_student_activity(data, st.session_state["student_id"], "Logout")
        del st.session_state["student_id"]

    st.session_state["logged_in"] = False
    st.session_state["user_type"] = None
    st.success("Logged out successfully!")



def record_inout_time(data):
    """
    Allows Security to record student in/out times digitally.
    """
    st.subheader("📋 Record In/Out Time")

    # Ensure only Security can access
    if st.session_state.get("user_type") != "Security":
        st.error("This feature is restricted to Security personnel.")
        return

    # Dropdown for selecting student
    student_id = st.selectbox(
        "Select Student",
        options=["Select"] + list(data["students"].keys()),
        format_func=lambda x: f"{x} - {data['students'][x]['name']}" if x != "Select" else "Select",
    )

    if student_id == "Select":
        st.info("Please select a student to proceed.")
        return

    # Action options
    action = st.radio("Select Action", ["In", "Out"])

    # Record time
    if st.button("Record Time"):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Ensure 'inout_times' key exists
        if "inout_times" not in data or not isinstance(data["inout_times"], list):
            data["inout_times"] = []

        # Append the record
        data["inout_times"].append({
            "student_id": student_id,
            "name": data["students"][student_id]["name"],
            "action": action,
            "timestamp": current_time,
        })

        save_data(data)  # Save updated data
        st.success(f"Recorded '{action}' time for {data['students'][student_id]['name']} successfully!")


def student_menu(data, student_id):

    with st.sidebar:
        student_options = option_menu(
        menu_title="STUDENT DASHBOARD",
        options=["👤 View Profile", "🏠 Check Room", "🔄 Request Room Change", "👥 View Roommates",
                 "🍽️ View Canteen Menu", "📢 File Complaint",
                 "🚶 Raise Outing Request", "📊 Outing Request Status",
                 "🛠️ Request Service", "👁️ View Service Requests", "📌 View Notices",
                 "📋 View Complaints","View My Activity Logs","View Activity Summary"],
        default_index=0,
        styles={
            "container":{"padding":"0!important","width":"100%"},
            "nav-link":{
                "font-size":"15px",
            },
            "nav-link-selected":{"background-color": "#00BFFF"},
            "menu-title": {"font-size": "18px","font-style":"italic","font-weight":"bold"},}
        )




    if "View Profile" in student_options:
        view_student_profile(data, student_id)
    elif "Check Room" in student_options:
        check_student_room(data, student_id)
    elif "Request Room Change" in student_options:
        request_room_change(data, student_id)
    elif "View Roommates" in student_options:
        view_roommates(data, student_id)
    elif "View Canteen Menu" in student_options:
        view_canteen_menu(data)
    elif "File Complaint" in student_options:
        file_complaint(data, student_id)
    elif "Raise Outing Request" in student_options:
        raise_outing_request(data, student_id)
    elif "Outing Request Status" in student_options:
        view_outing_request_status(data, student_id)
    elif "Request Service" in student_options:
        request_service(data, student_id)
    elif "View Service Requests" in student_options:
        view_service_requests(data, student_id)
    elif "View Notices" in student_options:
        view_notices(data)
    elif "View Complaints" in student_options:
        view_student_complaints(data, student_id)
    elif "View My Activity Logs" in student_options:
        view_student_logs(data, student_id)
    elif "View Activity Summary" in student_options:
        student_logs_summary(data, student_id=st.session_state["student_id"])

    

def student_logs_summary(data, student_id=None):
    """
    Visualizes summary statistics for student logs.
    """
    st.subheader("Activity Summary")

    logs = data.get("activity_logs", [])
    if student_id:
        logs = [log for log in logs if log["student_id"] == student_id]

    if not logs:
        st.info("No activity logs available.")
        return

    log_df = pd.DataFrame(logs)
    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"])

    # Summary statistics
    st.write("### Action Breakdown")
    action_counts = log_df["action"].value_counts()
    st.bar_chart(action_counts)

    st.write("### Activity Over Time")
    time_series = log_df.groupby(log_df["timestamp"].dt.date).size()
    st.line_chart(time_series)



def view_roommates(data, student_id):
    st.subheader("Roommates")
    room_number = data['students'][student_id]['room']
    roommates = [sid for sid in data['rooms'][room_number]['occupants'] if sid != student_id]

    if roommates:

        for roommate in roommates:
            roommate_info = data['students'][roommate]
            if 'photo' in roommate_info:
                col1, col2, col3 = st.columns([1, 2, 4])  # Adjust column widths as needed

                with col1:  # Center column
                    st.write(f" ")
                    st.write(f" ")
                    st.write(f" ")
                    st.image(roommate_info['photo'], width=200)
                with col3:
                    st.write(f" ")
                    st.write(f" ")
                    st.write(f" ")
                    st.write(f"Student ID : {student_id}")
                    st.write(f"Name       : {roommate_info.get('name', 'N/A')}")
                    st.write(f"Age        : {roommate_info.get('age', 'N/A')}")
                    st.write(f"Gender     : {roommate_info.get('gender', 'N/A')}")
                    st.write(f"Course     : {roommate_info.get('course', 'N/A')}")
                    st.write(f"Room       : {roommate_info.get('room', 'N/A')}")

    else:
        st.info("You have no roommates.")

def request_service(data, student_id):
    st.subheader("Request Service")
    service_type = st.text_input("Service Type")
    additional_details = st.text_area("Additional Details")

    if st.button("Submit Service Request"):
        request = {
            'student_id': student_id,
            'service_type': service_type,
            'additional_details': additional_details,
            'status': 'Pending',
            'admin_response': None,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data['service_requests'].append(request)
        save_data(data)
        st.success("Service request submitted successfully!")

def view_service_requests(data, student_id):
    st.subheader("Your Service Requests")

    requests = [req for req in data['service_requests'] if req['student_id'] == student_id]

    if requests:
        for i, request in enumerate(requests):
            st.write(f"**Request {i + 1}**")
            st.write(f"Service Type: {request['service_type']}")
            st.write(f"Additional Details: {request['additional_details']}")
            st.write(f"Status: {request['status']}")
            if request['admin_response']:
                st.write(f"Admin Response: {request['admin_response']}")
            st.write(f"Requested on: {request['timestamp']}")
            st.write("---")
    else:
        st.info("You have no service requests.")


def view_outing_request_status(data, student_id):
    st.subheader("Outing Request Status")

    requests = [req for req in data['outing_requests'] if req['student_id'] == student_id]

    if requests:
        for i, request in enumerate(requests):
            st.write(f"**Request {i + 1}**")
            st.write(f"Reason: {request['reason']}")
            st.write(f"Outing Date: {request['outing_date']}")
            st.write(f"Outing Time: {request['outing_time']}")
            st.write(f"Status: {request['status']}")
            if request['admin_response']:
                st.write(f"Admin Response: {request['admin_response']}")
            st.write("---")
    else:
        st.info("You have no outing requests.")


def manage_rooms(data):
    st.subheader("Manage Rooms")
    gender = st.selectbox("Gender", ["Select", "Male", "Female"])

    if gender == "Male":
        block_options = ["A", "B", "C", "D"]
    else:
        block_options = ["E","F","G","H"]

    block = st.selectbox("Block", block_options)

    if gender == "Male":
        room_options = ["524", "525", "526", "527", "528", "529", "530", "531", "532", "533", "534", "535"]
    else:
        room_options = ["424","424","425","426","427","428","429","430","431","432","433","434","435","436"]

    # Room input fields
    room_number = st.selectbox("Room Number",room_options)
    room_type = st.selectbox("Room Type", ["AC", "Non-AC"])
    capacity = st.number_input("Capacity", min_value=1, max_value=10)



    # Add/Update Room button

    # Add/Update Room button
    if st.button("Add/Update Room"):
        if not room_number.strip():  # Check if room number is empty or only whitespace
            st.warning("Please enter the room number.")
        else:
            # If room number is not null, proceed with adding or updating the room
            if room_number in data['rooms']:
                data['rooms'][room_number]['capacity'] = capacity
                data['rooms'][room_number]['type'] = room_type
                data['rooms'][room_number]['gender'] = gender

                st.success(f"Room {room_number} ({room_type}) updated successfully!")
            else:
                data['rooms'][room_number] = {'capacity': capacity, 'occupants': [], 'type': room_type, 'gender': gender, 'block': block}
                st.success(f"Room {room_number} ({room_type}) added successfully!")

    # Display current rooms
    st.subheader("Current Rooms")
    room_df = pd.DataFrame.from_dict(data['rooms'], orient='index')

    st.dataframe(room_df, width=1000)

def request_room_change(data, student_id):
    st.subheader("Request Room Change")

    student = data['students'].get(student_id)
    if not student:
        st.error("Student information not found.")
        return

    current_room = student.get('room')
    student_gender = student.get('gender', 'Not Specified')

    if not current_room:
        st.error("Incomplete student information. Room is missing.")
        return

    # Filter rooms to only those with available vacancies and matching gender
    available_rooms = [
        room for room, details in data['rooms'].items()
        if len(details.get('occupants', [])) < details.get('capacity', 0)
        and details['gender'] == student_gender
        and room != current_room  # Exclude current room
    ]


    if available_rooms:
        desired_room = st.selectbox("Select Desired Room", available_rooms)

        if st.button("Request Room Change"):
            if desired_room in data['rooms']:
                # Add the request to a list of pending requests
                data.setdefault('room_change_requests', {})[student_id] = desired_room
                save_data(data)
                st.success("Room change request submitted successfully!")
            else:
                st.error("The selected room does not exist.")
    else:
        if student_gender == 'Not Specified':
            st.info("No rooms are available for change.")
        else:
            st.info(f"No {student_gender} rooms are available for change.")

    # Display any existing notifications for the student
    if 'notifications' in data and student_id in data['notifications']:
        st.info(data['notifications'][student_id])
        # Remove the notification after showing it
        del data['notifications'][student_id]
        save_data(data)  # Save data after modifying it

def admin_review_room_change_requests(data):
        st.subheader("Room Change Requests")

        if 'room_change_requests' in data and data['room_change_requests']:
            # Make a list of requests to process to avoid modifying the dictionary during iteration
            requests_to_process = list(data['room_change_requests'].items())

            for student_id, requested_room in requests_to_process:
                student = data['students'].get(student_id)

                if student:
                    # Display student photo if available
                    if 'photo' in student and os.path.exists(student['photo']):
                        try:
                            image = Image.open(student['photo'])
                            st.image(image, caption=f"Student: {student['name']}", width=150)
                        except Exception as e:
                            st.write(f"Error loading image: {e}")
                    else:
                        st.write("No photo available")

                    # Display student details and request information
                    st.markdown(f"**Student ID:** {student_id}")
                    st.markdown(f"**Student Name:** {student['name']}")
                    st.markdown(f"**Current Room:** {student['room']}")
                    st.markdown(f"**Requested Room:** {requested_room}")

                    # Show room availability status
                    room_info = data['rooms'].get(requested_room, {})
                    current_occupants = len(room_info.get('occupants', []))
                    room_capacity = room_info.get('capacity', 0)
                    room_availability = room_capacity - current_occupants

                    st.markdown(
                        f"**Room {requested_room} Availability:** {room_availability} slots available out of {room_capacity}")

                    # Create Accept and Reject buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        accept_button = st.button(f"Accept Request for {student_id}", key=f"accept_{student_id}")
                    with col2:
                        reject_button = st.button(f"Reject Request for {student_id}", key=f"reject_{student_id}")

                    # Process Accept button
                    if accept_button:
                        if current_occupants < room_capacity:
                            current_room = student['room']

                            # Check and update room assignments
                            if student_id in data['rooms'][current_room]['occupants']:
                                data['rooms'][current_room]['occupants'].remove(student_id)
                            else:
                                st.warning(
                                    f"Student ID {student_id} not found in the current room {current_room} occupants list.")

                            data['rooms'][requested_room]['occupants'].append(student_id)
                            student['room'] = requested_room

                            # Notify the student
                            data.setdefault('notifications', {})[
                                student_id] = f"Your request to change room to {requested_room} has been accepted."

                            # Remove the request after processing
                            del data['room_change_requests'][student_id]
                            save_data(data)
                            st.success(f"Room change request for {student_id} accepted successfully!")
                        else:
                            st.error(f"Room {requested_room} is now full.")

                    # Process Reject button
                    if reject_button:
                        # Notify the student
                        data.setdefault('notifications', {})[student_id] = "Your room change request has been rejected."

                        # Remove the request after processing
                        del data['room_change_requests'][student_id]
                        save_data(data)
                        st.success(f"Room change request for {student_id} rejected successfully!")

                    st.markdown("---")  # Add a separator between requests

                else:
                    st.error(f"Student details not found for ID: {student_id}")
        else:
            st.info("No pending room change requests.")


def update_canteen_menu(data):
    st.subheader("Update Canteen Menu")

    day = st.selectbox("Select Day", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    breakfast = st.text_input("Breakfast")
    lunch = st.text_input("Lunch")
    dinner = st.text_input("Dinner")

    if st.button("Update Menu"):
        data['canteen_menu'][day] = {
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner
        }
        st.success(f"Menu for {day} updated successfully!")


def view_complaints(data):
    st.subheader("Student Complaints")

    if data['complaints']:
        for i, complaint in enumerate(data['complaints']):
            student_id = complaint['student_id']
            timestamp = complaint['timestamp']
            complaint_text = complaint['complaint']
            feedback = complaint.get('feedback', '')

            # Fetch student details including photo
            student = data['students'].get(student_id)



            st.write(f"**Timestamp:** {timestamp}")
            st.write(f"**Complaint:** {complaint_text}")

            # Admin Feedback Section
            if st.checkbox(f"Give feedback for complaint {i + 1}"):
                feedback_text = st.text_area(f"Feedback for {student_id}", value=feedback, key=f'feedback_{i}')
                if st.button(f"Submit Feedback for complaint {i + 1}", key=f'submit_feedback_{i}'):
                    data['complaints'][i]['feedback'] = feedback_text
                    st.success("Feedback submitted successfully!")

            # Display Feedback if available
            if feedback:
                st.write(f"**Feedback:** {feedback}")
            st.markdown("---")  # Adds a horizontal line between complaints
    else:
        st.info("No complaints filed yet.")

def view_student_complaints(data, student_id):
    st.subheader("My Complaints and Feedback")

    # Filter complaints by student_id
    student_complaints = [complaint for complaint in data['complaints'] if complaint['student_id'] == student_id]

    if student_complaints:
        for complaint in student_complaints:
            timestamp = complaint['timestamp']
            complaint_text = complaint['complaint']
            feedback = complaint.get('feedback', 'No feedback provided yet.')

            st.write(f"**Timestamp:** {timestamp}")
            st.write(f"**Complaint:** {complaint_text}")
            st.write(f"**Feedback From Admin:** {feedback}")
            st.markdown("---")  # Adds a horizontal line between complaints
    else:
        st.info("You have not filed any complaints yet.")

def security_menu(data):
    with st.sidebar:
        # Security menu options using Streamlit option menu
        security_options = option_menu(
            menu_title="SECURITY DASHBOARD",
            options=["📝 Record Visitor", "👁️ View Visitors", "📝 Record In/Out Time", "👁️ View In/Out Times"],
            icons=["person-plus", "eye", "calendar-plus", "calendar2-week", "camera"],
            menu_icon="shield-lock",
            default_index=0,
            styles={
                "container": {"padding": "5px", "font-size": "14px"},
                "menu-title": {"font-size": "16px", "font-style": "italic", "font-weight": "bold"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "5px"},
                "nav-link-selected": {"background-color": "#00BFFF"},
            }
        )

    # Routing options to respective functionalities
    if security_options == "📝 Record Visitor":
        record_visitor(data)
    elif security_options == "👁️ View Visitors":
        view_visitors(data)
    elif security_options == "📝 Record In/Out Time":
        record_inout_time(data)
    elif security_options == "👁️ View In/Out Times":
        view_inout_times(data)
    




def generate_reports(data):
    st.subheader("📊 Generate Reports")

    # Report type selection
    report_type = st.selectbox(
        "Select Report Type",
        ["Room Occupancy", "Student List"],
        index=0,
        help="Choose the type of report you'd like to generate."
    )

    if report_type == "Room Occupancy":
        # Calculate room occupancy
        room_occupancy = [
            {
                "Room": room,
                "Occupants": len(info.get("occupants", [])),
                "Capacity": info.get("capacity", 0),
                "Availability": info.get("capacity", 0) - len(info.get("occupants", [])),
            }
            for room, info in data["rooms"].items()
        ]
        occupancy_df = pd.DataFrame(room_occupancy)

        # Display data and visualization
        st.write("### Room Occupancy Details")
        st.dataframe(occupancy_df)

        st.write("### Room Occupancy Visualization")
        st.bar_chart(occupancy_df.set_index("Room")[["Occupants", "Capacity"]])

        # Export to CSV
        csv_data = occupancy_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Room Occupancy Report as CSV",
            data=csv_data,
            file_name="room_occupancy_report.csv",
            mime="text/csv",
        )

    elif report_type == "Student List":
        # Create a student DataFrame
        student_df = pd.DataFrame.from_dict(data["students"], orient="index")

        # Drop sensitive or unnecessary columns
        columns_to_drop = ["photo", "attendance_history", "username", "password"]
        student_df = student_df.drop(columns=[col for col in columns_to_drop if col in student_df.columns])

        # Add filtering options
        st.write("### Student List")
        search_query = st.text_input("Search by Name, ID, or Course")
        filtered_df = student_df[
            student_df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)
        ] if search_query else student_df

        st.dataframe(filtered_df)

        # Export to CSV
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Student List Report as CSV",
            data=csv_data,
            file_name="student_list_report.csv",
            mime="text/csv",
        )




def view_canteen_menu(data):
    st.subheader("Canteen Menu")
    if data['canteen_menu']:
        for day, meals in data['canteen_menu'].items():
            st.write(f"**{day}**")
            for meal, items in meals.items():
                st.write(f"- {meal.capitalize()}: {items}")
    else:
        st.info("Canteen menu not available.")


def file_complaint(data, student_id):
    st.subheader("File a Complaint")
    complaint_text = st.text_area("Enter your complaint")

    if st.button("Submit Complaint"):
        if "complaints" not in data or not isinstance(data["complaints"], list):
            data["complaints"] = []

        data["complaints"].append({
            "student_id": student_id,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "complaint": complaint_text
        })

        log_student_activity(data, student_id, "Complaint Filed", complaint_text)
        st.success("Complaint submitted successfully!")

def view_inout_times(data):
    """
    Allows Security to view and analyze student in/out times.
    """
    st.subheader("📊 View In/Out Times")

    # Ensure only Security can access
    if st.session_state.get("user_type") != "Security":
        st.error("This feature is restricted to Security personnel.")
        return

    if "inout_times" not in data or not data["inout_times"]:
        st.info("No in/out times recorded yet.")
        return

    # Convert records to DataFrame
    inout_df = pd.DataFrame(data["inout_times"])
    inout_df["timestamp"] = pd.to_datetime(inout_df["timestamp"])

    # Filters
    with st.expander("Filters"):
        selected_student = st.selectbox(
            "Filter by Student",
            options=["All"] + inout_df["student_id"].unique().tolist(),
            format_func=lambda x: f"{x} - {data['students'][x]['name']}" if x != "All" else "All",
        )
        selected_action = st.selectbox("Filter by Action", ["All", "In", "Out"])
        date_range = st.date_input("Filter by Date Range", [])

        # Apply filters
        filtered_df = inout_df
        if selected_student != "All":
            filtered_df = filtered_df[filtered_df["student_id"] == selected_student]
        if selected_action != "All":
            filtered_df = filtered_df[filtered_df["action"] == selected_action]
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df["timestamp"].dt.date >= date_range[0])
                & (filtered_df["timestamp"].dt.date <= date_range[1])
            ]

    # Display filtered data
    st.write("### Filtered Records")
    st.dataframe(filtered_df)

    # Visualization
    st.write("### Visualization")
    action_counts = filtered_df["action"].value_counts()
    st.bar_chart(action_counts, use_container_width=True)

    time_series = filtered_df.groupby(filtered_df["timestamp"].dt.date).size()
    st.line_chart(time_series, use_container_width=True)

    # Export as CSV
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download In/Out Times as CSV",
        data=csv_data,
        file_name="inout_times_report.csv",
        mime="text/csv",
    )


def record_visitor(data):
    st.subheader("Record Visitor")

    visitor_name = st.text_input("Visitor Name")
    purpose = st.text_input("Purpose of Visit")
    student_id = st.text_input("Student ID to Visit")

    if st.button("Record Visitor"):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Ensure 'visitors' is a list before appending
        if 'visitors' not in data or not isinstance(data['visitors'], list):
            data['visitors'] = []

        data['visitors'].append({
            'visitor_name': visitor_name,
            'purpose': purpose,
            'student_id': student_id,
            'timestamp': current_time
        })

        st.success("Visitor recorded successfully!")


def view_visitors(data):
    st.subheader("Visitor Records")

    if data['visitors']:
        visitor_df = pd.DataFrame(data['visitors'])
        st.dataframe(visitor_df)
    else:
        st.info("No visitors recorded yet.")


def mark_attendance(data):
    st.subheader("Mark Student Attendance")

    # Get the current date
    current_date = st.date_input("Date", value=datetime.date.today())

    # Create a list of all students
    student_list = list(data.get('students', {}).items())

    # Display a table with checkboxes for attendance
    st.write("Mark attendance for each student:")
    attendance_data = {}

    for student_id, student_info in student_list:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.write(f"ID: {student_id}")
        with col2:
            st.write(f"Name: {student_info['name']}")
        with col3:
            attendance = st.checkbox("Present", key=f"attendance_{student_id}")
        attendance_data[student_id] = "Present" if attendance else "Absent"

    if st.button("Save Attendance"):
        # Create attendance record for the day if it doesn't exist
        if 'attendance' not in data:
            data['attendance'] = {}
        if str(current_date) not in data['attendance']:
            data['attendance'][str(current_date)] = {}

        # Save attendance data
        for student_id, status in attendance_data.items():
            data['attendance'][str(current_date)][student_id] = status

            # Update student records with the latest attendance
            if 'attendance_history' not in data['students'][student_id]:
                data['students'][student_id]['attendance_history'] = {}
            data['students'][student_id]['attendance_history'][str(current_date)] = status

        st.success("Attendance marked successfully!")



# Add other functions like add_student, manage_rooms, etc. her
def admin_menu(data):

    with st.sidebar:
        admin_option = option_menu(
        menu_title="ADMIN DASHBOARD",
        options=["👥 Add Student", "📝 Update Student", "🗑️ Delete Student", "🏠 Manage Rooms",
                 "🍽️ Update Canteen Menu", "📢 View Complaints", "📊 Generate Reports",
                 "⏱️ View In/Out Times", "👁️ View Visitors", "🚶 View Outing Requests",
                 "📋 View Student List", "🛠️ View Service Requests", "📌 Add Notices",
                 "🔄 Room Change Requests", "📅 Mark Attendance", "🗒️ Attendance Record","Student Activity Logs","Activity Logs Summary"],

        styles={
            "container": {"padding": "0!important", "width": "100%"},
            "nav-link": {
                "font-size": "15px",
            },
            "nav-link-selected": {"background-color": "#00BFFF"},
            "menu-title": {"font-size": "18px", "font-style": "italic", "font-weight": "bold"}}
        )


    if "Add Student" in admin_option:
        add_student(data)
    elif "Update Student" in admin_option:
        update_student(data)
    elif "Delete Student" in admin_option:
        delete_student(data)
    elif "Manage Rooms" in admin_option:
        manage_rooms(data)
    elif "Update Canteen Menu" in admin_option:
        update_canteen_menu(data)
    elif "View Complaints" in admin_option:
        view_complaints(data)
    elif "Generate Reports" in admin_option:
        generate_reports(data)
    elif "View In/Out Times" in admin_option:
        view_inout_times(data)
    elif "View Visitors" in admin_option:
        view_visitors(data)
    elif "View Outing Requests" in admin_option:
        manage_outing_requests(data)
    elif "View Student List" in admin_option:
        view_student_list(data)
    elif "View Service Requests" in admin_option:
        manage_service_requests(data)
    elif "Add Notices" in admin_option:
        manage_notices(data)
    elif "Room Change Requests" in admin_option:
        admin_review_room_change_requests(data)
    elif "Mark Attendance" in admin_option:
        mark_attendance(data)  # New condition for the attendance feature
    elif "Attendance Record" in admin_option:
        view_student_list_with_attendance(data)
    elif "Notifications" in admin_option:
        view_notifications(data)
    elif "Analytics Dashboard" in admin_option:
        analytics_dashboard(data)
    elif "Student Activity Logs" in admin_option:
        view_activity_logs(data)
    elif "Activity Logs Summary" in admin_option:
        student_logs_summary(data)
    
    
    
    


def manage_service_requests(data):
    st.subheader("Manage Service Requests")

    if data['service_requests']:
        for i, request in enumerate(data['service_requests']):
            student_id = request['student_id']
            student = data['students'].get(student_id)

            col1, col2 = st.columns([1, 3])

            with col1:
                if student and 'photo' in student:
                    photo_path = student['photo']
                    if photo_path and os.path.exists(photo_path):
                        st.image(photo_path, caption=f"{student['name']}'s Photo", width=100)
                    else:
                        st.write("No photo available")
                else:
                    st.write("No photo available")

            with col2:
                st.write(f"**Request {i + 1}**")
                st.write(f"Student ID: {student_id}")
                if student:
                    st.write(f"Name: {student['name']}")
                    st.write(f"Course: {student['course']}")
                st.write(f"Service Type: {request['service_type']}")
                st.write(f"Additional Details: {request['additional_details']}")
                st.write(f"Status: {request['status']}")
                st.write(f"Requested on: {request['timestamp']}")

                if request['status'] == 'Pending':
                    if st.button(f"Mark Request {i + 1} as Completed"):
                        data['service_requests'][i]['status'] = 'Completed'
                        data['service_requests'][i]['admin_response'] = f"Completed on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        save_data(data)
                        st.success(f"Request {i + 1} marked as completed!")
                        st.rerun()

            st.markdown("---")  # Add a separator between requests
    else:
        st.info("No service requests to manage.")


def delete_student(data):
    st.subheader("Delete Student")

    student_id = st.selectbox("Select Student to Delete", list(data['students'].keys()))

    if st.button("Delete Student"):
        if student_id in data['students']:
            # Remove student from room occupants
            room_number = data['students'][student_id]['room']
            if room_number in data['rooms']:
                data['rooms'][room_number]['occupants'].remove(student_id)

            # Delete student data
            del data['students'][student_id]
            st.success(f"Student {student_id} deleted successfully!")
        else:
            st.error("Student ID not found!")

def check_student_room(data, student_id):
    st.subheader("Room Information")
    student_info = data['students'].get(student_id, {})
    room_number = student_info.get('room')

    if room_number and room_number in data['rooms']:
        room_info = data['rooms'][room_number]
        st.write(f"Room Number: {room_number}")
        st.write(f"Type: {room_info['type']}")
        st.write(f"Capacity: {room_info['capacity']}")
        st.write(f"Current Occupants: {len(room_info['occupants'])}")
    else:
        st.error("Room information not available for this student.")




def raise_outing_request(data, student_id):
    st.subheader("Raise Outing Request")
    reason = st.text_area("Reason for Outing")
    outing_date = st.date_input("Outing Date")
    outing_time = st.time_input("Outing Time")

    if st.button("Submit Request"):
        request = {
            'student_id': student_id,
            'reason': reason,
            'outing_date': outing_date.strftime("%Y-%m-%d"),
            'outing_time': outing_time.strftime("%H:%M"),
            'status': 'Pending',
            'admin_response': None
        }
        if 'outing_requests' not in data or not isinstance(data['outing_requests'], list):
            data['outing_requests'] = []
        data['outing_requests'].append(request)

        # Add a notification for the admin
        data.setdefault('notifications', []).append(f"New outing request from Student ID {student_id}.")
        save_data(data)
        st.success("Outing request submitted successfully!")

def view_notifications(data):
    st.subheader("Notifications")
    notifications = data.get('notifications', [])
    if notifications:
        for notification in notifications:
            st.write(notification)
        if st.button("Clear Notifications"):
            data['notifications'] = []
            save_data(data)
            st.success("Notifications cleared.")
    else:
        st.info("No new notifications.")



# Function for admin to manage outing requests
import qrcode
import io

def manage_outing_requests(data):
    st.subheader("Manage Outing Requests")

    if data['outing_requests']:
        for i, request in enumerate(data['outing_requests']):
            st.write(f"**Request {i + 1}**")

            # Get student details
            student = data['students'].get(request['student_id'])

            if student:
                st.write(f"Student Name: {student['name']}")
            else:
                st.write("Student details not found")

            st.write(f"Student ID: {request['student_id']}")
            st.write(f"Reason: {request['reason']}")
            st.write(f"Outing Date: {request['outing_date']}")
            st.write(f"Outing Time: {request['outing_time']}")
            st.write(f"Status: {request['status']}")

            if request['status'] == 'Pending':
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Accept Request {i + 1}"):
                        data['outing_requests'][i]['status'] = 'Accepted'
                        data['outing_requests'][i]['admin_response'] = f"Accepted on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

                        # Generate QR Code for accepted request
                        qr_data = f"Student ID: {request['student_id']}\nOuting Date: {request['outing_date']}\nTime: {request['outing_time']}\nReason: {request['reason']}"
                        qr = qrcode.make(qr_data)
                        qr_buffer = io.BytesIO()
                        qr.save(qr_buffer, format="PNG")
                        qr_buffer.seek(0)
                        st.image(qr_buffer, caption="Outing QR Code")

                        save_data(data)
                        st.success(f"Request {i + 1} accepted!")
                        st.rerun()

                with col2:
                    if st.button(f"Reject Request {i + 1}"):
                        data['outing_requests'][i]['status'] = 'Rejected'
                        data['outing_requests'][i]['admin_response'] = f"Rejected on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        save_data(data)
                        st.error(f"Request {i + 1} rejected!")
                        st.rerun()
            st.markdown("---")  # Add a separator between requests
    else:
        st.info("No outing requests to manage.")



def add_notice(data):
    # Input fields for the notice details
    notice_title = st.text_input("Notice Title")
    notice_description = st.text_area("Notice Description")
    notice_date = st.date_input("Notice Date")

    # Button to add the notice
    if st.button("Add Notice"):
        # Ensure 'notices' is a list in the 'data' dictionary
        if 'notices' not in data or not isinstance(data['notices'], list):
            data['notices'] = []  # Initialize as an empty list if it doesn't exist or isn't a list

        # Append the new notice to the list
        data['notices'].append({
            'title': notice_title,
            'description': notice_description,
            'date': str(notice_date)  # Convert date to string if needed
        })

        # Confirmation message
        st.success("Notice added successfully!")



def delete_notice(data):
    st.subheader("Delete Notice")

    if data['notices']:
        notice_titles = [notice['title'] for notice in data['notices']]
        notice_to_delete = st.selectbox("Select Notice to Delete", notice_titles)

        if st.button("Delete Notice"):
            # Removing the selected notice
            data['notices'] = [notice for notice in data['notices'] if notice['title'] != notice_to_delete]
            save_data(data)
            st.success("Notice deleted successfully!")
    else:
        st.info("No notices available to delete.")


def view_notices(data, student_id=None):
    st.subheader("NOTICES")

    notices = data.get("notices", [])
    if notices:
        if student_id:
            log_student_activity(data, student_id, "Viewed Notices")
        
        for notice in notices:
            st.markdown(f"""
            **{notice['title']}**

            Date: {notice['date']}

            {notice['description']}

            ---
            """)
    else:
        st.info("No notices available at the moment.")


# Function to manage notices (accessible by admin)
def manage_notices(data):
    st.subheader("Manage Notices")

    notice_options = ["Add Notice", "Delete Notice"]
    notice_choice = st.selectbox("Select Action", notice_options)

    if notice_choice == "Add Notice":
        add_notice(data)
    elif notice_choice == "Delete Notice":

        delete_notice(data)

def view_student_profile(data, student_id):

    st.write(f" ")
    st.write(f" ")
    st.write(f" ")

    student_info = data['students'][student_id]



    # Display the photo with a smaller width if available
    if 'photo' in student_info:
        col1, col3 = st.columns([1, 1])  # Adjust column widths as needed

        with col1:  # Center column
            st.image(student_info['photo'], width=250)
        with col3:
            st.write(f" ")


            st.write(f"Student ID : {student_id}")
            st.write(f"Name       : {student_info.get('name', 'N/A')}")
            st.write(f"Age        : {student_info.get('age', 'N/A')}")
            st.write(f"Gender     : {student_info.get('gender', 'N/A')}")
            st.write(f"Course     : {student_info.get('course', 'N/A')}")
            st.write(f"Room       : {student_info.get('room', 'N/A')}")
            
        log_student_activity(data, student_id, "Viewed Profile")



def add_student(data):
    st.subheader("Add New Student")

    student_id = st.text_input("Student ID")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=16, max_value=30)
    course = st.text_input("Course")
    gender = st.selectbox("Gender", ["Male", "Female"])

    available_rooms = [room for room, details in data['rooms'].items() if details['gender'] == gender]
    room_number = st.selectbox("Assign Room", available_rooms)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    photo = st.file_uploader("Upload Photo", type=["png", "jpg", "jpeg"])

    if st.button("Add Student"):
        if not username or not password:
            st.error("Username and Password cannot be empty!")
            return

        if student_id in data.get('students', {}):
            st.error("Student ID already exists!")
            return

        # Save photo to cloud or local directory
        photo_path = None
        if photo:
            photo_path = f"photos/{student_id}.png"
            with open(photo_path, "wb") as f:
                f.write(photo.getbuffer())

        # Add student details
        data['students'][student_id] = {
            'name': name, 'age': age, 'course': course, 'room': room_number,
            'photo': photo_path, 'username': username, 'password': password, 'gender': gender
        }

        # Update room occupants
        data['rooms'][room_number]['occupants'].append(student_id)
        save_data(data)
        st.success(f"Student {name} added successfully!")


def update_student(data):
    student_id = st.selectbox("Select Student", list(data['students'].keys()))

    if student_id:
        student_info = data['students'][student_id]
        current_room = student_info.get('room')  # Get the current room
        gender = student_info.get('gender', 'Male')  # Get the student's gender

        # Filter rooms based on the student's gender
        available_rooms = [room for room, details in data['rooms'].items() if details['gender'] == gender]

        # Check if current_room is valid and exists in data['rooms']
        if current_room and current_room in data['rooms']:
            if 'occupants' in data['rooms'][current_room]:
                # Only attempt to remove if the student is in the current room's occupants list
                if student_id in data['rooms'][current_room]['occupants']:
                    data['rooms'][current_room]['occupants'].remove(student_id)
        else:
            st.warning(f"Current room '{current_room}' is invalid or not found.")

        # Display and update other student details
        name = st.text_input("Name", student_info.get('name', ''))
        age = st.number_input("Age", min_value=16, max_value=30, value=student_info.get('age', 18))
        course = st.text_input("Course", student_info.get('course', ''))

        # Select the current room by default if it matches the gender restriction
        room_index = available_rooms.index(current_room) if current_room in available_rooms else 0
        room_number = st.selectbox("Assign Room", available_rooms, index=room_index)

        # Get the username and password, with default values if they don't exist
        username = st.text_input("Username", student_info.get('username', ''))
        password = st.text_input("Password", type="password", value=student_info.get('password', ''))

        # Add option to upload a student photo
        uploaded_photo = st.file_uploader("Upload Student Photo", type=["png", "jpg", "jpeg"])
        photo_path = None

        if uploaded_photo is not None:
            # Create the photos directory if it doesn't exist
            photos_dir = 'photos/'
            os.makedirs(photos_dir, exist_ok=True)

            # Save the uploaded photo
            photo_path = os.path.join(photos_dir, f"{student_id}.png")
            with open(photo_path, "wb") as f:
                f.write(uploaded_photo.getbuffer())

            # Update the student photo path in the data
            data['students'][student_id]['photo'] = photo_path

        if st.button("Update Student"):
            data['students'][student_id]['name'] = name
            data['students'][student_id]['age'] = age
            data['students'][student_id]['course'] = course
            data['students'][student_id]['room'] = room_number
            data['students'][student_id]['username'] = username
            data['students'][student_id]['password'] = password

            # Add student to the new room occupants
            data['rooms'][room_number]['occupants'].append(student_id)

            save_data(data)
            st.success(f"Student {student_id} updated successfully!")

def view_student_logs(data, student_id):
    """
    Allows a student to view their activity logs.
    """
    st.subheader("My Activity Logs")

    logs = [log for log in data.get("activity_logs", []) if log["student_id"] == student_id]
    if not logs:
        st.info("No logs available.")
        return

    log_df = pd.DataFrame(logs)
    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"])
    log_df = log_df.sort_values(by="timestamp", ascending=False)

    st.dataframe(log_df)

    # Download logs as CSV
    csv_data = log_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Logs as CSV",
        data=csv_data,
        file_name=f"{student_id}_activity_logs.csv",
        mime="text/csv"
    )



def view_student_list(data):
    st.subheader("Student List")

    student_list = []
    for student_id, details in data['students'].items():
        student_list.append({
            'Student ID': student_id,
            'Name': details['name'],
            'Age': details['age'],
            'Course': details['course'],
            'Room': details['room'],
            'Gender': details.get('gender', 'Not Specified'),  # Handle missing 'gender' key
        })

    student_df = pd.DataFrame(student_list)
    st.dataframe(student_df)

def main():
    set_page_config()
    add_logo_and_title()

    data = load_data()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        # Show main page content when not logged in
        main_page_content()
        if login(data):
            st.rerun()
    else:
        st.sidebar.button("Logout", on_click=lambda: logout(data))


        if st.session_state['user_type'] == "Admin":
            admin_menu(data)
        elif st.session_state['user_type'] == "Student":
            if 'student_id' in st.session_state:
                student_menu(data, st.session_state['student_id'])
            else:
                st.error("Student ID not found. Please log in again.")
                logout()
        else:
            security_menu(data)

    save_data(data)


def main_page_content():



    st.header("Welcome to our SEC Hostel Website")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ℹ️ About Us")
        st.write(
            "Our Hostel Management System provides a seamless experience for students, administrators, and security personnel. We strive to create a comfortable and safe living environment for all our residents.")

    with col2:
        st.subheader("⭐ Features")
        st.write("• Easy room allocation")
        st.write("• Efficient complaint management")
        st.write("• Secure access control")
        st.write("• Real-time updates and notifications")

def log_student_activity(data, student_id, action, details=""):
    """
    Logs a student's activity.

    Args:
        data: The application's main data dictionary.
        student_id: The ID of the student.
        action: The type of activity (e.g., "Login", "Complaint Filed").
        details: Additional details about the activity.
    """
    if "activity_logs" not in data or not isinstance(data["activity_logs"], list):
        data["activity_logs"] = []

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "student_id": student_id,
        "action": action,
        "details": details,
        "timestamp": timestamp
    }

    data["activity_logs"].append(log_entry)
    save_data(data)



def view_activity_logs(data):
    """
    Displays activity logs for the admin to view.
    """
    st.subheader("Student Activity Logs")

    if "activity_logs" not in data or not isinstance(data["activity_logs"], list) or not data["activity_logs"]:
        st.info("No activity logs available.")
        return

    log_df = pd.DataFrame(data["activity_logs"])
    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"])
    log_df = log_df.sort_values(by="timestamp", ascending=False)

    # Filters
    student_filter = st.selectbox(
        "Filter by Student ID", options=["All"] + list(log_df["student_id"].unique())
    )
    action_filter = st.selectbox(
        "Filter by Action", options=["All"] + list(log_df["action"].unique())
    )

    # Apply filters
    if student_filter != "All":
        log_df = log_df[log_df["student_id"] == student_filter]
    if action_filter != "All":
        log_df = log_df[log_df["action"] == action_filter]

    # Display logs
    st.dataframe(log_df)

    # Download logs as CSV
    csv_data = log_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Logs as CSV",
        data=csv_data,
        file_name="student_activity_logs.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    main()
