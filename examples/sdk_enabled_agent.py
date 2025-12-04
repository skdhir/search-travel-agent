"""
examples/sdk_enabled_agent.py

This script shows what an EXISTING agent looks like
AFTER integrating the HAP SDK.

Think of your old code as roughly:

    import requests

    def search_flights(origin, destination, date):
        resp = requests.get(
            "https://api.sanatdhir.com/api/flights/search",
            params={"origin": origin, "destination": destination, "date": date},
        )
        return resp

Now we:
  1. pip install hap-agent
  2. Paste agentId + privateKeyBase64 from AgentPassportHQ.
  3. Use the SDK's TravelAgent wrapper around HapAgentClient.
"""

from hap_agent.client import AgentConfig, HapAgentClient  # ✅ HAP SDK
from hap_agent.agent import TravelAgent                   # ✅ domain helper (flights)

API_BASE = "https://api.sanatdhir.com"

# 👉 Fill these from AgentPassportHQ (“New agent created – copy these values now”)
AGENT_ID = "agent_e5af7046fa544d91a6445499f7430511"
PRIVATE_KEY_B64 = "3VowD1Ig2r-AQMp_GygkqVRJ1Rx-dNTOP1WPicqRFfY"

def build_travel_agent() -> TravelAgent:
    """
    HAP-SPECIFIC SETUP (the important demo block).

    These ~6 lines are what you add to an existing agent:
      - create AgentConfig
      - create HapAgentClient
      - wrap it in TravelAgent (for flights)

    Everything else stays the same agent logic.
    """
    config = AgentConfig(
        api_base=API_BASE,
        agent_id=AGENT_ID,
        private_key_b64=PRIVATE_KEY_B64,
    )
    client = HapAgentClient(config)
    return TravelAgent(client)


def main():
    origin = "SFO"
    destination = "LAX"
    date = "2025-12-01"

    print("✅ DEMO: Agent AFTER integrating HAP SDK")
    print("   (uses hap-agent: signs requests, handles 402/payments, tracks credits)\n")

    agent = build_travel_agent()

    # Optional: show credits before the call
    credits = agent.get_current_credits()
    print(f"Current credits for this agent: {credits}")

    print(
        f"✈️  Searching flights {origin} → {destination} on {date} "
        f"as agent {AGENT_ID}"
    )

    # This method internally uses HapAgentClient + HAP headers + 402 handling.
    resp = agent.search_flights(origin, destination, date)

    # TravelAgent already prints a nice summary, but we can still return resp
    return resp


if __name__ == "__main__":
    main()