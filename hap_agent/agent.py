import json
from typing import Dict, Any, Optional

from .client import HapAgentClient


class TravelAgent:
    """
    Very simple 'agentic' wrapper around HapAgentClient.

    Responsibilities:
    - Call /api/flights/search with signed requests
    - Handle 200 vs 402
    - (Optionally) check credits via /api/billing/agents
    """

    def __init__(self, client: HapAgentClient, verbose: bool = True):
        self.client = client
        self.verbose = verbose

    # --- helper printing ---

    def _log(self, *args):
        if self.verbose:
            print(*args)

    # --- core behaviors ---

    def get_wallet_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Call /api/billing/agents and return THIS agent's wallet row, if any.
        (In a future multi-tenant world this endpoint will be admin-only,
        but for your MVP it's fine.)
        """
        resp = self.client.request("GET", "/api/billing/agents")
        if resp.status_code != 200:
            self._log("Failed to fetch billing snapshot:", resp.status_code, resp.text)
            return None

        data = resp.json()
        wallets = data.get("wallets", [])
        for w in wallets:
            if w.get("agentId") == self.client.config.agent_id:
                return w
        return None

    def get_current_credits(self) -> int:
        wallet = self.get_wallet_snapshot()
        if not wallet:
            return 0
        return int(wallet.get("credits", 0))

    def search_flights(self, origin: str, destination: str, date: str) -> Dict[str, Any]:
        """
        High-level API:
        - Tries /api/flights/search as an agent.
        - Handles 200 vs 402.
        - On 402, prints checkout URL and stops.
        """
        self._log(f"✈️  Searching flights {origin} → {destination} on {date} as agent {self.client.config.agent_id}")

        query = {"origin": origin, "destination": destination, "date": date}
        resp = self.client.request("GET", "/api/flights/search", query=query)

        self._log("Status:", resp.status_code, resp.reason)

        try:
            data = resp.json()
        except Exception:
            self._log("Non-JSON response:", resp.text)
            raise

        # Payment required: point a human at Stripe checkout
        if resp.status_code == 402:
            checkout_url = data.get("checkoutUrl")
            self._log("💸 Payment required.")
            self._log("   Checkout URL:", checkout_url)
            self._log("   After completing payment, re-run this method.")
            return data

        if resp.status_code != 200:
            self._log("Unexpected status:", resp.status_code)
            self._log(json.dumps(data, indent=2))
            return data

        self._log("✅ Flight search successful.")
        self._log(json.dumps(data, indent=2))
        return data
