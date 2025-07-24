from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram import Client, filters, enums 

class BUTTONS(object):
    MBUTTON = [[InlineKeyboardButton("• ᴄʜᴧᴛ-ɢᴘᴛ •", callback_data="mplus HELP_ChatGPT"),InlineKeyboardButton("• ǫᴜᴏᴛʟʏ •", callback_data="mplus HELP_Q"),InlineKeyboardButton("• sᴛɪᴄᴋᴇʀs •", callback_data="mplus HELP_Sticker")],
    [InlineKeyboardButton("• ᴛᴧɢ-ᴧʟʟ •", callback_data="mplus HELP_TagAll"),
    InlineKeyboardButton("• ɢɪᴛ-ʜᴜʙ •", callback_data="mplus HELP_Github"),InlineKeyboardButton("• ᴇxᴛʀᴧ •", callback_data="mplus HELP_Extra")],
    [InlineKeyboardButton("• ᴧᴄᴛɪᴏɴ •", callback_data="mplus HELP_Action"),InlineKeyboardButton("• sᴇᴧʀᴄʜ •", callback_data="mplus HELP_Search")],    
    [InlineKeyboardButton("• ғᴏɴᴛ •", callback_data="mplus HELP_Font"),
    InlineKeyboardButton("• ᴄᴏᴜᴘʟᴇs •", callback_data="mplus HELP_Couples"),InlineKeyboardButton("• ᴛ-ɢʀᴧᴘʜ •", callback_data="mplus HELP_TG")],          
    [InlineKeyboardButton("<", callback_data=f"settings_back_helper"), 
    InlineKeyboardButton(">", callback_data=f"managebot123 settings_back_helper"),
    ]]
