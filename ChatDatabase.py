import pymongo

# streamliimport datetime
import streamlit as st
from bson.objectid import ObjectId  # bson is installed with pymongo
from datetime import datetime as dt

# Replace the placeholder data with your Atlas connection string. Be sure it includes
# a valid username and password! Note that in a production environment,
# you should not store your password in plain-text here.

MONGO_KEY = st.secrets["MongoString"]
client = pymongo.MongoClient(MONGO_KEY)

# use a database named "ChatDB"
db = client.ChatDB


# Send a ping to confirm a successful connection
def pingDB():
    try:
        client.admin.command("ping")
        retval = "Pinged your deployment. You successfully connected to MongoDB!"
    except Exception as e:
        retval = "Failed:  Error is: " + e
    return retval


############################### Persist state


def save_newUserState(userID, temperature):
    return db.ChatState.insert_one({"UserID": userID, "Temperature": temperature})


def getUserState(userID):
    return db.ChatState.find_one({"UserID": userID})


# delete state record (not deleting the Collection)
def delete_user_state(userID):
    db.ChatState.delete_many({"UserID": userID})


def update_session_state_by_user(userID, fieldName, newVal):  ##TODO finish this
    query = {"UserID": userID}
    new_value = {"$set": {fieldName: newVal}}
    return db.ChatState.update_one(query, new_value)


############################## Persist chat content and title


def upsertChatContent(chat_id, chatDict):
    query = {"ChatID": chat_id}
    return db.chats.update_one(query, {"$set": {"Content": chatDict}}, upsert=True)


def save_new_chat(userID, chatID, chatTitle, chatContent):
    return db.chats.insert_one(
        {
            "UserID": userID,
            "ChatID": chatID,
            "ChatTitle": chatTitle,
            "Content": chatContent,
        }
    )


# TODO Retrieve latest chat for user
def get_latest_ChatRecord(userID):
    return db.chats.find_one({"UserID": userID}, sort=[("_id", 1)])


# Get all Chat Titles and datetime keys for sorting
def get_all_titles(userID):
    return list(
        db.chats.find({"UserID": userID}, {"_id": 0, "ChatID": 1, "ChatTitle": 1})
    )


# EX:
# result = get_all_chat_data()
# for i in result:
#     print(i)


# Get all Chat data
def get_all_chat_data():
    return db.chats.find({}, {"ChatID": 1, "ChatTitle": 1, "Content": 1})


# EX: update chat title by key
# result = update_chat_title_by_key("64d990cda68dad84b2b65f90", "My updated title")
# print(result)


# Update the title of a chat by chat key
def update_chat_title_by_key(chat_key, new_title):
    query = {"_id": ObjectId("chat_key")}
    new_value = {"$set": {"ChatTitle": "new_title"}}
    return db.chats.update_one(query, new_value)


# EX: update chat title by ChatID
#   result = update_chat_title_by_chatID("08152023 0923", "My updated title")
#   print(result)


# Update the title of a chat by chatID                      #TODO: Change to Update Many
def update_chat_title_by_chatID(chat_id, new_title):
    query = {"ChatID": "chat_id"}
    new_value = {"$set": {"ChatTitle": "new_title"}}
    return db.chats.update_one(query, new_value)


# EX:  delete a chat
#   chat_key = "64d990cda68dad84b2b65f90"
#   delete_chat_by_key(ChatKey)


def delete_chat_by_key(chat_key):
    query = {"_id": ObjectId("chat_key")}
    db.chats.delete_one(query)


# delete all chats (not deleting the Collection)
def delete_all_chats():
    db.chats.delete_many({})
