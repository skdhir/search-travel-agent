from hap_agent.client import AgentConfig, HapAgentClient
from hap_agent.agent import TravelAgent


def main():
    # TODO: fill these from your agents.html JSON
    API_BASE = "https://api.sanatdhir.com"

    config = AgentConfig(
        api_base=API_BASE,
        agent_id=AGENT_ID,
        private_key_b64=PRIVATE_KEY_B64,
    )
    client = HapAgentClient(config)
    agent = TravelAgent(client)

    # See current credits (optional)
    credits = agent.get_current_credits()
    print("Current credits:", credits)

    # Try a flight search
    agent.search_flights("SFO", "LAX", "2025-12-01")


if __name__ == "__main__":
    main()
