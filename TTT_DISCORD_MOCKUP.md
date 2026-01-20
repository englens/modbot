# TTT Discord Interface Mockup

## Channel Structure

```
📁 TTT GAME CATEGORY
├── 📖 ttt-rules (read-only)
├── 🎮 ttt-game-board (read-only, bot posts here)
├── ⚔️ ttt-actions (players submit commands here)
├── 💬 ttt-chat (players discuss strategy)
└── 👻 ttt-graveyard (only visible to downed players)
```

---

## Example: Game Board Message (Auto-Updated)

```
╔════════════════════════════════════════════╗
║         🎮 TTT GAME - TURN 12              ║
║    ⏰ Time Remaining: 6h 23m                ║
║    👥 Players Submitted: 8/12              ║
╚════════════════════════════════════════════╝

[ATTACHED IMAGE: 16x16 grid visualization]

┌─────────────────────────────────────────┐
│  LEGEND                                 │
├─────────────────────────────────────────┤
│  🟢 A - PlayerOne        ❤️ 3  🎯 Rng:2  │
│  🟢 B - PlayerTwo        ❤️ 4  🎯 Rng:3  │
│  🟢 C - AliceInChains    ❤️ 2  🎯 Rng:2  │
│  🟢 D - BobTheBuilder    ❤️ 5  🎯 Rng:2  │
│  🔴 E - DeadPlayer      💀 DOWNED        │
│  🟢 F - FastRunner       ❤️ 3  🎯 Rng:4  │
│  ...                                    │
│                                         │
│  💖 = Heart Spawn                       │
│  📦 = Loot Drop (3 AP)                  │
│  🟩 = Alive Player                      │
│  🟥 = Downed Player                     │
└─────────────────────────────────────────┘

Recent Events:
• PlayerTwo attacked AliceInChains! (-1 ❤️)
• FastRunner upgraded range (Rng: 3 → 4)
• BobTheBuilder picked up a heart! (+1 ❤️)
• Heart spawned at (7, 11)!
```

---

## Example: Grid Image Visualization

```
Actual rendered PNG would look like:

  0 1 2 3 4 5 6 7 8 9 A B C D E F
0 ░ ░ 🟢 ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░
  ░ ░ A ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░
1 ░ ░ ░ ░ ░ 🟢 ░ ░ ░ ░ ░ ░ ░ ░ ░ ░
  ░ ░ ░ ░ ░ B ░ ░ ░ ░ ░ ░ ░ ░ ░ ░
2 ░ ░ ░ ░ ░ ░ ░ 💖 ░ ░ ░ ░ ░ ░ ░ ░
3 ░ ░ ░ ░ ░ ░ ░ ░ ░ 🟢 ░ ░ ░ ░ ░ ░
  ░ ░ ░ ░ ░ ░ ░ ░ ░ C ░ ░ ░ ░ ░ ░
4 ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ 🟥 ░ ░ ░ ░
  ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ E ░ ░ ░ ░
5 ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░
6 ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ 📦 ░ ░
7 ░ ░ 🟢 ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░
  ░ ░ D ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░
...

With actual graphics:
- Each cell is 32x32 pixels
- Player letters overlaid on colored squares
- Gradient backgrounds
- Borders between cells
- Mini heart/AP icons for items
```

---

## Example: Player Commands (in #ttt-actions)

```
@PlayerOne
/ttt move north
✅ You moved north to (2, 1). Turn submitted!

@PlayerTwo
/ttt attack @AliceInChains
✅ You attacked AliceInChains for 1 damage! Turn submitted!

@AliceInChains
/ttt give_hearts @BobTheBuilder 1
✅ You gave 1 heart to BobTheBuilder. Turn submitted!

@BobTheBuilder
/ttt upgrade_range
✅ You upgraded your range! (2 → 3) Spent 3 AP. Turn submitted!

@DeadPlayer
/ttt vote_haunt @FastRunner
❌ You are not downed. Only downed players can vote.
```

---

## Example: DM from Bot (Secret Info)

```
🎮 TTT Game Update - Turn 12

Your Status:
├─ Position: (5, 7)
├─ ❤️ Hearts: 3 (visible) + 1 (secret) = 4 total
├─ ⚡ Action Points: 7 (SECRET - don't reveal!)
├─ 🎯 Range: 3 squares
└─ ✅ Turn Status: Submitted

Players in Range:
├─ 🟢 AliceInChains (6, 8) - 2 ❤️ visible
├─ 🟢 FastRunner (4, 5) - 3 ❤️ visible
└─ 🟥 DeadPlayer (7, 7) - DOWNED

Available Actions This Turn:
You already submitted: MOVE NORTH
(Turn will process when timer ends)

Tip: You have enough AP to upgrade your range!
```

---

## Example: Turn End Processing

```
╔═══════════════════════════════════════╗
║      🔔 TURN 12 PROCESSING            ║
╚═══════════════════════════════════════╝

Processing 12 actions...

⚔️ Combat:
• PlayerTwo attacked AliceInChains (-1 ❤️)
• AliceInChains is now at 1 ❤️!

🏃 Movement:
• PlayerOne moved from (2, 2) → (2, 1)
• FastRunner moved from (9, 3) → (9, 2)
• BobTheBuilder moved from (7, 2) → (8, 2) and picked up 💖 Heart!

🎁 Trading:
• AliceInChains gave 1 ❤️ to BobTheBuilder
• BobTheBuilder now has 5 ❤️!

⚡ Upgrades:
• BobTheBuilder upgraded range (2 → 3)

⏰ Missed Turns:
• SlowPlayer missed their turn! (-1 ❤️)
• SlowPlayer now at 2 ❤️

╔═══════════════════════════════════════╗
║      🎮 TURN 13 STARTING              ║
║    ⏰ Deadline: Jan 21, 2026 12:00 PM ║
╚═══════════════════════════════════════╝

Submit your actions with /ttt commands!
```

---

## Example: Random Event

```
🎉 RANDOM EVENT! 🎉

A 💖 HEART has spawned at position (11, 7)!

First player to move there gets +1 ❤️!

[Updated board image posted]
```

---

## Example: Daily AP Grant

```
☀️ DAILY ACTION POINT GRANT ☀️

All active players have received +1 AP!
(Check your DMs for your new total)

⚠️ Haunted Today:
• FastRunner will NOT receive AP today
  (Jury vote: 4 votes against)

🌟 Blessed Today:
• BobTheBuilder received +3 AP bonus!
  (Jury vote: 5 votes for intercession)
```

---

## Example: Player Status Command

```
@PlayerOne
/ttt status

(Bot DMs you:)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🎮 YOUR GAME STATUS - TURN 12
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Position: Row 5, Column 7

❤️ Hearts:
├─ Visible: 3 ❤️
├─ Secret: 1 ❤️ (hidden from others)
└─ Total: 4 ❤️

⚡ Action Points: 7 AP
   (🤫 Keep this secret!)

🎯 Range: 3 squares
   (Can attack/trade 3 squares away)

🎲 Turn Status: ✅ SUBMITTED
   Action: MOVE NORTH

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       PLAYERS WITHIN RANGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 AliceInChains (6, 8)
   └─ 2 ❤️ visible | Range: 2

🟢 FastRunner (4, 5)
   └─ 3 ❤️ visible | Range: 4

🟥 DeadPlayer (7, 7)
   └─ DOWNED - can be revived!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         AVAILABLE ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You already submitted this turn.
Next turn you can:

• /ttt move <direction>
• /ttt attack <player>
• /ttt upgrade_range (costs 3 AP) ✅ CAN AFFORD
• /ttt add_heart (costs 3 AP) ✅ CAN AFFORD
• /ttt give_hearts <player> <amount>
• /ttt give_ap <player> <amount> (max 3)
• /ttt pass

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Example: Jury Voting (#ttt-graveyard)

```
👻 Welcome to the Graveyard! 👻

As a downed player, you can influence the game through voting:

1️⃣ HAUNT Vote (/ttt vote_haunt <player>)
   → Player with most votes gets NO AP tomorrow

2️⃣ INTERCESSION Vote (/ttt vote_intercession <player>)
   → Any player with 3+ votes gets +3 AP

Votes are SECRET and reset daily!

Current Downed Players:
• DeadPlayer (Turn 8)
• UnluckyPlayer (Turn 10)
• SniperVictim (Turn 11)

─────────────────────────────────

@DeadPlayer
/ttt vote_haunt @FastRunner

✅ Your HAUNT vote for FastRunner has been recorded.
   (This is secret - no one else can see this)

@DeadPlayer
/ttt vote_intercession @BobTheBuilder

✅ Your INTERCESSION vote for BobTheBuilder has been recorded.
   (This is secret - no one else can see this)
```

---

## Example: Endgame - Placement Voting

```
╔═══════════════════════════════════════╗
║      🏁 ENDGAME - 4 PLAYERS LEFT      ║
╚═══════════════════════════════════════╝

Current Standings:

🥇 1st Place: BobTheBuilder
   └─ 6 ❤️ | 12 AP | Range: 5

🥈 2nd Place: FastRunner
   └─ 5 ❤️ | 8 AP | Range: 4

🥉 3rd Place: PlayerOne
   └─ 4 ❤️ | 7 AP | Range: 3

4th Place: AliceInChains
   └─ 3 ❤️ | 5 AP | Range: 2

─────────────────────────────────────────

Do you agree with this placement?

✅ /ttt agree_placement - Accept standings
❌ Continue playing until 3 remain

Votes to Accept: 0/4
(Requires unanimous agreement)

─────────────────────────────────────────

@BobTheBuilder
/ttt agree_placement

✅ BobTheBuilder agrees with the standings! (1/4)

@FastRunner
/ttt agree_placement

✅ FastRunner agrees with the standings! (2/4)

@PlayerOne
I want to keep playing!

(No vote yet)

─────────────────────────────────────────

Not unanimous. Game continues!

TURN 47 STARTING...
```

---

## Example: Final Results

```
╔═══════════════════════════════════════════════╗
║           🎉 GAME OVER! 🎉                    ║
║          TTT GAME #1 COMPLETE                 ║
║        Jan 15 - Jan 28, 2026                  ║
╚═══════════════════════════════════════════════╝

═══════════════════════════════════════════════
              FINAL STANDINGS
═══════════════════════════════════════════════

🥇 1st Place: BobTheBuilder
   └─ 6 ❤️ | 12 AP | Range: 5
   └─ 🏆 Awards: Most Hearts, Longest Survivor

🥈 2nd Place: FastRunner
   └─ 5 ❤️ | 8 AP | Range: 4
   └─ ⚡ Awards: Highest Range, Speed Demon

🥉 3rd Place: PlayerOne
   └─ 4 ❤️ | 7 AP | Range: 3
   └─ 🤝 Awards: Most Generous (gave 15 hearts)

═══════════════════════════════════════════════
              GAME STATISTICS
═══════════════════════════════════════════════

📊 Total Turns: 52
⏱️ Duration: 13 days
👥 Players: 16
⚔️ Total Attacks: 87
💀 Players Downed: 13
🔄 Revivals: 3
💖 Hearts Given: 45
⚡ AP Traded: 78
📈 Most Kills: PlayerTwo (5)
🎯 Highest Range: FastRunner (5)
💰 Most AP Earned: BobTheBuilder (47)

═══════════════════════════════════════════════
            SPECIAL ACHIEVEMENTS
═══════════════════════════════════════════════

🗡️ First Blood: PlayerTwo
💀 First Downed: UnluckyPlayer (Turn 3)
🏃 Pacifist: AliceInChains (0 attacks)
😈 Warmonger: PlayerTwo (5 kills)
🤝 Team Player: PlayerOne (15 hearts given)
🧙 Sorcerer: FastRunner (Range 5)
💪 Tank: BobTheBuilder (Max 8 hearts)
👻 Haunted Souls: FastRunner (haunted 4 times)
😇 Blessed: BobTheBuilder (3 intercessions)

═══════════════════════════════════════════════

Thanks for playing! 🎮

Next game starts: TBD
Use /ttt join to register for the next game!
```

---

## Example: Help Command

```
@PlayerOne
/ttt help

╔═══════════════════════════════════════════════╗
║            TTT - HELP GUIDE                   ║
╚═══════════════════════════════════════════════╝

📖 GAME COMMANDS:
├─ /ttt join - Join the next game
├─ /ttt board - View current game board
├─ /ttt status - Check your stats (DM)
├─ /ttt help - Show this help
└─ /ttt rules - View full rules

⚔️ ACTION COMMANDS (1 per turn):
├─ /ttt move <direction> - Move N/S/E/W (1 AP)
├─ /ttt attack <player> - Attack player in range (1 AP)
├─ /ttt upgrade_range - Increase range by 1 (3 AP)
├─ /ttt add_heart - Gain 1 heart (3 AP)
└─ /ttt pass - Do nothing

🤝 SOCIAL ACTIONS (1 per turn, in addition to above):
├─ /ttt give_hearts <player> <amount> - Give hearts
└─ /ttt give_ap <player> <amount> - Give AP (max 3)

👻 JURY COMMANDS (Downed players only):
├─ /ttt vote_haunt <player> - Vote to deny AP
└─ /ttt vote_intercession <player> - Vote to grant 3 AP

🏁 ENDGAME COMMANDS:
└─ /ttt agree_placement - Accept current standings

📚 For full rules: /ttt rules
💬 For strategy tips: /ttt strategy

Need help? Ask in #ttt-chat!
```

---

## UI/UX Considerations

### Color Coding (for images):
- 🟩 Green: Alive players (gradient based on hearts)
- 🟥 Red: Downed players
- 💛 Yellow: Items (hearts, loot)
- ⬜ White/Gray: Empty squares
- 🟦 Blue: Danger zone (grid shrinking)
- 🟪 Purple: Your player (in personalized view)

### Emojis:
- ❤️ Hearts (health)
- ⚡ Action Points
- 🎯 Range
- 💀 Downed
- 🏆 Winner
- ⚔️ Combat
- 🏃 Movement
- 🎁 Trading
- 👻 Jury/Ghost
- 📦 Loot
- 💖 Heart spawn

### Notifications:
- Turn timer warnings (6h, 3h, 1h, 30m, 5m)
- Daily AP grants
- Random spawns
- Jury vote results
- Combat results
- Turn processing complete
- Game phase changes

### Privacy:
- AP counts: ALWAYS DM, never public
- Secret hearts (>3): Only in DMs
- Jury votes: DM confirmations
- Player strategies: Keep in DMs/private channels

### Accessibility:
- Text alternatives to images
- Clear command syntax
- Help available everywhere
- Confirm all actions
- Undo for accidental commands? (before turn processes)
