# Based on https://github.com/alejandro-ao/langchain-chat-gui
# pip install streamlit streamlit-chat langchain openai
import streamlit as st
from streamlit_chat import message
import os
import openai
from datetime import datetime as dt
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from ChatDatabase import *

stss = st.session_state
stss.newChatSwitch = False  # TODO:Take this out
stss.userID = "sidjnsn66"  # TODO Temporary
chatModified = False
chatDict = {}
DEBUG = False


# TODO New chat button event handler.  Call newchat
def NewChat():
    st.write("NewChat fn is running")
    stss.newChatSwitch = True
    if len(stss.messages) > 1:
        st.session_state.messages = [
            SystemMessage(content="You are a helpful assistant.")
        ]  # clear old chat messages if any


def NewUserSim():
    if DEBUG:
        st.write("NewUserSim fn is running")
    delete_user_state(stss.userID)
    delete_all_chats()
    if DEBUG:
        st.write("Values currently in session_state:")
    for k in st.session_state:
        del st.session_state[k]
    if DEBUG:
        st.write("After deleting state, this is what state looks like: ")
    for k in st.session_state:
        st.write("     " + str(k) + "  = " + str(st.session_state[k]))


def NewSessionSim():
    if DEBUG:
        st.write("NewSession fn is running")
    del st.session_state["messages"]


def Init():
    if DEBUG:
        st.write("Init fn is running")
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.messages = [SystemMessage(content="You are a helpful assistant.")]
    # stss.chatDict = {}


def tempSliderChange():
    update_session_state_by_user(stss.userID, "Temperature", stss.tempSlider)


def buildChatDict(messages):
    for i, msg in enumerate(messages[1:]):
        if i % 2 == 0:
            # print( i + " - " + msg)
            chatDict.update({str(i) + "_user": msg.content})
        else:
            chatDict.update({str(i) + "_ai": msg.content})
    return chatDict


# NewUserSim()  # TODO:  Take out

# Test for first time user and init if so
if getUserState(stss.userID) == None:  # no state record exists, so this is a new user.
    if DEBUG:
        st.write("First-time user detected and is being set up.")
    Init()
    stss["tempSlider"] = 0.0  # initial value of temp slider
    stss.newChatSwitch = True  # TODO: is this right?
    save_newUserState(stss.userID, stss.tempSlider)
else:  # Test for new session
    if "messages" not in st.session_state:  # new session/startup
        if DEBUG:
            st.write("Not new user, but new session detected.  Calling Init().")
        # TODO: Retrieve state and messages
        getResult = getUserState(stss.userID)  # pull in state
        stss.tempSlider = getResult["Temperature"]
        stss.userID = getResult["UserID"]
        docsList = get_all_titles(stss.userID)
        titlesList = []
        for doc in docsList:
            titlesList.append(doc["ChatTitle"])
        Init()


# TODO
# test that the API key exists
# if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
#     print("OPENAI_API_KEY is not set")
#     exit(1)
# else:
#     print("OPENAI_API_KEY is set")

# setup streamlit page
# st.set_page_config(page_title="Your own ChatGPT", page_icon="🤖")

# st.header("Your own ChatGPT 🤖")

with st.sidebar:
    st.title("Sid's ChatGPT Clone")

    btnNewChatReturn = st.button("New Chat", on_click=NewChat)
    btnNewUserReturn = st.button("New User", on_click=NewUserSim)
    btnNewUserSession = st.button("New Session", on_click=NewSessionSim)

    # titlesList = ["Title1", "Title2", "Title3", "Title4", "Title5"]
    for title in titlesList:
        title

    # TODO Put message hx here, individually selectable, and in historical order

    # borrowed from https://github.com/dataprofessor/llama2
    temp = 0.0
    temp = st.sidebar.slider(
        "Temperature",
        min_value=0.01,
        max_value=5.0,
        step=0.01,
        on_change=tempSliderChange,
        key="tempSlider",
    )

    # top_p = st.sidebar.slider(
    #     "top_p", min_value=0.01, max_value=1.0, value=0.9, step=0.01
    # )
    # max_length = st.sidebar.slider(
    #     "max_length", min_value=64, max_value=4096, value=512, step=8
    # )

chat = ChatOpenAI(temperature=stss.tempSlider)

# User-provided prompt
if prompt := st.chat_input("Enter your message: "):  # string
    st.session_state.messages.append(HumanMessage(content=prompt))
    # with st.chat_message("user"):
    #     st.write(prompt)
    with st.spinner("Thinking..."):
        response = chat(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))
        CurrContent = response.content
        chatModified = True


# display message history
if DEBUG:
    st.write("About to write messages out to screen.")
messages = st.session_state.get("messages", [])  # this is a list

for i, msg in enumerate(messages[1:]):
    if i % 2 == 0:
        message(msg.content, is_user=True, key=str(i) + "_user")
    else:
        message(msg.content, is_user=False, key=str(i) + "_ai")


if DEBUG:
    st.write(
        "newChatSwitch = "
        + str(stss.newChatSwitch)
        + ". -----len(Messages) = "
        + str(len(messages))
    )

# Create a new chat with new title.  Occurs after first chat turn so that title can be created.
if (
    stss.newChatSwitch == True and len(messages) > 1
):  # it's a new chat and one chat turn has occurred
    if DEBUG:
        st.write("newChatSwitchcode is running")
    chatID = str(dt.now())
    chatTitle = chat(
        messages[1:]
        + [
            HumanMessage(
                content="What is a good title for this chat that is 20 characters or less?"
            )
        ]
    )
    stss.chatTitle = chatTitle.content
    stss.chatID = chatID

    chatDict = buildChatDict(messages)

    newChatSaveResult = save_new_chat(
        stss.userID, stss.chatID, stss.chatTitle, chatDict
    )
    stss.newChatSwitch = False
    chatModified = False

if DEBUG:
    st.write("At end of run, state looks like this:")
    for k in st.session_state:
        st.write("------  " + str(k) + "  = " + str(st.session_state[k]))

if chatModified:
    chatDict = buildChatDict(messages)

    # save to db
    upsertResult = upsertChatContent(stss.chatID, chatDict)
    if DEBUG:
        st.write("The id of the record upserted is: " + str(upsertResult.upserted_id))
        st.write("Number of records modified = " + str(upsertResult.modified_count))
    chatModified = False

# Checklist
#    make new session work correctly
#        retrieve state vars, Chat Titles, and latest chat messages
#        what is 1_ai and 0_user in state?
#    create chat title list on sidebar

# TODO's:
# all sessions are loaded from db on startup?????

# TODO's FEATURES:
# Public Facing
# Multiple users with logins and separate work spaces
# Google Search
# Vector DB
# PDF Handling
# Text handling
# ReAct Agent
# Use sidebar controls to set model params
# Llama 2
# Llama Index
# Other Models - Hugging Face interface?
# Support other users with their API Keys?
# Prompt Selection
# Bot Personality Selection
# Plugins


# Example:
# messages =
# [SystemMessage(content='You are a helpful assistant.', additional_kwargs={}),
# HumanMessage(content='What was the cause of the death of James Dean?', additional_kwargs={}, example=False),
# AIMessage(content='James Dean died in a car accident on September 30, 1955. The cause of the accident was attributed to speeding. He was driving his Porsche 550 Spyder when he collided with another car at an intersection near Cholame, California.', additional_kwargs={}, example=False)]
