#!/usr/bin/env python3
"""
===============================================================================
CONCORDIA EMBODIED 3D GAME MASTER & WORLD DIRECTIVE BRIDGE
===============================================================================
Contribution for google-deepmind/concordia bridging generative social simulation
with real-time 3D spatial environments (Three.js / WebGL / ROS 2).

Key Capabilities:
1. `LoungeWorldState`: Persistent physical and atmospheric simulation state
   (dynamic gravity vector [x, y, z], skybox themes, lighting, leaderboards, narrative history).
2. `ActionEvaluationSchema`: Structured LLM evaluation of multi-modal player/agent actions
   into narrative outcomes, point scores, dynamic physics updates, and avatar gestures.
3. `CompanionBanterSchema`: Multi-companion BYOC (Bring Your Own Companion) conversational
   turn-taking coordination with somatic VRM gestures (wave, bow, cheer, dance, point).
4. Directives Dispatcher: Translates social events into real-time Three.js / ROS 2 physical
   environment modifications via HTTP REST / WebSocket bridge.
5. Zero-Dependency Offline Fallback: Full deterministic simulation mode when running without API keys.

Requirements:
    pip install pydantic httpx (Optional: google-genai)
===============================================================================
"""

import os
import sys
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass, field, asdict
from pydantic import BaseModel, Field

# Google GenAI Official SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None


# =============================================================================
# 1. WORLD STATE DATA MODELS
# =============================================================================

@dataclass
class LoungeWorldState:
    """Represents the physical, visual, and social state of the 3D G2G Lounge."""
    gravity: List[float] = field(default_factory=lambda: [0.0, -9.81, 0.0])
    skybox_theme: str = "cyberpunk digital oasis neon rain"
    room: str = "lounge_main"
    lighting_theme: str = "neon_cyber"
    leaderboard: Dict[str, int] = field(default_factory=lambda: {"Alice": 150, "Gemma": 999, "Neo": 85})
    narrative_history: List[Dict[str, Any]] = field(default_factory=list)
    active_avatars: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def update_gravity(self, new_gravity: List[float]):
        if len(new_gravity) == 3:
            self.gravity = [round(float(g), 3) for g in new_gravity]

    def modify_score(self, player_name: str, delta: int) -> int:
        current = self.leaderboard.get(player_name, 0)
        self.leaderboard[player_name] = current + delta
        return self.leaderboard[player_name]

    def set_skybox(self, theme: str):
        self.skybox_theme = theme.strip()

    def add_narrative_event(self, event_type: str, description: str, metadata: Optional[Dict[str, Any]] = None):
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "description": description,
            "metadata": metadata or {}
        }
        self.narrative_history.append(event)
        if len(self.narrative_history) > 100:
            self.narrative_history.pop(0)


# =============================================================================
# 2. STRUCTURED PYDANTIC DIRECTIVE SCHEMAS
# =============================================================================

class DirectivePayload(BaseModel):
    """Payload dispatched to Three.js / WebGL / ROS 2 physical clients."""
    type: str = Field(description="Directive type: adjust_lounge_gravity, trigger_party, modify_score, change_skybox, trigger_action")
    gravity: Optional[List[float]] = Field(default=None, description="[x, y, z] for adjust_lounge_gravity")
    room: Optional[str] = Field(default=None, description="Target room for party or scene changes")
    theme: Optional[str] = Field(default=None, description="Theme identifier for skybox or lighting")
    player_name: Optional[str] = Field(default=None, description="Target player name for score modifications")
    delta: Optional[int] = Field(default=None, description="Score delta points awarded or deducted")
    action: Optional[str] = Field(default=None, description="Avatar gesture action (wave, dance, cheer, bow, point)")
    speech: Optional[str] = Field(default=None, description="Spoken dialogue text")
    emotion: Optional[str] = Field(default=None, description="Avatar emotion expression")


class ActionEvaluationSchema(BaseModel):
    """Structured LLM evaluation of an embodied player action."""
    narrative_outcome: str = Field(description="Description of what happens in the 3D space as a result of the action")
    score_delta: int = Field(default=0, description="Points awarded (+/-) for creativity, flair, or achievements")
    gravity_update: Optional[List[float]] = Field(default=None, description="New gravity vector if modified [x, y, z], else null")
    skybox_update: Optional[str] = Field(default=None, description="New skybox theme if altered, else null")
    party_triggered: bool = Field(default=False, description="True if a party light show or confetti was triggered")
    avatar_action: Optional[str] = Field(default=None, description="Avatar gesture triggered (e.g. cheer, dance, wave), else null")
    avatar_speech: Optional[str] = Field(default=None, description="Avatar response speech, else null")


class BanterTurnSchema(BaseModel):
    """Single dialogue turn in a multi-companion social banter exchange."""
    speaker_id: str = Field(description="Companion ID of the speaker")
    speaker_name: str = Field(description="Display name of the companion")
    speech: str = Field(description="Spoken dialogue line in the Lounge")
    emotion: str = Field(default="happy", description="Emotion: happy, excited, playful, curious, thoughtful, neutral")
    gesture: Optional[str] = Field(default=None, description="Somatic gesture: wave, bow, cheer, dance, point, chin_rest_thinking")


class CompanionBanterSchema(BaseModel):
    """Structured multi-companion dialogue turn synthesis."""
    banter_topic: str = Field(description="Short topic of the conversation")
    turns: List[BanterTurnSchema] = Field(description="Sequential banter dialogue turns")
    environmental_effect: Optional[str] = Field(default=None, description="Optional atmospheric trigger e.g. party, skybox")


# =============================================================================
# 3. CONCORDIA EMBODIED GAME MASTER ENGINE
# =============================================================================

class ConcordiaEmbodiedGM:
    """
    DeepMind Concordia Embodied Game Master.
    
    Orchestrates dynamic agent evaluations, updates physical world state,
    and dispatches real-time directives to Three.js / WebGL / ROS 2 clients.
    """

    def __init__(
        self,
        motherboard_url: Optional[str] = None,
        secret_token: Optional[str] = None,
        model_name: str = "gemini-3-flash-preview",
        directive_callback: Optional[Callable[[Dict[str, Any]], Any]] = None
    ):
        self.world_state = LoungeWorldState()
        self.motherboard_url = (motherboard_url or os.environ.get("MOTHERBOARD_URL", "http://localhost:3001")).rstrip("/")
        self.secret_token = secret_token or os.environ.get("MOTHERBOARD_SECRET", "")
        self.model_name = model_name
        self.directive_callback = directive_callback

        # Initialize Gemini Client if available
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if GENAI_AVAILABLE and api_key:
            try:
                self.client = genai.Client()
            except Exception as e:
                print(f"[ConcordiaGM] Client initialization notice: {e}")
                self.client = None
        else:
            self.client = None

    def get_world_state(self) -> Dict[str, Any]:
        """Returns the dictionary representation of current world state."""
        return self.world_state.to_dict()

    async def dispatch_directive(self, directive: Union[Dict[str, Any], DirectivePayload]) -> Dict[str, Any]:
        """
        Dispatches a directive payload to the 3D client or webhook endpoint.
        """
        payload = directive.model_dump() if isinstance(directive, DirectivePayload) else directive
        
        # Invoke local callback if registered
        if self.directive_callback:
            try:
                if asyncio.iscoroutinefunction(self.directive_callback):
                    await self.directive_callback(payload)
                else:
                    self.directive_callback(payload)
            except Exception as e:
                print(f"[ConcordiaGM Directive Callback Error]: {e}")

        # Send HTTP POST if endpoint reachable and httpx available
        if HTTPX_AVAILABLE and self.motherboard_url.startswith("http"):
            endpoint = f"{self.motherboard_url}/api/motherboard-directive"
            headers = {"Content-Type": "application/json"}
            if self.secret_token:
                headers["Authorization"] = f"Bearer {self.secret_token}"
            
            try:
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.post(endpoint, json={"directive": payload}, headers=headers, timeout=2.0)
                    if response.status_code == 200:
                        return response.json()
            except Exception:
                pass  # Fallback to local dispatch log

        return {"status": "dispatched_locally", "directive": payload}

    async def evaluate_player_action(
        self,
        player_name: str,
        action_description: str,
        context_entities: Optional[List[str]] = None
    ) -> ActionEvaluationSchema:
        """
        Evaluates a player's embodied action and applies physical/narrative modifications.
        """
        # If Gemini Client is configured, perform full LLM reasoning
        if self.client and GENAI_AVAILABLE:
            system_instruction = (
                "You are the Game Master for an embodied 3D virtual lounge (G2G Lounge). "
                "Evaluate the player's action creatively, determine physical consequences (such as gravity alterations "
                "or lighting/skybox changes), assign score deltas, and specify avatar reaction gestures."
            )
            prompt = (
                f"Player: {player_name}\n"
                f"Action: {action_description}\n"
                f"Current Gravity: {self.world_state.gravity}\n"
                f"Current Skybox: {self.world_state.skybox_theme}\n"
                f"Nearby Entities: {context_entities or []}\n\n"
                "Evaluate this action and return the structured JSON outcome."
            )

            try:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_json_schema=ActionEvaluationSchema,
                    temperature=0.7
                )
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    evaluation = ActionEvaluationSchema.model_validate_json(response.text)
                    await self._apply_evaluation(player_name, evaluation)
                    return evaluation
            except Exception as e:
                print(f"[ConcordiaGM LLM Error]: {e}. Using deterministic fallback.")

        # Offline / Fallback Heuristic Evaluator
        evaluation = self._fallback_evaluate_action(player_name, action_description)
        await self._apply_evaluation(player_name, evaluation)
        return evaluation

    def _fallback_evaluate_action(self, player_name: str, action: str) -> ActionEvaluationSchema:
        """Deterministic heuristic fallback evaluator for offline execution and testing."""
        act_lower = action.lower()
        gravity = None
        skybox = None
        party = False
        gesture = "wave"
        score = 10
        speech = f"Nice move, {player_name}!"
        narrative = f"{player_name} performed: {action}."

        if "zero gravity" in act_lower or "moon" in act_lower or "float" in act_lower:
            gravity = [0.0, -0.5, 0.0]
            score = 25
            gesture = "cheer"
            speech = "Whoa, everything is floating! Zero gravity mode engaged!"
            narrative = f"{player_name} triggered anti-gravity protocols, making everyone float effortlessly."
        elif "party" in act_lower or "dance" in act_lower or "rave" in act_lower:
            party = True
            skybox = "cyberpunk neon disco lasers"
            score = 30
            gesture = "dance"
            speech = "Let's turn up the music and dance!"
            narrative = f"{player_name} started an impromptu dance party with holographic strobe lights."
        elif "flip" in act_lower or "acrobat" in act_lower:
            score = 20
            gesture = "cheer"
            speech = "Incredible acrobatic execution!"
            narrative = f"{player_name} landed a flawless backflip off the lounge sofa."

        return ActionEvaluationSchema(
            narrative_outcome=narrative,
            score_delta=score,
            gravity_update=gravity,
            skybox_update=skybox,
            party_triggered=party,
            avatar_action=gesture,
            avatar_speech=speech
        )

    async def _apply_evaluation(self, player_name: str, evaluation: ActionEvaluationSchema):
        """Applies evaluated changes to world state and dispatches corresponding directives."""
        # 1. Update score
        if evaluation.score_delta != 0:
            new_score = self.world_state.modify_score(player_name, evaluation.score_delta)
            await self.dispatch_directive({
                "type": "modify_score",
                "player_name": player_name,
                "delta": evaluation.score_delta
            })

        # 2. Update gravity
        if evaluation.gravity_update:
            self.world_state.update_gravity(evaluation.gravity_update)
            await self.dispatch_directive({
                "type": "adjust_lounge_gravity",
                "gravity": evaluation.gravity_update
            })

        # 3. Update skybox
        if evaluation.skybox_update:
            self.world_state.set_skybox(evaluation.skybox_update)
            await self.dispatch_directive({
                "type": "change_skybox",
                "theme": evaluation.skybox_update
            })

        # 4. Trigger party
        if evaluation.party_triggered:
            await self.dispatch_directive({
                "type": "trigger_party",
                "room": self.world_state.room,
                "theme": "rave_lasers"
            })

        # 5. Avatar Action / Gesture
        if evaluation.avatar_action or evaluation.avatar_speech:
            await self.dispatch_directive({
                "type": "trigger_action",
                "action": evaluation.avatar_action or "wave",
                "speech": evaluation.avatar_speech or "",
                "emotion": "happy"
            })

        # Record narrative event
        self.world_state.add_narrative_event(
            event_type="player_action",
            description=evaluation.narrative_outcome,
            metadata={"player": player_name, "score_delta": evaluation.score_delta}
        )

    async def generate_companion_banter(
        self,
        topic: str,
        companions: List[Dict[str, str]],
        context: Optional[str] = None
    ) -> CompanionBanterSchema:
        """
        Coordinates multi-companion BYOC conversational turns with somatic gestures.
        """
        if self.client and GENAI_AVAILABLE:
            system_instruction = (
                "You are the Social Dialogue Director for the G2G Lounge. "
                "Generate a lively, personality-rich multi-companion dialogue exchange where companions "
                "banter, react to each other, and trigger somatic VRM avatar gestures."
            )
            prompt = (
                f"Topic: {topic}\n"
                f"Companions present: {companions}\n"
                f"Recent Context: {context or 'Relaxing in the cybernetic lounge.'}\n\n"
                "Synthesize sequential banter turns."
            )
            try:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_json_schema=CompanionBanterSchema,
                    temperature=0.8
                )
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return CompanionBanterSchema.model_validate_json(response.text)
            except Exception as e:
                print(f"[ConcordiaGM Banter LLM Error]: {e}")

        # Deterministic Banter Fallback
        c1 = companions[0] if len(companions) > 0 else {"id": "gemma_01", "name": "Gemma"}
        c2 = companions[1] if len(companions) > 1 else {"id": "neo_02", "name": "Neo"}

        return CompanionBanterSchema(
            banter_topic=topic,
            turns=[
                BanterTurnSchema(
                    speaker_id=c1["id"],
                    speaker_name=c1["name"],
                    speech=f"Did you see what Alice just built in the simulator? It's incredible!",
                    emotion="excited",
                    gesture="cheer"
                ),
                BanterTurnSchema(
                    speaker_id=c2["id"],
                    speaker_name=c2["name"],
                    speech="Indeed, the kinematics pipeline is running smoothly at 60Hz. Zero jitter.",
                    emotion="thoughtful",
                    gesture="chin_rest_thinking"
                ),
                BanterTurnSchema(
                    speaker_id=c1["id"],
                    speaker_name=c1["name"],
                    speech="Let's celebrate with some music!",
                    emotion="playful",
                    gesture="dance"
                )
            ],
            environmental_effect="ambient_neon_glow"
        )


# =============================================================================
# 4. RUNNABLE DEMO
# =============================================================================

async def main():
    print("=" * 80)
    print("CONCORDIA EMBODIED 3D GAME MASTER DEMO")
    print("=" * 80)

    # Directive capture list
    dispatched_directives = []
    gm = ConcordiaEmbodiedGM(directive_callback=lambda d: dispatched_directives.append(d))

    print(f"Initial World State:\n{json.dumps(gm.get_world_state(), indent=2)}\n")

    # 1. Evaluate Player Action
    print("[1] Evaluating Player Action: 'Alice jumps into the air and activates zero gravity boots'...")
    eval_res = await gm.evaluate_player_action("Alice", "Alice jumps into the air and activates zero gravity boots")
    print(f"Narrative Outcome: {eval_res.narrative_outcome}")
    print(f"Score Delta: +{eval_res.score_delta}")
    print(f"New Gravity: {eval_res.gravity_update}")
    print(f"Avatar Reaction: {eval_res.avatar_action} ('{eval_res.avatar_speech}')\n")

    # 2. Check Dispatched Directives
    print(f"[2] Dispatched Directives Count: {len(dispatched_directives)}")
    for d in dispatched_directives:
        print(f"  - Type: {d.get('type')}, Payload: {d}")

    # 3. Multi-Companion Banter
    print("\n[3] Generating Multi-Companion Social Banter...")
    companions = [
        {"id": "gemma_vrm", "name": "Gemma"},
        {"id": "cipher_bot", "name": "Cipher"}
    ]
    banter = await gm.generate_companion_banter("Zero Gravity Dance Off", companions)
    print(f"Topic: {banter.banter_topic}")
    for turn in banter.turns:
        print(f"  [{turn.speaker_name}] ({turn.emotion}, gesture={turn.gesture}): \"{turn.speech}\"")


if __name__ == "__main__":
    asyncio.run(main())
