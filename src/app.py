"""
Main Streamlit application for the Plastic Tracker with rewards system.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plastic_tracker import PlasticTracker
from rewards import RewardsSystem, Achievement, GiftCard
import ui_components
import os
from datetime import datetime
import tempfile
import time
from typing import Dict, List, Any, Optional

# Initialize the tracker and rewards system
@st.cache_resource
def get_tracker():
    return PlasticTracker()

@st.cache_resource
def get_rewards_system():
    return RewardsSystem()

# Page configuration
st.set_page_config(
    page_title="Recyclr - Plastic Tracking System",
    page_icon="♻️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stProgress .st-bo {
        background-color: #34D399;
    }
    .recycled {
        color: #10B981;
        font-weight: bold;
    }
    .not-recycled {
        color: #EF4444;
        font-weight: bold;
    }
    .reward-header {
        background-color: #F9FAFB;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize tracker and rewards system
tracker = get_tracker()
rewards_system = get_rewards_system()

# Check for earned achievements based on recycled items count
stats = tracker.get_stats()
recycled_count = stats['recycled_plastics']

# Check if session state variables exist, initialize if not
if 'just_earned_achievement' not in st.session_state:
    st.session_state.just_earned_achievement = None
    st.session_state.show_animation = False

# Check for new achievements
new_achievement = rewards_system.check_achievements(recycled_count)
if new_achievement:
    st.session_state.just_earned_achievement = new_achievement
    st.session_state.show_animation = True

# Sidebar
st.sidebar.title("♻️ Recyclr")
st.sidebar.markdown("Track and manage your single-use plastic consumption")

# Navigation
page = st.sidebar.radio("Navigation", ["Dashboard", "Upload Receipt", "My Items", "Rewards"])

if page == "Dashboard":
    st.title("Dashboard")
    
    # Get statistics
    stats = tracker.get_stats()
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Plastic Items", stats['total_plastics'])
    
    with col2:
        recycling_rate = (stats['recycled_plastics'] / stats['total_plastics'] * 100) if stats['total_plastics'] > 0 else 0
        st.metric("Recycling Rate", f"{recycling_rate:.1f}%")
    
    with col3:
        st.metric("Carbon Saved", f"{stats['carbon_saved']:.1f}g CO2")
    
    with col4:
        st.metric("Tree Equivalent", f"{stats['tree_equivalent']:.3f} trees")
    
    # Charts
    st.subheader("Plastic Items by Category")
    
    # Prepare data for category chart
    categories = {}
    for item in tracker.items:
        if item.category not in categories:
            categories[item.category] = {'total': 0, 'recycled': 0}
        categories[item.category]['total'] += 1
        if item.recycled:
            categories[item.category]['recycled'] += 1
    
    if categories:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Not Recycled',
            x=list(categories.keys()),
            y=[cat['total'] - cat['recycled'] for cat in categories.values()],
            marker_color='#EF4444'
        ))
        fig.add_trace(go.Bar(
            name='Recycled',
            x=list(categories.keys()),
            y=[cat['recycled'] for cat in categories.values()],
            marker_color='#34D399'
        ))
        
        fig.update_layout(
            barmode='stack',
            plot_bgcolor='white',
            margin=dict(t=0, b=0, l=0, r=0),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No plastic items tracked yet. Upload a receipt to get started!")
    
    # Show achievements progress
    if stats['total_plastics'] > 0:
        st.subheader("Achievements Progress")
        ui_components.display_achievement_progress(rewards_system, recycled_count)

elif page == "Upload Receipt":
    st.title("Upload Receipt")
    
    uploaded_file = st.file_uploader("Choose a receipt image", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            with st.spinner('Processing receipt...'):
                # Process the receipt
                plastic_items = tracker.process_receipt(tmp_path)
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            if plastic_items:
                st.success(f"Detected {len(plastic_items)} plastic items!")
                
                # Display detected items
                for item in plastic_items:
                    st.write(f"🔍 {item.name} ({item.category})")
                    st.write(f"   Carbon footprint: {item.carbon_footprint:.1f}g CO2")
            else:
                st.info("No plastic items detected in this receipt.")
                
        except Exception as e:
            st.error(f"Error processing receipt: {str(e)}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

elif page == "My Items":
    st.title("My Items")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Recycled", "Not Recycled"]
        )
    with col2:
        filter_category = st.selectbox(
            "Filter by category",
            ["All"] + list(tracker.plastic_keywords.keys())
        )
    
    # Filter items
    filtered_items = tracker.items
    if filter_status != "All":
        filtered_items = [
            item for item in filtered_items
            if (filter_status == "Recycled") == item.recycled
        ]
    if filter_category != "All":
        filtered_items = [
            item for item in filtered_items
            if item.category == filter_category.lower()
        ]
    
    # Display items
    for item in filtered_items:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{item.name}**")
                st.write(f"Category: {item.category}")
            
            with col2:
                st.write("Status:")
                if item.recycled:
                    st.markdown('<span class="recycled">✓ Recycled</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="not-recycled">✗ Not Recycled</span>', unsafe_allow_html=True)
            
            with col3:
                if not item.recycled:
                    if st.button("Mark as Recycled", key=item.id):
                        tracker.mark_as_recycled(item.id)
                        
                        # Check for new achievements after recycling
                        stats = tracker.get_stats()
                        recycled_count = stats['recycled_plastics']
                        new_achievement = rewards_system.check_achievements(recycled_count)
                        
                        if new_achievement:
                            st.session_state.just_earned_achievement = new_achievement
                            st.session_state.show_animation = True
                        
                        st.rerun()
            
            st.write(f"Added: {item.date}")
            st.write(f"Carbon footprint: {item.carbon_footprint:.1f}g CO2")
            st.divider()

elif page == "Rewards":
    st.title("Rewards & Achievements")
    
    # Stats summary
    stats = tracker.get_stats()
    recycled_count = stats['recycled_plastics']
    
    # Rewards dashboard header
    st.markdown(
        """
        <div class="reward-header">
            <h3 style="margin:0; color:#059669;">♻️ Recycling Rewards</h3>
            <p style="margin:0;">Earn discount codes by recycling plastic items</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Progress to next reward
    ui_components.display_achievement_progress(rewards_system, recycled_count)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Available Rewards", "Achievement Progress", "Redeem Code"])
    
    with tab1:
        st.subheader("Your Reward Codes")
        
        # Get active gift cards
        active_gift_cards = rewards_system.get_active_gift_cards()
        redeemed_gift_cards = rewards_system.get_redeemed_gift_cards()
        
        if active_gift_cards:
            for gift_card in active_gift_cards:
                achievement = rewards_system.get_achievement_by_id(gift_card.achievement_id)
                # Check if this is the newly earned reward
                is_new = (st.session_state.just_earned_achievement and 
                          st.session_state.just_earned_achievement.id == gift_card.achievement_id)
                ui_components.display_gift_card(gift_card, achievement, is_new)
        else:
            st.info("You don't have any available reward codes yet. Recycle more plastic items to earn rewards!")
        
        if redeemed_gift_cards:
            st.subheader("Redeemed Codes")
            for gift_card in redeemed_gift_cards[:3]:  # Show only the most recent ones
                achievement = rewards_system.get_achievement_by_id(gift_card.achievement_id)
                ui_components.display_gift_card(gift_card, achievement)
            
            if len(redeemed_gift_cards) > 3:
                st.markdown(f"*+{len(redeemed_gift_cards) - 3} more redeemed codes*")
    
    with tab2:
        st.subheader("Achievements")
        
        # Get earned and unearned achievements
        earned_achievements = rewards_system.get_earned_achievements_list()
        all_achievements = rewards_system.achievements
        unearned_achievements = [a for a in all_achievements if a.id not in [ea.id for ea in earned_achievements]]
        
        # Display earned achievements
        if earned_achievements:
            st.markdown("### Earned")
            for achievement in earned_achievements:
                ui_components.display_achievement_card(achievement, earned=True)
        
        # Display unearned achievements
        if unearned_achievements:
            st.markdown("### Locked")
            for achievement in unearned_achievements:
                ui_components.display_achievement_card(achievement, earned=False)
    
    with tab3:
        st.subheader("Redeem a Code")
        
        # Redeem code form
        with st.form("redeem_code_form"):
            redemption_code = st.text_input("Enter your gift card code", max_chars=6)
            submit_button = st.form_submit_button("Redeem Code")
            
            if submit_button and redemption_code:
                # Try to redeem the code
                if rewards_system.redeem_gift_card(redemption_code):
                    st.success("Code redeemed successfully! Your discount has been applied to your account.")
                    # Adding a small delay to let the success message show
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid code or code already redeemed. Please check and try again.")
        
        # Instructions on how to use codes
        st.markdown("""
        ### How to use your reward codes
        
        1. Copy the code from your available rewards
        2. Visit our store at [recyclr-store.example.com](https://example.com)
        3. Add items to your cart
        4. Enter the code at checkout to receive your discount
        5. Come back here to earn more rewards by recycling!
        """)

# Handle just_earned_achievement reset after navigation
if page != "Rewards" and st.session_state.just_earned_achievement:
    st.session_state.just_earned_achievement = None

# Run the app with command: streamlit run app.py