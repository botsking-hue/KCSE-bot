# bot.py
"""
🎮 SOCCERFORUM SUPER BOT - Main Bot File
⚽ Tournaments • 💬 Forums • 👥 Social • 👤 Profiles
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, ConversationHandler

from config import Config
from datamanager import SuperDatabase


# ==================== CARD SYSTEM ====================
class CardSystem:
    def __init__(self, db):
        self.db = db

    def truncate_text(self, text: str, max_length: int = Config.TRUNCATE_LENGTH) -> str:
        """Truncate text with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def format_progress_bar(self, percentage: float, length: int = Config.PROGRESS_BAR_LENGTH) -> str:
        """Create visual progress bar"""
        filled = int(percentage / 100 * length)
        empty = length - filled
        return "🟩" * filled + "⬜" * empty

    # ==================== MAIN MENU CARD ====================
    async def create_main_menu(self, user_id: int) -> Dict[str, Any]:
        """Create main menu card"""
        user = self.db.get_user(user_id)
        stats = self.db.get_quick_stats()
        
        menu_text = (
            f"🎮 *Welcome to SoccerForum, {user.get('username', 'Player')}!* 🏆\n\n"
            f"📊 *Community Stats:*\n"
            f"👥 {stats.get('total_users', 0)} members • 📝 {stats.get('total_threads', 0)} threads\n"
            f"⚽ {stats.get('active_tournaments', 0)} active tournaments\n\n"
            "✨ *Choose your action below:*"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("⚽ Tournaments", callback_data="tournaments"),
                InlineKeyboardButton("💬 Forums", callback_data="forums")
            ],
            [
                InlineKeyboardButton("👥 Social", callback_data="social"),
                InlineKeyboardButton("👤 Profile", callback_data="profile")
            ],
            [
                InlineKeyboardButton("🎯 Quick Play", callback_data="quick_play"),
                InlineKeyboardButton("📊 Leaderboard", callback_data="leaderboard")
            ],
            [
                InlineKeyboardButton("🆘 Help", callback_data="help"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ]
        ]
        
        return {
            'text': menu_text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    # ==================== TOURNAMENT CARDS ====================
    async def create_tournaments_menu(self, user_id: int) -> Dict[str, Any]:
        """Create tournaments menu card"""
        tournaments = self.db.get_tournaments(status='pending', limit=6)
        stats = self.db.get_quick_stats()
        
        menu_text = (
            "⚽ *Tournament Hub* 🏆\n\n"
            f"🎯 *Active: {stats.get('active_tournaments', 0)}* • ⏳ *Pending: {len(tournaments)}*\n\n"
            "Join competitive tournaments and showcase your skills!\n"
        )
        
        keyboard = []
        
        # Add tournament buttons
        for tournament in tournaments:
            status_emoji = "🟢" if tournament['status'] == 'active' else "🟡"
            button_text = f"{status_emoji} {self.truncate_text(tournament['name'])}"
            keyboard.append([
                InlineKeyboardButton(button_text, callback_data=f"tournament_view_{tournament['id']}")
            ])
        
        # Action buttons
        keyboard.extend([
            [InlineKeyboardButton("➕ Create Tournament", callback_data="tournament_create")],
            [InlineKeyboardButton("📋 My Tournaments", callback_data="tournament_my")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="tournament_leaderboard")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="menu")]
        ])
        
        return {
            'text': menu_text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    async def create_tournament_card(self, user_id: int, tournament_id: int) -> Dict[str, Any]:
        """Create detailed tournament card"""
        tournament = self.db.get_tournament(tournament_id)
        if not tournament:
            return await self.create_error_card("Tournament not found")
        
        participants = self.db.get_tournament_participants(tournament_id)
        user_joined = user_id in participants
        
        # Status emoji
        status_emoji = {
            'pending': '🟡',
            'active': '🟢', 
            'completed': '✅',
            'cancelled': '❌'
        }.get(tournament['status'], '⚽')
        
        card_text = (
            f"{status_emoji} *{tournament['name']}*\n\n"
            f"🎮 *Game:* {tournament['game_version']}\n"
            f"👥 *Teams:* {len(participants)}/{tournament['max_teams']}\n"
            f"🏅 *Prize:* {tournament['prize_pool']}\n"
            f"📝 *Status:* {tournament['status'].title()}\n"
            f"👤 *Creator:* {tournament.get('creator_name', 'Unknown')}\n\n"
            f"*Description:*\n{tournament['description']}\n\n"
        )
        
        # Add participants preview
        if participants:
            card_text += "👥 *Participants:*\n"
            for i, participant_id in enumerate(participants[:5], 1):
                user = self.db.get_user(participant_id)
                card_text += f"{i}. {user.get('username', 'Player')}\n"
            if len(participants) > 5:
                card_text += f"... and {len(participants) - 5} more\n"
        
        keyboard = []
        
        # Join/Leave button
        if tournament['status'] == 'pending':
            if user_joined:
                keyboard.append([InlineKeyboardButton("❌ Leave Tournament", callback_data=f"tournament_leave_{tournament_id}")])
            else:
                keyboard.append([InlineKeyboardButton("✅ Join Tournament", callback_data=f"tournament_join_{tournament_id}")])
        
        # Additional buttons
        keyboard.extend([
            [InlineKeyboardButton("📋 Fixtures", callback_data=f"tournament_fixtures_{tournament_id}")],
            [InlineKeyboardButton("👥 Participants", callback_data=f"tournament_participants_{tournament_id}")],
            [InlineKeyboardButton("⚽ Tournaments", callback_data="tournaments")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="menu")]
        ])
        
        return {
            'text': card_text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    # ==================== FORUM CARDS ====================
    async def create_forums_menu(self, user_id: int) -> Dict[str, Any]:
        """Create forums menu card"""
        forums = self.db.get_forums(featured_only=True)
        user_follows = self.db.get_user_forum_follows(user_id)
        stats = self.db.get_quick_stats()
        
        menu_text = (
            "💬 *Forum Hub* 📚\n\n"
            f"📊 {stats.get('total_threads', 0)} threads • 💭 {stats.get('total_replies', 0)} replies\n\n"
            "Join discussions about your favorite football games!\n"
        )
        
        keyboard = []
        
        # Create forum cards with icons and stats
        for forum in forums:
            follow_emoji = "❤️" if forum['id'] in user_follows else "💙"
            button_text = f"{forum['icon']} {self.truncate_text(forum['name'])} ({forum['thread_count']}) {follow_emoji}"
            keyboard.append([
                InlineKeyboardButton(button_text, callback_data=f"forum_view_{forum['id']}")
            ])
        
        # Action buttons
        keyboard.extend([
            [InlineKeyboardButton("🔍 Search Threads", callback_data="forum_search")],
            [InlineKeyboardButton("📚 My Forums", callback_data="forum_my")],
            [InlineKeyboardButton("🔥 Popular", callback_data="forum_popular")],
            [InlineKeyboardButton("🕒 Recent", callback_data="forum_recent")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="menu")]
        ])
        
        return {
            'text': menu_text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    async def create_forum_card(self, user_id: int, forum_id: int) -> Dict[str, Any]:
        """Create detailed forum card"""
        forum = self.db.get_forum(forum_id)
        if not forum:
            return await self.create_error_card("Forum not found")
        
        threads = self.db.get_threads(forum_id=forum_id, limit=5)
        user_follows = self.db.get_user_forum_follows(user_id)
        is_following = forum_id in user_follows
        
        # Create visual forum card
        card_text = (
            f"{forum['icon']} *{forum['name']}*\n\n"
            f"📖 *Category:* {forum['category'].title()}\n"
            f"📝 *Threads:* {forum['thread_count']}\n"
            f"💬 *Replies:* {forum['reply_count']}\n"
            f"❤️ *Status:* {'Following' if is_following else 'Not following'}\n\n"
            f"*Description:*\n{forum['description']}\n\n"
        )
        
        # Add recent threads
        if threads:
            card_text += "📝 *Recent Threads:*\n"
            for thread in threads[:3]:
                card_text += f"• {self.truncate_text(thread['title'])} by {thread['creator_name']} ({thread['reply_count']}💬)\n"
            card_text += "\n"
        
        keyboard = []
        
        # Follow/Unfollow button
        if is_following:
            keyboard.append([InlineKeyboardButton("💔 Unfollow", callback_data=f"forum_unfollow_{forum_id}")])
        else:
            keyboard.append([InlineKeyboardButton("❤️ Follow", callback_data=f"forum_follow_{forum_id}")])
        
        # Thread actions
        keyboard.extend([
            [InlineKeyboardButton("📝 New Thread", callback_data=f"thread_create_{forum_id}")],
            [InlineKeyboardButton("📚 Browse Threads", callback_data=f"forum_threads_{forum_id}")],
            [InlineKeyboardButton("💬 Forums", callback_data="forums")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="menu")]
        ])
        
        return {
            'text': card_text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    async def create_thread_card(self, user_id: int, thread_id: int) -> Dict[str, Any]:
        """Create thread card"""
        thread = self.db.get_thread(thread_id)
        if not thread:
            return await self.create_error_card("Thread not found")
        
        replies = self.db.get_replies(thread_id)
        
        card_text = (
            f"📄 *{thread['title']}*\n\n"
            f"*Forum:* {thread['forum_name']}\n"
            f"*Author:* {thread['creator_name']}\n"
            f"*Replies:* {thread['reply_count']}\n"
            f"*Views:* {thread['views']}\n"
            f"*Created:* {thread['created_at'][:16]}\n\n"
            f"*Content:*\n{thread['content']}\n\n"
        )
        
        # Add recent replies preview
        if replies:
            card_text += "--- *Recent Replies* ---\n"
            for reply in replies[:3]:
                card_text += f"\n👤 *{reply['username']}:*\n{reply['content'][:100]}"
                if len(reply['content']) > 100:
                    card_text += "..."
                card_text += f"\n🕒 {reply['created_at'][:16]}\n"
        
        if len(replies) > 3:
            card_text += f"\n... and {len(replies) - 3} more replies"
        
        keyboard = [
            [InlineKeyboardButton("💬 Reply", callback_data=f"reply_create_{thread_id}")],
            [InlineKeyboardButton("📋 All Replies", callback_data=f"thread_replies_{thread_id}")],
            [InlineKeyboardButton("🔙 Forum", callback_data=f"forum_view_{thread['forum_id']}")],
            [InlineKeyboardButton("💬 Forums", callback_data="forums")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
        ]
        
        return {
            'text': card_text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    # ==================== SOCIAL CARDS ====================
    async def create_social_menu(self, user_id: int) -> Dict[str, Any]:
        """Create social menu card"""
        user = self.db.get_user(user_id)
        stats = self.db.get_quick_stats()
        
        menu_text = (
            "👥 *Social Hub* 🌐\n\n"
            f"🤝 Connect with {stats.get('total_users', 0)} football fans!\n\n"
            "Find friends, follow players, and build your network."
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🔍 Find Players", callback_data="social_find"),
                InlineKeyboardButton("👑 Leaderboard", callback_data="social_leaderboard")
            ],
            [
                InlineKeyboardButton("❤️ Following", callback_data="social_following"),
                InlineKeyboardButton("👤 Followers", callback_data="social_followers")
            ],
            [
                InlineKeyboardButton("🎯 Recommended", callback_data="social_recommended"),
                InlineKeyboardButton("🌟 Top Contributors", callback_data="social_top")
            ],
            [
                InlineKeyboardButton("🔙 Main Menu", callback_data="menu")
            ]
        ]
        
        return {
            'text': menu_text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    async def create_user_profile_card(self, user_id: int, target_user_id: int) -> Dict[str, Any]:
        """Create user profile card"""
        user = self.db.get_user(target_user_id)
        if not user:
            return await self.create_error_card("User not found")
        
        badges = self.db.get_user_badges(target_user_id)
        is_following = target_user_id in self.db.get_user_following(user_id)
        is_self = user_id == target_user_id
        
        # Calculate progress to next level
        current_level_xp = (user['level'] - 1) * 100
        next_level_xp = user['level'] * 100
        xp_progress = user['experience'] - current_level_xp
        xp_required = next_level_xp - current_level_xp
        progress_percent = (xp_progress / xp_required) * 100 if xp_required > 0 else 100
        
        # Create progress bar
        progress_bar = self.format_progress_bar(progress_percent)
        
        card_text = (
            f"👤 *{user['username']}* {'(You)' if is_self else ''}\n\n"
            f"🎯 *Level {user['level']}* • ⭐ {user['reputation']} Rep\n"
            f"{progress_bar} {progress_percent:.0f}%\n"
            f"📝 {user['threads_created']} threads • 💬 {user['replies_posted']} replies\n"
            f"⚽ {user['tournaments_joined']} tournaments\n"
            f"❤️ {user['following_count']} following • 👤 {user['follower_count']} followers\n\n"
        )
        
        # Add badges section
        if badges:
            card_text += f"🏆 *Badges ({len(badges)}):*\n"
            for badge in badges[:3]:
                card_text += f"• {badge.get('badge_name', 'Achievement')}\n"
            if len(badges) > 3:
                card_text += f"... and {len(badges) - 3} more\n"
        else:
            card_text += "🎯 *No badges yet!* Be active to earn achievements.\n"
        
        keyboard = []
        
        if not is_self:
            if is_following:
                keyboard.append([InlineKeyboardButton("💔 Unfollow", callback_data=f"social_unfollow_{target_user_id}")])
            else:
                keyboard.append([InlineKeyboardButton("❤️ Follow", callback_data=f"social_follow_{target_user_id}")])
        
        keyboard.extend([
            [InlineKeyboardButton("📝 View Threads", callback_data=f"social_threads_{target_user_id}")],
            [InlineKeyboardButton("👥 Social", callback_data="social")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="menu")]
        ])
        
        return {
            'text': card_text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    async def create_find_users_card(self, user_id: int) -> Dict[str, Any]:
        """Create user discovery card"""
        # Get recommended users (excluding self and already followed)
        all_users = self.db.get_all_users(limit=20)
        following = self.db.get_user_following(user_id)
        
        recommended = [
            user for user in all_users 
            if user['telegram_id'] != user_id 
            and user['telegram_id'] not in following
        ][:6]
        
        card_text = "🔍 *Find Players*\n\nConnect with other football enthusiasts!\n\n"
        
        keyboard = []
        for user in recommended:
            keyboard.append([
                InlineKeyboardButton(
                    f"👤 {user['username']} (Lv.{user['level']})", 
                    callback_data=f"social_view_{user['telegram_id']}"
                )
            ])
        
        keyboard.extend([
            [InlineKeyboardButton("🔙 Social", callback_data="social")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
        ])
        
        return {
            'text': card_text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    # ==================== PROFILE CARDS ====================
    async def create_profile_card(self, user_id: int) -> Dict[str, Any]:
        """Create user profile card"""
        user = self.db.get_user(user_id)
        badges = self.db.get_user_badges(user_id)
        
        # Calculate progress to next level
        current_level_xp = (user['level'] - 1) * 100
        next_level_xp = user['level'] * 100
        xp_progress = user['experience'] - current_level_xp
        xp_required = next_level_xp - current_level_xp
        progress_percent = (xp_progress / xp_required) * 100 if xp_required > 0 else 100
        
        # Create progress bar
        progress_bar = self.format_progress_bar(progress_percent)
        
        card_text = (
            f"👤 *Your Profile* 🏅\n\n"
            f"**{user['username']}** • Level {user['level']}\n"
            f"{progress_bar} {progress_percent:.0f}%\n"
            f"⭐ {user['reputation']} Reputation\n\n"
            f"📊 *Statistics:*\n"
            f"📝 {user['threads_created']} threads created\n"
            f"💬 {user['replies_posted']} replies posted\n"
            f"⚽ {user['tournaments_joined']} tournaments joined\n"
            f"❤️ {user['following_count']} following\n"
            f"👤 {user['follower_count']} followers\n\n"
        )
        
        # Add badges section
        if badges:
            card_text += f"🏆 *Badges ({len(badges)}):*\n"
            for badge in badges[:5]:
                card_text += f"• {badge.get('badge_name', 'Achievement')}\n"
            if len(badges) > 5:
                card_text += f"... and {len(badges) - 5} more\n"
        else:
            card_text += "🎯 *No badges yet!* Be active to earn achievements.\n"
        
        keyboard = [
            [
                InlineKeyboardButton("🏆 Badges", callback_data="profile_badges"),
                InlineKeyboardButton("📈 Stats", callback_data="profile_stats")
            ],
            [
                InlineKeyboardButton("✏️ Edit Profile", callback_data="profile_edit"),
                InlineKeyboardButton("🎯 Achievements", callback_data="profile_achievements")
            ],
            [
                InlineKeyboardButton("🔙 Main Menu", callback_data="menu")
            ]
        ]
        
        return {
            'text': card_text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    async def create_badges_card(self, user_id: int) -> Dict[str, Any]:
        """Create badges collection card"""
        badges = self.db.get_user_badges(user_id)
        all_badges = self.db.get_badges()
        
        card_text = "🏆 *Your Badges Collection*\n\n"
        
        if badges:
            card_text += f"🎖️ *Earned ({len(badges)}/{len(all_badges)}):*\n"
            for badge in badges:
                card_text += f"• {badge.get('badge_name')}\n"
        else:
            card_text += "🎯 *No badges earned yet!*\n\n"
            card_text += "Be active in the community to earn achievements!\n"
        
        # Add available badges preview
        card_text += "\n🔮 *Available Badges:*\n"
        for badge in all_badges[:5]:
            card_text += f"• {badge['name']} - {badge['description']}\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Profile", callback_data="profile")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
        ]
        
        return {
            'text': card_text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    # ==================== UTILITY CARDS ====================
    async def create_error_card(self, message: str) -> Dict[str, Any]:
        """Create error card"""
        return {
            'text': f"❌ *Oops!*\n\n{message}",
            'reply_markup': InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
            ]),
            'parse_mode': 'Markdown'
        }

    async def create_success_card(self, title: str, message: str, return_to: str = "menu") -> Dict[str, Any]:
        """Create success card"""
        return {
            'text': f"✅ *{title}*\n\n{message}",
            'reply_markup': InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=return_to)],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
            ]),
            'parse_mode': 'Markdown'
        }

    async def create_help_card(self) -> Dict[str, Any]:
        """Create help card"""
        help_text = (
            "🆘 *SoccerForum Bot Help*\n\n"
            "🎯 *Quick Actions:*\n"
            "• Use buttons to navigate\n"
            "• Join tournaments easily\n"
            "• Create discussions in forums\n\n"
            "📱 *Main Features:*\n"
            "⚽ *Tournaments* - Competitive events\n"
            "💬 *Forums* - Game discussions\n"
            "👥 *Social* - Connect with players\n"
            "👤 *Profile* - Your stats & achievements\n\n"
            "Need help? Use /menu to return to main menu!"
        )
        
        return {
            'text': help_text,
            'reply_markup': InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")],
                [InlineKeyboardButton("📚 Full Guide", callback_data="guide")]
            ]),
            'parse_mode': 'Markdown'
        }


# ==================== CONVERSATION HANDLERS ====================
class ConversationHandlers:
    def __init__(self, db, cards):
        self.db = db
        self.cards = cards

    async def start_tournament_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start tournament creation"""
        query = update.callback_query
        context.user_data.clear()
        
        await query.edit_message_text(
            "⚽ Tournament Creation Wizard\n\n"
            "Step 1/4: What should we name your tournament?\n\n"
            "💡 Example: 'FIFA 14 Champions League'\n\n"
            "Type your answer below:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]])
        )
        return Config.TOURNAMENT_NAME

    async def tournament_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament name"""
        context.user_data['tournament_name'] = update.message.text
        
        await update.message.reply_text(
            "Step 2/4: Which game version?\n\n"
            "💡 Examples: FIFA 14, eFootball 2025, FIFA 16\n\n"
            "Type your answer below:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]])
        )
        return Config.TOURNAMENT_GAME

    async def tournament_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament game version"""
        context.user_data['tournament_game'] = update.message.text
        
        await update.message.reply_text(
            "Step 3/4: Maximum number of teams?\n\n"
            "💡 Enter a number (e.g., 16, 32)\n\n"
            "Type your answer below:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]])
        )
        return Config.TOURNAMENT_TEAMS

    async def tournament_teams(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament teams"""
        try:
            max_teams = int(update.message.text)
            if max_teams < Config.MIN_TOURNAMENT_TEAMS:
                await update.message.reply_text(f"❌ Minimum {Config.MIN_TOURNAMENT_TEAMS} teams required. Try again:")
                return Config.TOURNAMENT_TEAMS
            if max_teams > Config.MAX_TOURNAMENT_TEAMS:
                await update.message.reply_text(f"❌ Maximum {Config.MAX_TOURNAMENT_TEAMS} teams allowed. Try again:")
                return Config.TOURNAMENT_TEAMS
                
            context.user_data['tournament_teams'] = max_teams
            await update.message.reply_text(
                "Step 4/4: Tournament description\n\n"
                "💡 Describe your tournament rules, format, etc.\n\n"
                "Type your answer below:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]])
            )
            return Config.TOURNAMENT_DESC
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number. Try again:")
            return Config.TOURNAMENT_TEAMS

    async def tournament_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament description and create"""
        user_id = update.message.from_user.id
        
        try:
            tournament_data = {
                "name": context.user_data['tournament_name'],
                "game_version": context.user_data['tournament_game'],
                "max_teams": context.user_data['tournament_teams'],
                "description": update.message.text,
                "creator_id": user_id
            }
            
            tournament_id = self.db.create_tournament(tournament_data)
            
            if tournament_id:
                # Award experience
                self.db.update_user_stats(user_id, {'experience': Config.EXPERIENCE_PER_ACTION['thread_created']})
                
                keyboard = [
                    [InlineKeyboardButton("👀 View Tournament", callback_data=f"tournament_view_{tournament_id}")],
                    [InlineKeyboardButton("⚽ Tournaments", callback_data="tournaments")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
                ]
                
                await update.message.reply_text(
                    f"✅ Tournament created successfully!\n\n"
                    f"🏆 *{tournament_data['name']}*\n"
                    f"🎮 {tournament_data['game_version']}\n"
                    f"👥 {tournament_data['max_teams']} teams max\n\n"
                    f"Share the tournament with others to join!",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Error creating tournament. Please try again.")
                
        except Exception as e:
            logging.error(f"Error creating tournament: {e}")
            await update.message.reply_text("❌ Error creating tournament. Please try again.")
        
        context.user_data.clear()
        return ConversationHandler.END

    async def start_thread_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start thread creation"""
        query = update.callback_query
        forum_id = int(query.data.split('_')[-1])
        
        context.user_data['forum_id'] = forum_id
        forum = self.db.get_forum(forum_id)
        context.user_data['forum_name'] = forum['name']
        
        await query.edit_message_text(
            f"📝 Creating New Thread in *{forum['name']}*\n\n"
            "Step 1/2: Enter the thread title:\n\n"
            "Type your answer below:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]),
            parse_mode='Markdown'
        )
        return Config.THREAD_TITLE

    async def thread_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle thread title"""
        context.user_data['thread_title'] = update.message.text
        
        await update.message.reply_text(
            "Step 2/2: Enter the thread content:\n\n"
            "Type your answer below:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]])
        )
        return Config.THREAD_CONTENT

    async def thread_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle thread content and create"""
        user_id = update.message.from_user.id
        forum_id = context.user_data.get('forum_id')
        
        if not forum_id:
            await update.message.reply_text("❌ Error: Forum not specified.")
            context.user_data.clear()
            return ConversationHandler.END
        
        thread_data = {
            "title": context.user_data['thread_title'],
            "content": update.message.text,
            "forum_id": forum_id,
            "creator_id": user_id
        }
        
        thread_id = self.db.create_thread(thread_data)
        forum = self.db.get_forum(forum_id)
        
        if thread_id:
            # Award experience
            self.db.update_user_stats(user_id, {'experience': Config.EXPERIENCE_PER_ACTION['thread_created']})
            
            keyboard = [
                [InlineKeyboardButton("👀 View Thread", callback_data=f"thread_view_{thread_id}")],
                [InlineKeyboardButton("💬 Forum", callback_data=f"forum_view_{forum_id}")],
                [InlineKeyboardButton("💬 Forums", callback_data="forums")]
            ]
            
            await update.message.reply_text(
                f"✅ Thread created in *{forum['name']}*!\n\n"
                f"*{context.user_data['thread_title']}*",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Error creating thread. Please try again.")
            
        context.user_data.clear()
        return ConversationHandler.END

    async def start_reply_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start reply creation"""
        query = update.callback_query
        thread_id = int(query.data.split('_')[-1])
        
        context.user_data['thread_id'] = thread_id
        thread = self.db.get_thread(thread_id)
        context.user_data['thread_title'] = thread['title']
        
        await query.edit_message_text(
            f"💬 Writing Reply to: *{thread['title']}*\n\n"
            "Enter your reply:\n\n"
            "Type your answer below:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]),
            parse_mode='Markdown'
        )
        return Config.REPLY_CONTENT

    async def reply_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle reply content and create"""
        user_id = update.message.from_user.id
        thread_id = context.user_data.get('thread_id')
        
        if not thread_id:
            await update.message.reply_text("❌ Error: Thread not specified.")
            context.user_data.clear()
            return ConversationHandler.END
        
        reply_data = {
            "content": update.message.text,
            "thread_id": thread_id,
            "user_id": user_id
        }
        
        reply_id = self.db.create_reply(reply_data)
        thread = self.db.get_thread(thread_id)
        
        if reply_id:
            # Award experience
            self.db.update_user_stats(user_id, {'experience': Config.EXPERIENCE_PER_ACTION['reply_posted']})
            
            keyboard = [
                [InlineKeyboardButton("👀 View Thread", callback_data=f"thread_view_{thread_id}")],
                [InlineKeyboardButton("💬 Forum", callback_data=f"forum_view_{thread['forum_id']}")]
            ]
            
            await update.message.reply_text(
                "✅ Reply posted successfully!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text("❌ Error posting reply. Please try again.")
            
        context.user_data.clear()
        return ConversationHandler.END

    async def cancel_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel any conversation"""
        context.user_data.clear()
        if update.message:
            await update.message.reply_text(
                "❌ Operation cancelled.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
                ])
            )
        else:
            await update.callback_query.edit_message_text(
                "❌ Operation cancelled.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
                ])
            )
        return ConversationHandler.END


# ==================== MAIN BOT CLASS ====================
class SuperSoccerBot:
    def __init__(self):
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        self.db = SuperDatabase()
        self.cards = CardSystem(self.db)
        self.conversations = ConversationHandlers(self.db, self.cards)
        
        self.setup_handlers()

    def setup_handlers(self):
        """Setup all bot handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("menu", self.show_main_menu))
        self.application.add_handler(CommandHandler("help", self.show_help))
        
        # Conversation handlers
        tournament_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.conversations.start_tournament_creation, pattern="^tournament_create$")],
            states={
                Config.TOURNAMENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conversations.tournament_name)],
                Config.TOURNAMENT_GAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conversations.tournament_game)],
                Config.TOURNAMENT_TEAMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conversations.tournament_teams)],
                Config.TOURNAMENT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conversations.tournament_description)],
            },
            fallbacks=[CommandHandler("cancel", self.conversations.cancel_conversation)]
        )
        
        thread_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.conversations.start_thread_creation, pattern="^thread_create_")],
            states={
                Config.THREAD_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conversations.thread_title)],
                Config.THREAD_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conversations.thread_content)],
            },
            fallbacks=[CommandHandler("cancel", self.conversations.cancel_conversation)]
        )
        
        reply_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.conversations.start_reply_creation, pattern="^reply_create_")],
            states={
                Config.REPLY_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conversations.reply_content)],
            },
            fallbacks=[CommandHandler("cancel", self.conversations.cancel_conversation)]
        )
        
        self.application.add_handler(tournament_conv)
        self.application.add_handler(thread_conv)
        self.application.add_handler(reply_conv)
        
        # Callback query handler - MUST BE LAST
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Initialize user in database
        user_data = self.db.get_user(user_id)
        if not user_data.get('username') or user_data.get('username') == f'user_{user_id}':
            user_data['username'] = user.username or f"user_{user_id}"
            user_data['full_name'] = user.full_name
            self.db.save_user(user_id, user_data)
        
        # Send welcome card
        welcome_text = (
            f"👋 Welcome to *SoccerForum*, {user.first_name}! 🎉\n\n"
            "⚽ *Your ultimate football community!*\n\n"
            "🎮 Discuss games • 🏆 Join tournaments • 👥 Make friends\n\n"
            "Ready to get started?"
        )
        
        keyboard = [
            [InlineKeyboardButton("🚀 Get Started", callback_data="menu")],
            [InlineKeyboardButton("📚 Quick Guide", callback_data="help")]
        ]
        
        if update.message:
            await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        else:
            await update.callback_query.edit_message_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu"""
        user_id = update.effective_user.id
        card = await self.cards.create_main_menu(user_id)
        
        if update.message:
            await update.message.reply_text(**card)
        else:
            await update.callback_query.edit_message_text(**card)

    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help"""
        card = await self.cards.create_help_card()
        
        if update.message:
            await update.message.reply_text(**card)
        else:
            await update.callback_query.edit_message_text(**card)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        # If there's active conversation data, suggest using /cancel
        if context.user_data and len(context.user_data) > 0:
            await update.message.reply_text(
                "It looks like you're in the middle of an operation. "
                "Use /cancel to cancel the current operation, or use the menu buttons to navigate."
            )
            return
        
        # Otherwise show help
        card = await self.cards.create_help_card()
        await update.message.reply_text(**card)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        logging.info(f"Callback received: {data} from user {user_id}")
        
        try:
            # Handle cancel first
            if data == "cancel":
                await self.conversations.cancel_conversation(update, context)
                return
            
            # Main navigation
            if data == "menu":
                card = await self.cards.create_main_menu(user_id)
            elif data == "help":
                card = await self.cards.create_help_card()
            
            # Tournament handlers
            elif data == "tournaments":
                card = await self.cards.create_tournaments_menu(user_id)
            elif data.startswith("tournament_view_"):
                tournament_id = int(data.split("_")[-1])
                card = await self.cards.create_tournament_card(user_id, tournament_id)
            elif data.startswith("tournament_join_"):
                tournament_id = int(data.split("_")[-1])
                if self.db.join_tournament(user_id, tournament_id):
                    # Award experience
                    self.db.update_user_stats(user_id, {'experience': Config.EXPERIENCE_PER_ACTION['tournament_joined']})
                    card = await self.cards.create_success_card(
                        "Tournament Joined!", 
                        "You've successfully joined the tournament!",
                        f"tournament_view_{tournament_id}"
                    )
                else:
                    card = await self.cards.create_error_card("Could not join tournament.")
            
            # Forum handlers
            elif data == "forums":
                card = await self.cards.create_forums_menu(user_id)
            elif data.startswith("forum_view_"):
                forum_id = int(data.split("_")[-1])
                card = await self.cards.create_forum_card(user_id, forum_id)
            elif data.startswith("forum_follow_"):
                forum_id = int(data.split("_")[-1])
                if self.db.follow_forum(user_id, forum_id):
                    card = await self.cards.create_success_card(
                        "Forum Followed!", 
                        "You'll now receive updates from this forum.",
                        f"forum_view_{forum_id}"
                    )
                else:
                    card = await self.cards.create_error_card("Already following this forum.")
            elif data.startswith("thread_view_"):
                thread_id = int(data.split("_")[-1])
                card = await self.cards.create_thread_card(user_id, thread_id)
            
            # Social handlers
            elif data == "social":
                card = await self.cards.create_social_menu(user_id)
            elif data == "social_find":
                card = await self.cards.create_find_users_card(user_id)
            elif data.startswith("social_view_"):
                target_user_id = int(data.split("_")[-1])
                card = await self.cards.create_user_profile_card(user_id, target_user_id)
            elif data.startswith("social_follow_"):
                target_user_id = int(data.split("_")[-1])
                if self.db.follow_user(user_id, target_user_id):
                    card = await self.cards.create_success_card(
                        "User Followed!", 
                        "You're now following this user.",
                        f"social_view_{target_user_id}"
                    )
                else:
                    card = await self.cards.create_error_card("Could not follow user.")
            
            # Profile handlers
            elif data == "profile":
                card = await self.cards.create_profile_card(user_id)
            elif data == "profile_badges":
                card = await self.cards.create_badges_card(user_id)
            
            # Leaderboard
            elif data == "leaderboard" or data == "social_leaderboard":
                rankings = self.db.get_user_rankings(limit=10)
                leaderboard_text = "👑 *Community Leaderboard*\n\n"
                
                for i, user in enumerate(rankings, 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    leaderboard_text += f"{medal} *{user['username']}* - Lv.{user['level']} • ⭐{user['reputation']}\n"
                
                keyboard = [
                    [InlineKeyboardButton("👥 Social", callback_data="social")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
                ]
                
                card = {
                    'text': leaderboard_text,
                    'reply_markup': InlineKeyboardMarkup(keyboard),
                    'parse_mode': 'Markdown'
                }
            
            else:
                card = await self.cards.create_error_card("Unknown command. Please try again.")
            
            await query.edit_message_text(**card)
                
        except Exception as e:
            logging.error(f"Error handling callback {data}: {e}")
            card = await self.cards.create_error_card("An error occurred. Please try again.")
            await query.edit_message_text(**card)

    def run(self):
        """Start the bot"""
        print("🎮 SOCCERFORUM SUPER BOT")
        print("⚽ Tournaments • 💬 Forums • 👥 Social • 👤 Profiles")
        print("🚀 Starting...")
        print(f"📊 Database: {Config.DATABASE_PATH}")
        print("🤖 Bot is now running! Press Ctrl+C to stop.")
        
        self.application.run_polling()


# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run bot
    bot = SuperSoccerBot()
    bot.run()