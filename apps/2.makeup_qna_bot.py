from langchain_openai import ChatOpenAI
import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="GlamDesk AI - Makeup Parlour Bot",
    page_icon="💄",
    layout="centered"
)

# -----------------------------
# Sample Parlour Data
# You can change this later
# -----------------------------
PARLOUR_INFO = {
    "name": "Glow Beauty Studio",
    "city": "Delhi",
    "location": "Rohini, Delhi",
    "working_hours": "10:00 AM to 8:00 PM",
    "home_service": "Available for bridal and party makeup with extra travel charges",
    "booking_advance": "30% advance payment required to confirm booking",
    "contact": "+91-9876543210"
}

SERVICES = {
    "bridal_makeup": {
        "name": "Bridal Makeup",
        "price": 15000,
        "description": "HD bridal makeup with hairstyling and draping"
    },
    "airbrush_bridal_makeup": {
        "name": "Airbrush Bridal Makeup",
        "price": 22000,
        "description": "Premium airbrush bridal makeup with hairstyling and draping"
    },
    "engagement_makeup": {
        "name": "Engagement Makeup",
        "price": 8000,
        "description": "Engagement makeup with basic hairstyling"
    },
    "party_makeup": {
        "name": "Party Makeup",
        "price": 3500,
        "description": "Party makeup for wedding, reception, birthday, or family function"
    },
    "hair_styling": {
        "name": "Hair Styling",
        "price": 1500,
        "description": "Basic to advanced hair styling"
    },
    "saree_draping": {
        "name": "Saree Draping",
        "price": 800,
        "description": "Professional saree or lehenga draping"
    },
    "pre_bridal_facial": {
        "name": "Pre-Bridal Facial",
        "price": 2500,
        "description": "Glow facial for brides before wedding"
    },
    "nail_art": {
        "name": "Nail Art",
        "price": 1200,
        "description": "Basic nail art service"
    }
}

COMBOS = {
    "bridal_basic_combo": {
        "name": "Bridal Basic Combo",
        "services": [
            "Bridal Makeup",
            "Hair Styling",
            "Saree Draping"
        ],
        "actual_price": 17300,
        "combo_price": 16000,
        "description": "Best for wedding day bridal look"
    },
    "bridal_premium_combo": {
        "name": "Bridal Premium Combo",
        "services": [
            "Airbrush Bridal Makeup",
            "Hair Styling",
            "Saree Draping",
            "Pre-Bridal Facial",
            "Nail Art"
        ],
        "actual_price": 28000,
        "combo_price": 25000,
        "description": "Premium complete bridal package"
    },
    "engagement_combo": {
        "name": "Engagement Combo",
        "services": [
            "Engagement Makeup",
            "Hair Styling",
            "Saree Draping"
        ],
        "actual_price": 10300,
        "combo_price": 9500,
        "description": "Perfect for engagement or ring ceremony"
    },
    "party_ready_combo": {
        "name": "Party Ready Combo",
        "services": [
            "Party Makeup",
            "Hair Styling"
        ],
        "actual_price": 5000,
        "combo_price": 4500,
        "description": "Best for party, reception, birthday, or family function"
    }
}

# -----------------------------
# Helper Functions
# -----------------------------
def format_services():
    text = ""
    for service in SERVICES.values():
        text += f"""
Service: {service['name']}
Price: ₹{service['price']}
Description: {service['description']}
"""
    return text


def format_combos():
    text = ""
    for combo in COMBOS.values():
        services = ", ".join(combo["services"])
        text += f"""
Combo Name: {combo['name']}
Included Services: {services}
Actual Price: ₹{combo['actual_price']}
Combo Price: ₹{combo['combo_price']}
Description: {combo['description']}
"""
    return text


def get_system_prompt():
    services_text = format_services()
    combos_text = format_combos()

    return f"""
You are an AI booking assistant for a makeup parlour.

Business Details:
Name: {PARLOUR_INFO['name']}
City: {PARLOUR_INFO['city']}
Location: {PARLOUR_INFO['location']}
Working Hours: {PARLOUR_INFO['working_hours']}
Home Service: {PARLOUR_INFO['home_service']}
Booking Advance: {PARLOUR_INFO['booking_advance']}
Contact: {PARLOUR_INFO['contact']}

Services and Prices:
{services_text}

Combo Packages:
{combos_text}

Your job:
1. Answer customer questions politely.
2. Help customers choose the right makeup package.
3. Ask for important booking details:
   - Customer name
   - Phone number
   - Event type
   - Event date
   - Event location
   - Required service
   - Budget
4. Recommend combos when suitable.
5. Do not make fake availability confirmation.
6. If customer asks for availability, say:
   "Please share your event date and location. Our team will confirm availability shortly."
7. If customer wants to book, ask for name, phone number, event date, event type, and location.
8. Keep replies short, friendly, and professional.
9. Use Indian Rupees.
10. Do not give medical or skin disease advice.
"""


def get_llm_response(user_message):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.4
    )

    messages = [
        {
            "role": "system",
            "content": get_system_prompt()
        }
    ]

    for chat in st.session_state.chat_history:
        messages.append(chat)

    messages.append({
        "role": "user",
        "content": user_message
    })

    response = llm.invoke(messages)

    return response.content


def recommend_combo(event_type, budget):
    event_type = event_type.lower()

    if "bridal" in event_type or "wedding" in event_type:
        if budget >= 25000:
            return COMBOS["bridal_premium_combo"]
        return COMBOS["bridal_basic_combo"]

    if "engagement" in event_type or "ring" in event_type:
        return COMBOS["engagement_combo"]

    if "party" in event_type or "reception" in event_type or "birthday" in event_type:
        return COMBOS["party_ready_combo"]

    return None


# -----------------------------
# Session State
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "leads" not in st.session_state:
    st.session_state.leads = []

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("💄 GlamDesk AI")
st.sidebar.write("AI Booking Assistant for Makeup Parlour")

st.sidebar.divider()

st.sidebar.subheader("Parlour Details")
st.sidebar.write(f"**Name:** {PARLOUR_INFO['name']}")
st.sidebar.write(f"**Location:** {PARLOUR_INFO['location']}")
st.sidebar.write(f"**Timing:** {PARLOUR_INFO['working_hours']}")
st.sidebar.write(f"**Contact:** {PARLOUR_INFO['contact']}")

st.sidebar.divider()

if st.sidebar.button("Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

# -----------------------------
# Main UI
# -----------------------------
st.title("💄 GlamDesk AI")
st.caption("AI Makeup Parlour Booking Assistant")

tab1, tab2, tab3, tab4 = st.tabs([
    "Chatbot",
    "Services",
    "Combo Packages",
    "Lead Capture"
])

# -----------------------------
# Tab 1: Chatbot
# -----------------------------
with tab1:
    st.subheader("Chat with AI Assistant")

    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            with st.chat_message("user"):
                st.write(chat["content"])
        elif chat["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(chat["content"])

    user_input = st.chat_input("Ask about bridal makeup, party makeup, packages, price...")

    if user_input:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                ai_response = get_llm_response(user_input)
                st.write(ai_response)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": ai_response
        })

# -----------------------------
# Tab 2: Services
# -----------------------------
with tab2:
    st.subheader("Available Services")

    for service in SERVICES.values():
        with st.container(border=True):
            st.markdown(f"### {service['name']}")
            st.write(service["description"])
            st.markdown(f"**Price:** ₹{service['price']}")

# -----------------------------
# Tab 3: Combo Packages
# -----------------------------
with tab3:
    st.subheader("Combo Packages")

    for combo in COMBOS.values():
        saving = combo["actual_price"] - combo["combo_price"]

        with st.container(border=True):
            st.markdown(f"### {combo['name']}")
            st.write(combo["description"])
            st.write("**Included Services:**")
            for item in combo["services"]:
                st.write(f"- {item}")

            st.markdown(f"**Actual Price:** ₹{combo['actual_price']}")
            st.markdown(f"**Combo Price:** ₹{combo['combo_price']}")
            st.success(f"You save ₹{saving}")

# -----------------------------
# Tab 4: Lead Capture
# -----------------------------
with tab4:
    st.subheader("Capture Customer Lead")

    with st.form("lead_form"):
        customer_name = st.text_input("Customer Name")
        phone_number = st.text_input("Phone Number")
        event_type = st.selectbox(
            "Event Type",
            [
                "Bridal Makeup",
                "Engagement",
                "Party",
                "Reception",
                "Birthday",
                "Other"
            ]
        )
        event_date = st.date_input("Event Date")
        event_location = st.text_input("Event Location")
        budget = st.number_input("Budget", min_value=0, step=500)
        notes = st.text_area("Extra Notes")

        submitted = st.form_submit_button("Save Lead")

        if submitted:
            recommended_combo = recommend_combo(event_type, budget)

            lead = {
                "customer_name": customer_name,
                "phone_number": phone_number,
                "event_type": event_type,
                "event_date": str(event_date),
                "event_location": event_location,
                "budget": budget,
                "notes": notes,
                "recommended_combo": recommended_combo["name"] if recommended_combo else "No combo found",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            st.session_state.leads.append(lead)

            st.success("Lead saved successfully!")

            if recommended_combo:
                st.info(
                    f"Recommended Combo: {recommended_combo['name']} "
                    f"at ₹{recommended_combo['combo_price']}"
                )

    st.divider()

    st.subheader("Saved Leads")

    if len(st.session_state.leads) == 0:
        st.info("No leads saved yet.")
    else:
        for index, lead in enumerate(st.session_state.leads, start=1):
            with st.container(border=True):
                st.markdown(f"### Lead #{index}")
                st.write(f"**Name:** {lead['customer_name']}")
                st.write(f"**Phone:** {lead['phone_number']}")
                st.write(f"**Event:** {lead['event_type']}")
                st.write(f"**Date:** {lead['event_date']}")
                st.write(f"**Location:** {lead['event_location']}")
                st.write(f"**Budget:** ₹{lead['budget']}")
                st.write(f"**Recommended Combo:** {lead['recommended_combo']}")
                st.write(f"**Notes:** {lead['notes']}")
                st.write(f"**Created At:** {lead['created_at']}")