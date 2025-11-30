# examples/run_agent.py
# ======= USAGE =====
# default agent (first in AGENT_PROFILES)
# python -m examples.run_agent

# explicitly pick one
# python -m examples.run_agent --agent sanat-main

# second agent
# python -m examples.run_agent --agent price-monitor

# try different routes / dates
# python -m examples.run_agent --agent price-monitor --origin JFK --destination SFO --date 2026-01-15
# ======= 

import argparse

from hap_agent.client import AgentConfig, HapAgentClient
from hap_agent.agent import TravelAgent


# 👇 fill these in from https://travel.sanatdhir.com/agents.html
API_BASE = "https://api.sanatdhir.com"

AGENT_PROFILES = {
    # Example: keep your existing agent here
    "travel-search": {
        "agent_id": "agent_f2b86a123f614776a64c12eab8e585d8",
        "private_key_b64": "vppzQk4oLuHgmHj7_76TsxTwAE6H8OHN0KQQXYYXl0E",
    },

    "price-monitor": {
        "agent_id": "agent_a6aee7548a374140981aaaa4fbe757b0",
        "private_key_b64": "E1--4WIlZ26OL5sEezaIrKPH0RDOamYGCPQG4m3lCtw",
    },
}

def build_travel_agent(profile_name: str) -> TravelAgent:
    if profile_name not in AGENT_PROFILES:
        raise SystemExit(
            f"Unknown agent profile '{profile_name}'. "
            f"Known profiles: {', '.join(AGENT_PROFILES.keys())}"
        )

    profile = AGENT_PROFILES[profile_name]
    config = AgentConfig(
        api_base=API_BASE,
        agent_id=profile["agent_id"],
        private_key_b64=profile["private_key_b64"],
    )
    client = HapAgentClient(config)
    return TravelAgent(client)


def main():
    parser = argparse.ArgumentParser(
        description="Run a HAP travel agent against api.sanatdhir.com"
    )
    parser.add_argument(
        "--agent",
        default=next(iter(AGENT_PROFILES.keys())),
        help=f"Which agent profile to use. Options: {', '.join(AGENT_PROFILES.keys())}",
    )
    parser.add_argument("--origin", default="SFO")
    parser.add_argument("--destination", default="LAX")
    parser.add_argument("--date", default="2025-12-01")

    args = parser.parse_args()

    agent = build_travel_agent(args.agent)

    credits = agent.get_current_credits()
    print(f"Current credits for agent '{args.agent}': {credits}")

    print(
        f"✈️  Searching flights {args.origin} → {args.destination} on {args.date} "
        f"as agent {agent.client.config.agent_id}"
    )

    resp = agent.search_flights(args.origin, args.destination, args.date)
    # resp already printed by TravelAgent; we just return it in case you want to inspect later
    return resp


if __name__ == "__main__":
    main()
