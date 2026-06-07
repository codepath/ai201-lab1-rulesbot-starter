def chunk_document(text, game_name):
    """
    Split a rule document into chunks ready for embedding.

    This function is already implemented — read through it and the inline
    comments before moving on. The decisions made here directly shape what
    retrieval returns in Milestones 2 and 3, so it's worth understanding
    before you build on top of it.

    Strategy: character-based sliding window with overlap.
      - chunk_size = 300 characters: long enough to carry the semantic
        meaning of a single rule, short enough to return targeted results
      - overlap = 50 characters: duplicates a small window of text at each
        boundary so a rule that spans two chunks can still be retrieved intact
      - min_length = 50 characters: filters out whitespace artifacts and
        very short fragments that add noise without useful semantic content

    Returns a list of dicts, each with:
      - "text"     : the chunk text (str)
      - "game"     : the game name, e.g. "Catan" (str)
      - "chunk_id" : a unique identifier, e.g. "catan_0", "catan_1" (str)
    """
    chunk_size = 300
    overlap = 50
    min_length = 50

    chunks = []
    prefix = game_name.lower().replace(" ", "_")
    counter = 0

    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()
        print(chunk_text+"\n")
        print("--------------------------------------------------------------------------")
        if len(chunk_text) >= min_length:
            chunks.append({
                "text": chunk_text,
                "game": game_name,
                "chunk_id": f"{prefix}_{counter}",
            })
            counter += 1

        # Advance by (chunk_size - overlap) so the next chunk shares
        # `overlap` characters with the tail of this one.
        start += chunk_size - overlap

    return chunks


text = '''
CATAN — OFFICIAL RULES SUMMARY

OVERVIEW
Catan is a strategy board game for 3–4 players (5–6 with an expansion). Players take on the roles of settlers, building roads, settlements, and cities on the island of Catan. The goal is to be the first player to earn 10 Victory Points on your turn.

COMPONENTS
The game includes 19 terrain hexes, 6 sea frame pieces, 9 harbor pieces, 18 circular number tokens, 95 resource cards (19 of each: Brick, Lumber, Ore, Grain, and Wool), 25 development cards, 4 building cost cards, 2 special cards (Longest Road and Largest Army), 16 cities, 20 settlements, 60 roads (in 4 colors), 2 dice, 1 robber, and 1 sand timer.

SETUP
Arrange the terrain hexes randomly (or use the beginner layout) inside the sea frame. Place the number tokens on the hexes in alphabetical order, following a clockwise spiral from a corner. Each player places two settlements and two roads on the board in reverse turn order: the last player to place their first settlement places their second first. Each player collects starting resources based on the terrain hexes adjacent to their second settlement only.

TURN STRUCTURE
Each turn consists of three phases, in this order:
1. Roll the dice.
2. Trade (optional).
3. Build (optional).

RESOURCE PRODUCTION
At the start of your turn, roll both dice. Every settlement adjacent to a hex with the rolled number produces one resource card of that hex's type. Every city adjacent to that hex produces two resource cards. If the robber is on a hex, that hex produces no resources that turn, regardless of the number rolled.

ROLLING A 7
When a 7 is rolled, no resources are produced. Every player with more than 7 resource cards in hand must discard half (rounded down). The player who rolled moves the robber to any terrain hex and steals one random resource card from a player with a settlement or city adjacent to that hex.

TRADING
You may trade resource cards with other players or with the bank. Bank trades are always 4-for-1: give the bank 4 identical resource cards, take 1 of any resource. Harbor trades reduce this ratio. A generic harbor (marked with a circle and "3:1") lets you trade any 3 identical resources for 1 of any type. Specific harbors (marked with a resource icon and "2:1") let you trade 2 of that specific resource for 1 of any type. You can only use a harbor if you have a settlement or city on one of its two coastal intersections. You may trade with other players at any mutually agreed ratio — this is negotiated freely during your turn.

BUILDING
Settlements cost 1 Brick + 1 Lumber + 1 Grain + 1 Wool. They must be placed at an intersection (a corner where hexes meet) that is connected to one of your existing roads, and no closer than two intersections from any other settlement or city (the Distance Rule). Settlements are worth 1 Victory Point each.

Cities cost 2 Grain + 3 Ore and are built by upgrading an existing settlement. Remove the settlement and replace it with a city. Cities are worth 2 Victory Points each and produce double resources.

Roads cost 1 Brick + 1 Lumber and must be placed on a path (an edge between two intersections) connected to one of your roads, settlements, or cities. Roads cannot be placed through an opponent's settlement or city.

Development cards cost 1 Ore + 1 Grain + 1 Wool. Draw the top card of the face-down development deck. Development cards cannot be played on the turn they are purchased. You may play at most one development card per turn.

DEVELOPMENT CARDS
Knight cards: Move the robber and steal a resource as if you had rolled a 7. Collecting 3 or more knights earns the Largest Army special card (2 Victory Points). Progress cards (Road Building, Year of Plenty, Monopoly) have powerful one-time effects. Victory Point cards are revealed only when you win.

LONGEST ROAD
The Longest Road special card is worth 2 Victory Points and is awarded to the first player to build a continuous road of at least 5 segments. If another player builds a longer road, they take the card. Roads cannot branch — only the longest single continuous path counts.

WINNING
The first player to reach 10 Victory Points on their own turn wins immediately. Victory Points come from settlements (1 each), cities (2 each), Longest Road (2), Largest Army (2), and Victory Point development cards.


'''
chunks = chunk_document(text, "Catan")