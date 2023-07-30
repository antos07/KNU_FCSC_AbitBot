from telegram import ChatMemberUpdated, ChatMember


def did_new_user_join(chat_member_update: ChatMemberUpdated) -> bool:
    """Checks if chat memeber status update means that new user has joined"""
    # Code taken from PTB's example:
    # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/chatmemberbot.py
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get(
        "is_member", (None, None))

    if status_change is None:
        return False

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return not was_member and is_member
