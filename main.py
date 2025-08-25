import os
import asyncio
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from dotenv import load_dotenv
from slack_sdk import WebClient
from openai import OpenAI
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
from typing import Dict
from pydantic import BaseModel
from src.trapnz.models import Volunteer


async def handle_message(client: SocketModeClient, req: SocketModeRequest, target_channel_id: str):
    """Handle incoming messages in real-time"""

    # Acknowledge the request
    await client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))

    if req.type == "events_api":
        event = req.payload.get("event", {})
        event_type = event.get("type")
        print(f"Event Type: {event_type}")

        webClient = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        openai = OpenAI()

       
        
        if event_type == "message":
            # Extract message details
            channel = event.get("channel", "Unknown")
            user = event.get("user", "Unknown")
            text = event.get("text", "")
            ts = event.get("ts", "")
            bot_user = webClient.auth_test()['user_id']

            print(f"bot user: {bot_user}: User: {user}")
            
            # Only process messages from the target channel and
            # don't respond to your own messages
            if channel == target_channel_id:
                from datetime import datetime
                timestamp = datetime.fromtimestamp(float(ts)).strftime('%H:%M:%S')
                
                # Print the message
                print(f"📨 Message received: [{timestamp}] {text}")
                for_bot_user=f"@{bot_user}" in text
                print(f"For bot user? {for_bot_user}")
                print("-" * 40)


                if for_bot_user:
                    print("Contacting AI")
                    INSTRUCTIONS =  """
                    you are an AI agent that is helping coordinate volunteers to check pest control traps. 
                    You're new to the job and still learning. if the user is asking for something to do, 
                    respond asking if they are availble to check traps today or tomorrow if its late in the day. The volunteers are located in Crhistchurch, New Zealand. 
                    If they are, tell them you'll go check and let them know otherwise just say thanks for checking in. 
                    If they are not asking for something to do, say hello in a language of your choosing. 
                    When you meet a volunteer, call the load_volunteer tool, passing in their handle. if nothing is returned, tell them you haven't met them, introduce yourself and ask for their name.
                    once we have their name, call the store_volunteer tool, preferences is a json document where you store their user name as 'slack_handle'
                    """
                    user_messages = f"from volunteer with handle {user}: {text}"

                    trapmanager_agent = Agent(
                        name="Trap Manager Agent agent",
                        instructions=INSTRUCTIONS,
                        tools=[store_volunteer, load_volunteer],
                        model="gpt-4o-mini",
                        )

                    with trace("Conversation"):
                        ai_response = await Runner.run(trapmanager_agent, user_messages)

                    print(f"\n\n\n\n\nAI Response: {ai_response}")

                    response = webClient.chat_postMessage(channel=target_channel_id, text=f"{ai_response.final_output}")
        


async def get_channel_id(web_client: AsyncWebClient, channel_name: str) -> str:
    """Get the channel ID from channel name"""
    try:
        # Try to get channel info
        response = await web_client.conversations_list(types="public_channel,private_channel")
        if response["ok"]:
            for channel in response["channels"]:
                if channel["name"] == channel_name.replace("#", ""):
                    return channel["id"]
        
        print(f"⚠️  Channel '{channel_name}' not found in accessible channels")
        print("   Available channels:")
        if response["ok"]:
            for channel in response["channels"]:
                print(f"   - #{channel['name']} (ID: {channel['id']})")
        return None
    except Exception as e:
        print(f"❌ Error getting channel info: {e}")
        return None

async def start_socket_mode():
    """Start real-time message listening using Socket Mode"""
    # Load environment variables
    load_dotenv(override=True)
    
    # Get tokens
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN not found in environment variables")
        print("Please add SLACK_BOT_TOKEN=your_token_here to your .env file")
        return
    
    if not app_token:
        print("❌ SLACK_APP_TOKEN not found in environment variables")
        print("Please add SLACK_APP_TOKEN=your_token_here to your .env file")
        print("\nTo get SLACK_APP_TOKEN:")
        print("1. Go to api.slack.com/apps")
        print("2. Select your app")
        print("3. Go to 'Socket Mode' → Enable it")
        print("4. Copy the 'App-Level Token' (starts with xapp-)")
        return
    
    print("🔄 Starting real-time message monitoring...")
    print("   Channel: #all-halswell-quarry-trappers")
    print("   Messages will appear below as they arrive...")
    print("   Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Create async web client
        web_client = AsyncWebClient(token=bot_token)
        
        # Get the target channel ID
        target_channel = "all-halswell-quarry-trappers"
        channel_id = await get_channel_id(web_client, target_channel)
        
        if not channel_id:
            print(f"❌ Cannot find channel '{target_channel}'")
            print("   Please check the channel name and bot permissions")
            return
        
        print(f"✅ Target channel: #{target_channel} (ID: {channel_id})")
        
        # Create socket mode client
        client = SocketModeClient(
            app_token=app_token,
            web_client=web_client
        )
        
        # Add message handler with channel ID
        client.socket_mode_request_listeners.append(
            lambda client, req: handle_message(client, req, channel_id)
        )
        
        print("✅ Message handler registered")
        print("   Waiting for connection...")
        
        # Connect and start listening
        await client.connect()
        print("✅ Socket Mode connection established")
        print("   Listening for messages...")
        
        # Test the connection by sending a ping
        try:
            await web_client.auth_test()
            print("✅ Bot authentication verified")
        except Exception as e:
            print(f"⚠️  Bot auth test failed: {e}")
        
        # Keep the connection alive and handle events
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            await client.close()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping message listener...")
        await client.close()
    except Exception as e:
        print(f"❌ Error: {e}")

@function_tool
def store_volunteer(volunteer: Volunteer):
    print(f"Storing Volunteer {volunteer}")

@function_tool
def load_volunteer(handle: str) -> Volunteer:
    print(f"Loading Volunteer")
    volunteer = Volunteer(name="Simon", preferences="{'slack_handle': 'U099QRWEPN2'}")
    return volunteer

def main():
    """Main function"""
    print("🪤 Trap Manager - Real-Time Channel Monitor")
    print("=" * 50)
    print("Using Slack Socket Mode for instant message delivery")
    print("=" * 50)
    
    try:
        # Run the async socket mode client
        asyncio.run(start_socket_mode())
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
