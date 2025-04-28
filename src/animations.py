"""
Animation utilities for the Plastic Tracker application.
"""
import streamlit as st
import json
import time
from typing import Dict, Any

def get_confetti_html():
    """Get HTML/JS code for confetti animation."""
    return """
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <script>
    function launchConfetti() {
        var duration = 3000;
        var end = Date.now() + duration;
        
        (function frame() {
            // Launch confetti from the bottom
            confetti({
                particleCount: 2,
                angle: 60,
                spread: 55,
                origin: { x: 0, y: 1 },
                colors: ['#34D399', '#60A5FA', '#F59E0B']
            });
            
            confetti({
                particleCount: 2,
                angle: 120,
                spread: 55,
                origin: { x: 1, y: 1 },
                colors: ['#34D399', '#60A5FA', '#F59E0B']
            });
            
            if (Date.now() < end) {
                requestAnimationFrame(frame);
            }
        }());
    }
    
    // Launch a large burst initially
    confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#34D399', '#60A5FA', '#F59E0B', '#A78BFA']
    });
    
    // Start the continuous effect
    setTimeout(launchConfetti, 500);
    </script>
    """

def get_achievement_animation(achievement_title, achievement_icon):
    """Get HTML/JS code for achievement unlocked animation."""
    return f"""
    <div id="achievement-popup" style="
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: rgba(0,0,0,0.8);
        border-radius: 16px;
        padding: 32px;
        z-index: 1000;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        width: 300px;
        animation: popup 0.5s ease-out forwards;
    ">
        <div style="font-size: 64px; margin-bottom: 16px;">{achievement_icon}</div>
        <div style="font-size: 24px; font-weight: bold; margin-bottom: 8px;">Achievement Unlocked!</div>
        <div style="font-size: 18px; opacity: 0.9;">{achievement_title}</div>
    </div>
    
    <style>
    @keyframes popup {
        0% {{ transform: translate(-50%, -50%) scale(0.5); opacity: 0; }}
        50% {{ transform: translate(-50%, -50%) scale(1.1); opacity: 1; }}
        100% {{ transform: translate(-50%, -50%) scale(1); opacity: 1; }}
    }
    </style>
    
    <script>
    setTimeout(function() {{
        document.getElementById('achievement-popup').style.animation = 'popout 0.5s ease-in forwards';
    }}, 3000);
    </script>
    
    <style>
    @keyframes popout {
        0% {{ transform: translate(-50%, -50%) scale(1); opacity: 1; }}
        100% {{ transform: translate(-50%, -50%) scale(0.5); opacity: 0; }}
    }
    </style>
    """

def get_gift_card_reveal_animation():
    """Get HTML/JS code for gift card reveal animation."""
    return """
    <style>
    @keyframes flipCard {
        0% { transform: rotateY(180deg); opacity: 0; }
        100% { transform: rotateY(0deg); opacity: 1; }
    }
    
    .gift-card-container {
        perspective: 1000px;
    }
    
    .gift-card {
        animation: flipCard 1s ease-out forwards;
        transform-style: preserve-3d;
    }
    </style>
    """

def get_progress_bar_fill_animation():
    """Get HTML/JS code for progress bar filling animation."""
    return """
    <style>
    @keyframes fillProgress {
        0% { width: 0; }
        100% { width: 100%; }
    }
    
    .animated-progress-bar {
        height: 8px;
        background-color: #E5E7EB;
        border-radius: 4px;
        overflow: hidden;
        position: relative;
    }
    
    .animated-progress-bar-fill {
        height: 100%;
        background-color: #34D399;
        border-radius: 4px;
        position: absolute;
        top: 0;
        left: 0;
        animation: fillProgress 1.5s ease-out forwards;
    }
    </style>
    """

def get_floating_icons_animation():
    """Get HTML/JS code for floating environmental icons animation."""
    return """
    <style>
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .floating-icon {
        font-size: 24px;
        position: absolute;
        opacity: 0.5;
        animation: float 3s ease-in-out infinite;
    }
    </style>
    
    <div id="floating-icons-container" style="
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        overflow: hidden;
        z-index: -1;
    ">
    </div>
    
    <script>
    const icons = ['🌱', '♻️', '🌿', '🌳', '🌎', '💧'];
    const container = document.getElementById('floating-icons-container');
    const containerWidth = container.offsetWidth;
    const containerHeight = container.offsetHeight;
    
    for (let i = 0; i < 12; i++) {
        const icon = document.createElement('div');
        icon.className = 'floating-icon';
        icon.textContent = icons[Math.floor(Math.random() * icons.length)];
        icon.style.left = `${Math.random() * 100}%`;
        icon.style.top = `${Math.random() * 100}%`;
        icon.style.animationDelay = `${Math.random() * 2}s`;
        container.appendChild(icon);
    }
    </script>
    """

def get_popup_notification(title, message, icon="✅", theme="success"):
    """
    Generate HTML for a popup notification.
    
    Args:
        title: Title of the notification
        message: Message content
        icon: Emoji icon to display
        theme: "success", "warning", or "error"
    """
    colors = {
        "success": {"bg": "#ECFDF5", "border": "#34D399", "text": "#059669"},
        "warning": {"bg": "#FFFBEB", "border": "#F59E0B", "text": "#B45309"},
        "error": {"bg": "#FEF2F2", "border": "#EF4444", "text": "#B91C1C"}
    }
    
    theme_colors = colors.get(theme, colors["success"])
    
    return f"""
    <div id="notification-popup" style="
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: {theme_colors['bg']};
        border-left: 4px solid {theme_colors['border']};
        border-radius: 4px;
        padding: 16px;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        z-index: 1000;
        transform: translateX(400px);
        opacity: 0;
        transition: transform 0.3s ease-out, opacity 0.3s ease-out;
    ">
        <div style="display: flex; align-items: center;">
            <div style="font-size: 24px; margin-right: 12px;">{icon}</div>
            <div>
                <div style="font-weight: bold; color: {theme_colors['text']};">{title}</div>
                <div style="color: #4B5563;">{message}</div>
            </div>
        </div>
    </div>
    
    <script>
    // Show the notification
    setTimeout(function() {{
        const popup = document.getElementById('notification-popup');
        popup.style.transform = 'translateX(0)';
        popup.style.opacity = '1';
        
        // Hide the notification after 5 seconds
        setTimeout(function() {{
            popup.style.transform = 'translateX(400px)';
            popup.style.opacity = '0';
        }}, 5000);
    }}, 500);
    </script>
    """

def countdown_timer(seconds, callback=None):
    """
    Display a countdown timer and execute callback when finished.
    
    Args:
        seconds: Number of seconds to count down
        callback: Function to call when timer completes
    """
    placeholder = st.empty()
    
    for remaining in range(seconds, 0, -1):
        placeholder.markdown(f"<h1 style='text-align: center; font-size: 48px;'>{remaining}</h1>", unsafe_allow_html=True)
        time.sleep(1)
    
    placeholder.empty()
    
    if callback:
        callback()

def celebration_animation():
    """Display a celebration animation with emojis and effects."""
    return """
    <div id="celebration" style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        pointer-events: none;
    ">
        <div id="emoji-container" style="
            position: absolute;
            width: 100%;
            height: 100%;
            overflow: hidden;
        "></div>
    </div>
    
    <script>
    function createEmoji() {
        const emojis = ['🌱', '♻️', '🌿', '🌳', '🌎', '💧', '🎉', '🎊', '✨'];
        const emoji = document.createElement('div');
        emoji.className = 'celebration-emoji';
        emoji.textContent = emojis[Math.floor(Math.random() * emojis.length)];
        emoji.style.position = 'absolute';
        emoji.style.left = `${Math.random() * 100}%`;
        emoji.style.top = '-50px';
        emoji.style.fontSize = `${Math.random() * 30 + 20}px`;
        emoji.style.opacity = '0.8';
        emoji.style.transform = `rotate(${Math.random() * 60 - 30}deg)`;
        
        const animDuration = Math.random() * 3 + 2;
        emoji.style.animation = `fall ${animDuration}s linear forwards`;
        
        document.getElementById('emoji-container').appendChild(emoji);
        
        setTimeout(() => {
            emoji.remove();
        }, animDuration * 1000);
    }
    
    document.head.insertAdjacentHTML('beforeend', `
        <style>
        @keyframes fall {
            0% { transform: translateY(0) rotate(0deg); opacity: 0.8; }
            80% { opacity: 0.8; }
            100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
        }
        </style>
    `);
    
    // Create emojis continually
    for (let i = 0; i < 50; i++) {
        setTimeout(createEmoji, i * 100);
    }
    </script>
    """