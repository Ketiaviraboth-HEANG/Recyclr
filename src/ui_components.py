"""
Reusable UI components for the Plastic Tracker application.
"""
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import time
import base64
from rewards import Achievement, GiftCard, RewardsSystem

def display_achievement_progress(rewards_system: RewardsSystem, recycled_count: int):
    """Display visual progress towards the next achievement."""
    progress = rewards_system.get_progress_to_next_achievement(recycled_count)
    
    # Create columns for progress bar and text
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Create a circular progress indicator
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progress['percentage'],
            title={"text": "Progress"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#34D399"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 100], 'color': "#F3F4F6"}
                ]
            }
        ))
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=50, b=20),
            height=200,
            width=200
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Next Achievement")
        st.markdown(f"**{progress['achievement'].title}** {progress['achievement'].icon}")
        st.markdown(f"{progress['achievement'].description}")
        st.markdown(f"**Reward**: {progress['achievement'].discount_amount}% discount code")
        st.progress(progress['percentage'] / 100)
        st.markdown(f"**Progress**: {recycled_count} / {progress['next_milestone']} items recycled")

def display_achievement_card(achievement: Achievement, earned: bool = False):
    """Display an achievement card with an earned or locked state."""
    # Create a card-like container
    with st.container():
        # Add card styling
        st.markdown(
            f"""
            <div style="
                background-color: {'#FFFFFF' if earned else '#F3F4F6'};
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 16px;
                border: 1px solid {'#34D399' if earned else '#E5E7EB'};
                box-shadow: {'0 4px 12px rgba(0,0,0,0.08)' if earned else 'none'};
                opacity: {'1' if earned else '0.7'};
            ">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="font-size: 32px; margin-right: 12px;">{achievement.icon}</div>
                    <div>
                        <h3 style="margin: 0; color: {'#111827' if earned else '#6B7280'};">{achievement.title}</h3>
                        <p style="margin: 0; color: {'#374151' if earned else '#9CA3AF'};">{achievement.description}</p>
                    </div>
                </div>
                <div style="
                    background-color: {'#ECFDF5' if earned else '#F9FAFB'};
                    padding: 8px 12px;
                    border-radius: 8px;
                    display: inline-block;
                ">
                    <span style="color: {'#059669' if earned else '#9CA3AF'}; font-weight: 500;">
                        {'🎁 ' if earned else '🔒 '}
                        {f"{achievement.discount_amount}% discount earned!" if earned else f"Recycle {achievement.required_items} items to unlock"}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_gift_card(gift_card: GiftCard, achievement: Achievement, reward_just_earned: bool = False):
    """Display a gift card with its code and discount amount."""
    st.markdown(f"### {achievement.title} Reward")
    st.markdown(f"{achievement.description}")
    
    # Display the gift card code in a monospace font with a border
    st.code(gift_card.code, language=None)
    
    # Display discount and date info
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{gift_card.discount_amount}% OFF COUPON**")
    with col2:
        if gift_card.is_redeemed:
            st.markdown(f"*Redeemed on {gift_card.date_redeemed}*")
        else:
            st.markdown(f"*Earned on {gift_card.date_earned}*")
    
    if reward_just_earned:
        st.success("🎉 New reward earned!")
    
    st.divider()

def create_animation_placeholder():
    """Create a placeholder for animations."""
    animation_placeholder = st.empty()
    return animation_placeholder

def load_lottie_animation(animation_placeholder, animation_name: str):
    """Load a Lottie animation from URL."""
    animation_url = f"https://assets9.lottiefiles.com/packages/{animation_name}.json"
    animation_placeholder.markdown(
        f"""
        <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
        <lottie-player src="{animation_url}" background="transparent" speed="1" style="width: 100%; height: 300px;" autoplay></lottie-player>
        """,
        unsafe_allow_html=True
    )
