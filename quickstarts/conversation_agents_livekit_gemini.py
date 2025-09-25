# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# to run it, pip install livekit google.genai livekit-agents livekit-api python-dotenv google-genai livekit-plugins-google , add gemini api in .env and
# then run "python conversation_agents_livekit_gemini.py console" in terminal

import asyncio  
import logging  
from dataclasses import dataclass  
from typing import Optional  
from dotenv import load_dotenv  
  
from livekit.agents import JobContext, WorkerOptions, cli  
from livekit.agents.voice import Agent, AgentSession  
from livekit.plugins.google.beta.realtime import RealtimeModel  
from google.genai import types  
  
load_dotenv()  
logger = logging.getLogger("dual-agent-conversation")  
topic = input("Enter the topic for the conversation: ")
@dataclass  
class ConversationState:  
    topic: str = topic  
    conversation_mode: str = "debate"  # "friendly" or "debate"  
    turn_count: int = 0  
    max_turns: int = 12  
    conversation_active: bool = True  
    current_speaker: str = "agent1"  
    last_error: Optional[str] = None  
    session_healthy: bool = True  
  
class DualPersonaAgent(Agent):  
    def __init__(self, topic: str, mode: str):  
        if mode == "friendly":  
            instructions = f"""You are participating in a friendly discussion about {topic}.  
            You will receive specific instructions about which supportive perspective to take.  
            Always respond in one line only to save API costs.  
            Be collaborative and encouraging. """  
        else:  
            instructions = f"""You are participating in a debate about {topic}.  
            You will receive specific instructions about which perspective to take.  
            Always respond in one line only to save API costs.  
            Be direct and contrary.  """  
          
        super().__init__(instructions=instructions)  
        self.topic = topic  
        self.mode = mode
  
async def get_conversation_mode() -> str:  
    """Get conversation mode from user input"""  
    print("\nSelect conversation mode:")  
    print("1. Friendly discussion")  
    print("2. Debate format")  
      
    while True:  
        try:  
            choice = input("Enter your choice (1 or 2): ").strip()  
            if choice == "1":  
                return "friendly"  
            elif choice == "2":  
                return "debate"  
            else:  
                print("Please enter 1 or 2")  
        except (EOFError, KeyboardInterrupt):  
            return "debate"  # Default fallback  
  
async def entrypoint(ctx: JobContext):  
    await ctx.connect()  
      
    # Get user's preferred conversation mode  
    mode = await get_conversation_mode()  
      
    state = ConversationState(conversation_mode=mode)  
      
    # Single agent with dual personas  
    agent = DualPersonaAgent(state.topic, mode)  
      
    # Session with comprehensive error handling  
    session = AgentSession[ConversationState](  
        userdata=state,  
        llm=RealtimeModel(  
            # model="gemini-2.0-flash-live-001",
            model= "gemini-2.5-flash-preview-native-audio-dialog",  
            instructions=agent.instructions,  
            voice="Puck",  
            realtime_input_config=types.RealtimeInputConfig(  
                automatic_activity_detection=types.AutomaticActivityDetection(  
                    disabled=False  
                )  
            )  
        ),  
        allow_interruptions=True,  
        turn_detection="realtime_llm",  
        min_interruption_duration=0.3,  
    )  
      
    # Error handling for session events  
    def on_session_error(error):  
        logger.error(f"Session error: {error}")  
        state.session_healthy = False  
        state.conversation_active = False  
      
    session.on("error", on_session_error)  
      
    try:  
        await session.start(agent=agent, room=ctx.room)  
        logger.info(f"Session started successfully in {mode} mode")  
          
        # Checkpoint: Verify session is running  
        if not session._started:  
            raise RuntimeError("Session failed to start properly")  
          
        await run_conversation(session, state)  
          
    except Exception as e:  
        logger.error(f"Critical error in entrypoint: {e}")  
        state.conversation_active = False  
    finally:  
        await cleanup_session(session, state)  
  
async def run_conversation(session: AgentSession, state: ConversationState):  
    """Main conversation loop supporting both friendly and debate modes"""  
      
    try:  
        if state.conversation_mode == "friendly":  
            logger.info("Starting friendly conversation...")  
            await run_friendly_conversation(session, state)  
        else:  
            logger.info("Starting debate conversation...")  
            await run_debate_conversation(session, state)  
              
    except asyncio.CancelledError:  
        logger.info("Conversation cancelled by user")  
        state.conversation_active = False  
    except Exception as e:  
        logger.error(f"Error in conversation loop: {e}")  
        state.last_error = str(e)  
        state.conversation_active = False  
  
async def run_friendly_conversation(session: AgentSession, state: ConversationState):  
    """Friendly conversation between two collaborative agents"""  
      
    # Initial checkpoint  
    await verify_session_health(session, state)  

    await asyncio.sleep(2)  # Give time for full initialization  
      
    # Verify realtime session is ready  
    if hasattr(session._activity, '_rt_session') and session._activity._rt_session:  
        logger.info("Realtime session confirmed ready")  
    else:  
        logger.warning("Realtime session not ready, proceeding anyway")  
      
    # Start with first agent - use direct content instruction  
    await safe_generate_reply(  
        session, state,  
        instructions=topic,    
        voice="Puck",  
        speaker="agent1"  
    )  
      
    # Main conversation loop  
    while state.conversation_active and state.turn_count < state.max_turns:  
        await asyncio.sleep(3)  
          
        if not await verify_session_health(session, state):  
            break  
          
        state.turn_count += 1  
          
        if state.current_speaker == "agent1":  
            state.current_speaker = "agent2"  
            await safe_generate_reply(  
                session, state,  
                instructions=topic,   
                voice="Charon",  
                speaker="agent2"  
            )  
        else:  
            state.current_speaker = "agent1"  
            await safe_generate_reply(  
                session, state,  
                instructions=topic,  
                voice="Puck",  
                speaker="agent1"  
            )  
          
        logger.info(f"Completed turn {state.turn_count}/{state.max_turns}")
  
async def run_debate_conversation(session: AgentSession, state: ConversationState):  
    """Debate conversation between optimist and skeptic"""  
      
    # Initial checkpoint  
    await verify_session_health(session, state)  

    await asyncio.sleep(2)  # Give time for full initialization  
      
    # Verify realtime session is ready  
    if hasattr(session._activity, '_rt_session') and session._activity._rt_session:  
        logger.info("Realtime session confirmed ready")  
    else:  
        logger.warning("Realtime session not ready, proceeding anyway") 
      
    # Start with optimist perspective  
    await safe_generate_reply(  
        session, state,  
        instructions=topic,  # Direct content  
        voice="Puck",  
        speaker="optimist"  
    )  
      
    # Main conversation loop  
    while state.conversation_active and state.turn_count < state.max_turns:  
        await asyncio.sleep(3)  
          
        if not await verify_session_health(session, state):  
            break  
          
        state.turn_count += 1  
          
        if state.current_speaker == "optimist":  
            state.current_speaker = "skeptic"  
            await safe_generate_reply(  
                session, state,  
                instructions=topic,  # Direct content  
                voice="Charon",  
                speaker="skeptic"  
            )  
        else:  
            state.current_speaker = "optimist"  
            await safe_generate_reply(  
                session, state,  
                instructions=topic,  # Direct content  
                voice="Puck",  
                speaker="optimist"  
            )  
          
        logger.info(f"Completed turn {state.turn_count}/{state.max_turns}")
  
async def safe_generate_reply(  
    session: AgentSession,   
    state: ConversationState,   
    instructions: str,   
    voice: str,   
    speaker: str  
) -> bool:  
    """Safely generate a reply with error handling and retries"""  
      
    max_retries = 3  
    retry_count = 0  
      
    while retry_count < max_retries:  
        try:  
            # Checkpoint: Verify session before generating reply  
            if not session._started or session._activity is None:  
                logger.warning(f"Session not ready for {speaker}")  
                return False  
              
            # Check if session is draining  
            if session._activity.draining:  
                logger.warning(f"Session draining, cannot generate reply for {speaker}")  
                return False  
              
            # Update voice  
            if hasattr(session.llm, 'voice'):  
                session.llm.voice = voice  
              
            # Get conversation history for context  
            chat_history = session.history  
            recent_messages = []  
            if len(chat_history.items) > 1:  # Skip system message  
                # Get last 3 messages for context  
                recent_items = chat_history.items[-3:]  
                for item in recent_items:  
                    if hasattr(item, 'text_content') and item.text_content:  
                        recent_messages.append(item.text_content)  
              
            # Create context-aware instructions  
            if recent_messages:  
                context = " Previous context: " + " | ".join(recent_messages[-2:])  # Last 2 messages  
                contextual_instructions = f"{instructions}. {context}"  
            else:  
                contextual_instructions = instructions  
              
            # Generate reply with context  
            logger.info(f"{speaker.capitalize()} speaking (turn {state.turn_count + 1})")  
            speech_handle = session.generate_reply(user_input=contextual_instructions)  
              
            # Wait for speech to complete with timeout  
            try:  
                await asyncio.wait_for(speech_handle.wait_for_playout(), timeout=15.0)  
                logger.info(f"{speaker.capitalize()} finished speaking")  
                return True  
                  
            except asyncio.TimeoutError:  
                if retry_count < max_retries:  
                    logger.warning(f"Speech timeout for {speaker}, retrying...")  
                    retry_count += 1  
                    await asyncio.sleep(2)  
                    continue  
                else:  
                    logger.warning(f"Max retries exceeded for {speaker}")  
                    return False  
                      
        except RuntimeError as e:  
            if "closing" in str(e).lower() or "draining" in str(e).lower():  
                logger.warning(f"Session closing/draining for {speaker}: {e}")  
                state.session_healthy = False  
                return False  
            else:  
                retry_count += 1  
                logger.warning(f"RuntimeError for {speaker} (attempt {retry_count}): {e}")  
                if retry_count < max_retries:  
                    await asyncio.sleep(1)  
                    continue  
                else:  
                    logger.error(f"Max retries exceeded for {speaker}")  
                    return False  
                      
        except Exception as e:  
            retry_count += 1  
            logger.error(f"Unexpected error for {speaker} (attempt {retry_count}): {e}")  
            if retry_count < max_retries:  
                await asyncio.sleep(1)  
                continue  
            else:  
                state.last_error = str(e)  
                return False  
      
    return False
  
async def verify_session_health(session: AgentSession, state: ConversationState) -> bool:  
    """Verify session is healthy and ready for operations"""  
      
    try:  
        if not session._started:  
            logger.warning("Session not started")  
            state.session_healthy = False  
            return False  
          
        if session._activity is None:  
            logger.warning("Session activity is None")  
            state.session_healthy = False  
            return False  
          
        if session._activity.draining:  
            logger.warning("Session activity is draining")  
            state.session_healthy = False  
            return False  
          
        state.session_healthy = True  
        return True  
          
    except Exception as e:  
        logger.error(f"Error checking session health: {e}")  
        state.session_healthy = False  
        return False  
  
async def cleanup_session(session: AgentSession, state: ConversationState):  
    """Clean up session with proper error handling"""  
      
    logger.info("Starting session cleanup...")  
      
    try:  
        # Try to interrupt any ongoing speech  
        if session._started and session._activity and not session._activity.draining:  
            try:  
                await asyncio.wait_for(session.interrupt(), timeout=2.0)  
            except (asyncio.TimeoutError, RuntimeError):  
                logger.warning("Could not interrupt session cleanly")  
          
        # Drain the session  
        if session._started:  
            try:  
                await asyncio.wait_for(session.drain(), timeout=5.0)  
                logger.info("Session drained successfully")  
            except asyncio.TimeoutError:  
                logger.warning("Session drain timeout")  
            except RuntimeError as e:  
                logger.warning(f"Session drain error: {e}")  
          
        # Close the session  
        try:  
            await asyncio.wait_for(session.aclose(), timeout=3.0)  
            logger.info("Session closed successfully")  
        except asyncio.TimeoutError:  
            logger.warning("Session close timeout")  
        except Exception as e:  
            logger.error(f"Session close error: {e}")  
      
    except Exception as e:  
        logger.error(f"Critical error during cleanup: {e}")  
      
    # Final status report  
    logger.info(f"Conversation completed: {state.turn_count} turns, "  
                f"healthy: {state.session_healthy}, "  
                f"last_error: {state.last_error}")  
  
if __name__ == "__main__":  
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
