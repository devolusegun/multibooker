import uuid

def generate_bet9ja_bet_code(event_id: str, market: str, selection: str) -> str:
    """
    Simulate Bet9ja betslip code generation.
    This is a placeholder until we reverse engineer or automate true betslip building.

    Args:
        event_id (str): Event identifier (used as seed).
        market (str): Market key (e.g. match_result).
        selection (str): Selection key (e.g. home, draw).

    Returns:
        str: Fake betslip code.
    """
    seed = f"{event_id}-{market}-{selection}"
    code = uuid.uuid5(uuid.NAMESPACE_DNS, seed).hex[:8].upper()
    return f"B9JA-{code}"
