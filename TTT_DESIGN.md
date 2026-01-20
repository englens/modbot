# TTT Discord Game - Design & Implementation Plan

## Discord Adaptation Design

### Grid Visualization Solution

**Option 1: Auto-Updating Embed with Image (RECOMMENDED)**
- Generate a PNG/GIF image of the 16x16 grid using Python Pillow
- Post as an embed attachment that gets edited every turn
- Color-coded squares for: empty, players (alive), downed players, items (hearts/AP loot)
- Include player indicators with emoji/letters
- Legend below the grid

**Option 2: ASCII/Emoji Art**
- Use Discord emojis to create a visual grid
- Update a pinned message each turn
- Pros: No image generation needed
- Cons: 16x16 might be too large, emoji limits

**Option 3: Web Dashboard**
- External website showing live game state
- Link posted in Discord
- Pros: Best visuals, no Discord limitations
- Cons: More complex infrastructure

**DECISION: Go with Option 1** - Best balance of visibility and implementation complexity

### Discord-Specific Modifications

#### 1. Turn System
**Original:** 24 hour turn timer, first-come-first-served
**Discord Adaptation:**
- Turns tracked by Discord user ID
- Players submit actions via slash commands or reaction buttons
- Bot tracks who has submitted their action
- Turn ends when all players submit OR 24 hours pass (configurable for faster testing)
- Bot posts countdown timer updates (every 6 hours, then hourly for last 3 hours)

#### 2. Secret Information (Action Points)
**Solution:**
- DM players their current AP count after each action
- DM daily AP grants
- Main channel only shows public info (position, hearts, range)
- Use spoiler tags for hearts >3

#### 3. Action Input
**Slash Commands:**
- `/ttt move <direction>` - Move north/south/east/west
- `/ttt attack <player>` - Attack player in range
- `/ttt upgrade_range` - Spend 3 AP to increase range
- `/ttt add_heart` - Spend 3 AP to add a heart
- `/ttt give_hearts <player> <amount>` - Give hearts to player in range
- `/ttt give_ap <player> <amount>` - Give AP to player in range (max 3)
- `/ttt pass` - Do nothing this turn
- `/ttt status` - Check your current stats (DM only)
- `/ttt board` - Show current board state

**Admin Commands:**
- `/ttt start <players>` - Start new game
- `/ttt force_end_turn` - Force turn to end
- `/ttt game_status` - Show full game state

**Jury Commands (for downed players):**
- `/ttt vote_haunt <player>` - Vote to deny AP to a player
- `/ttt vote_intercession <player>` - Vote to grant 3 AP to a player

#### 4. Player Identification
**On Grid:**
- Each player assigned a letter (A-P for 16 players) or emoji
- Username + letter shown in legend
- Grid shows letter on their square

#### 5. Communication
**Channels:**
- `#ttt-game-board` - Read-only, bot posts board updates
- `#ttt-actions` - Players submit commands here
- `#ttt-graveyard` - Downed players discuss and vote
- DMs - Bot sends secret info (AP counts, private notifications)

#### 6. Timing Adjustments for Discord
**Configurable Settings:**
- Turn duration: 24 hours (production) / 5 minutes (testing)
- Daily AP grant: Once per 24 hours at random time
- Random heart spawn: Once per turn
- Random loot spawn: Random interval (every 2-5 turns)
- Grid shrink: Every 3 turns (optional mode)

#### 7. Range Visualization
When a player uses `/ttt status` or `/ttt board`, highlight:
- Their current position
- Squares within their range
- Players they can interact with

### Game State Management

**Database Structure (JSON via GameData):**
```json
{
  "ttt_game": {
    "active": true,
    "turn_number": 1,
    "turn_start_time": "2026-01-20T12:00:00",
    "grid_size": 16,
    "board": {
      "0,0": {"type": "player", "id": "user_123"},
      "5,7": {"type": "heart"},
      "8,3": {"type": "loot", "amount": 3}
    },
    "players": {
      "user_123": {
        "username": "Player1",
        "letter": "A",
        "position": [0, 0],
        "hearts": 3,
        "hearts_secret": 0,
        "action_points": 1,
        "range": 2,
        "is_downed": false,
        "can_revive": true,
        "turn_submitted": false,
        "missed_turns": 0
      }
    },
    "turn_actions": {
      "user_123": {"action": "move", "params": {"direction": "north"}}
    },
    "jury_votes": {
      "haunt": {"user_123": "user_456"},
      "intercession": {"user_123": "user_789"}
    },
    "last_ap_grant": "2026-01-20T10:00:00",
    "settings": {
      "turn_duration_hours": 24,
      "grid_shrink_enabled": true,
      "min_players": 8,
      "max_players": 16
    }
  }
}
```

**Instance Variables (volatile state):**
- Board update message ID
- Scheduled tasks for turn timer, spawns
- Image cache

---

## Implementation Plan

### Phase 1: Core Framework Setup
**Files to Create:**
- `ttt_game.py` - Main game bot class
- `ttt_models.py` - Data models (Player, GameState, Position)
- `ttt_renderer.py` - Board image generation using Pillow
- `ttt_commands.py` - Command handlers
- `ttt_mechanics.py` - Game logic (movement, combat, range checking)

**Tasks:**
1. Create `TTTGame` class extending `DispatchedBot`
2. Set up game data structure in GameData
3. Create basic slash command registration
4. Implement player registration system

### Phase 2: Grid & Visualization
**Tasks:**
1. Install Pillow: `pip install Pillow`
2. Create grid renderer that generates images:
   - 16x16 grid with borders
   - Color coding for cell types
   - Player letters/emojis on squares
   - Legend showing player names
   - Turn number, time remaining
3. Implement board update message posting/editing
4. Create `/ttt board` command to show current state

### Phase 3: Movement & Basic Actions
**Tasks:**
1. Implement position validation (bounds checking, occupied squares)
2. Create movement system:
   - Cardinal directions (N, S, E, W)
   - Validate square is unoccupied
   - Update player position
   - Check for item pickups (hearts, loot)
3. Implement `/ttt move` command
4. Implement `/ttt pass` command
5. Implement turn submission tracking

### Phase 4: Combat & Range System
**Tasks:**
1. Create range calculation function (Manhattan or Chebyshev distance)
2. Implement `/ttt attack` command:
   - Validate target in range
   - Reduce target hearts
   - Handle downing (transfer AP to attacker)
   - Update downed player status
3. Implement `/ttt upgrade_range` command
4. Implement `/ttt add_heart` command

### Phase 5: Trading & Social Actions
**Tasks:**
1. Implement `/ttt give_hearts` command:
   - Validate target in range
   - Transfer hearts
   - Handle revival of downed players
2. Implement `/ttt give_ap` command (max 3 per turn)
3. Send DM confirmations for trades

### Phase 6: Turn Management
**Tasks:**
1. Set up discord.ext.tasks for scheduled tasks
2. Create turn timer task:
   - Check if all players submitted
   - Auto-end turn after 24 hours
   - Process all submitted actions
   - Reset turn_submitted flags
   - Punish players who missed turn (lose heart)
3. Post countdown updates (6h, 3h, 1h, 30m, 5m warnings)
4. Implement turn resolution:
   - Process all actions in submission order
   - Handle conflicts (two players moving to same square)
   - Update board
   - Post new board image

### Phase 7: Daily Systems
**Tasks:**
1. Daily AP grant task:
   - Runs at random time each day
   - Grant 1 AP to all active players
   - DM each player notification
   - Skip "haunted" players (jury vote)
2. Random heart spawn task:
   - Once per day at random time
   - Spawn heart on empty square
   - Announce in channel (or keep secret?)
3. Random loot drop task:
   - Random interval (every 2-5 turns)
   - Spawn 3 AP on empty square

### Phase 8: Jury System (Downed Players)
**Tasks:**
1. Create jury voting system:
   - `/ttt vote_haunt <player>` - Vote to deny AP
   - `/ttt vote_intercession <player>` - Vote to grant 3 AP
   - Store votes secretly
   - Reset votes daily
2. Process haunt votes:
   - Count votes, player with most is haunted
   - Mark player to skip next AP grant
3. Process intercession votes:
   - Any player with 3+ votes gets 3 AP
4. Create `#ttt-graveyard` channel with restricted access:
   - Only downed players can see/write
   - Auto-add/remove players as they get downed/revived

### Phase 9: Grid Shrinking (Optional)
**Tasks:**
1. Every 3 turns, reduce grid size by 1 row and column
2. Handle players in shrink zone:
   - If downed: lose ability to revive
   - If alive: become downed, cannot revive
3. Remove items in shrink zone
4. Update board renderer for new grid size

### Phase 10: End Game
**Tasks:**
1. Detect when 4 or fewer players remain
2. Create voting system for placement agreement:
   - `/ttt agree_placement` - Vote to accept current standings
   - Requires all remaining players to agree
3. Determine final standings:
   - By hearts, then AP, then range
4. Post final results
5. Archive game to game history
6. Reset game state

### Phase 11: Admin & Debugging
**Tasks:**
1. `/ttt start` - Initialize new game:
   - Set up game state
   - Randomly place players
   - Create board message
   - Start all scheduled tasks
2. `/ttt admin_stats` - Show full game state (admin only)
3. `/ttt force_action <user> <action>` - Force player action (admin)
4. `/ttt reset` - Reset game (admin only)
5. Error handling and logging
6. Add game state validation checks

### Phase 12: Polish & Testing
**Tasks:**
1. Create comprehensive help command `/ttt help`
2. Add tutorial/onboarding for new players
3. Create test mode:
   - Shorter turn timers (5 minutes)
   - Smaller grid (8x8)
   - Fewer players needed (4 minimum)
4. Balance testing and adjustments
5. Performance optimization (caching, async operations)
6. Add game statistics tracking (kills, deaths, AP spent, etc.)

---

## Technical Considerations

### Libraries Needed
```
discord.py >= 2.0 (already installed)
Pillow >= 9.0 (for image generation)
python-dateutil (for time handling)
```

### Performance Concerns
- **Image Generation**: Cache grid images when possible, only regenerate on state changes
- **Database Writes**: GameData auto-saves after every change - consider batching for turn resolution
- **Scheduled Tasks**: Use discord.ext.tasks for reliable scheduling

### Security Considerations
- **Action Points are Secret**: Only send via DM, never in public channel
- **Prevent Cheating**: Validate all commands server-side, never trust client input
- **Rate Limiting**: Limit command usage to prevent spam (1 action per turn)

### Edge Cases to Handle
- Player leaves Discord server mid-game
- Bot restarts during active game (persist scheduled task times)
- Two players try to move to same square
- Player downed exactly when turn ends
- Grid shrinks while players are voting on placement
- Multiple players at exactly 3 jury votes for intercession

---

## File Structure
```
modbot/
├── main.py (register TTTGame)
├── ttt/
│   ├── __init__.py
│   ├── game.py          # Main TTTGame class (DispatchedBot)
│   ├── models.py        # Data classes
│   ├── renderer.py      # Image generation
│   ├── commands.py      # Command handlers
│   ├── mechanics.py     # Game logic
│   ├── jury.py          # Jury voting system
│   ├── spawns.py        # Heart/loot spawning
│   ├── scheduler.py     # Scheduled tasks manager
│   └── utils.py         # Helper functions
├── gamedata_defaults.py (add TTT defaults)
└── requirements.txt (add Pillow)
```

---

## Testing Strategy

### Unit Tests
- Movement validation
- Range calculations
- Combat mechanics
- Trading logic
- Grid shrinking
- Vote counting

### Integration Tests
- Full turn cycle
- Player interactions
- Scheduled tasks
- Database persistence

### Playtesting
1. **Test Mode Game** (4 players, 8x8 grid, 5-minute turns)
2. **Single Turn Test** (all action types)
3. **Multi-Day Test** (daily AP grants, spawns, jury votes)
4. **Endgame Test** (placement voting, grid shrinking)

---

## Estimated Complexity

**Total Implementation:**
- **Core Game**: ~800-1200 lines of code
- **Renderer**: ~200-300 lines
- **Commands**: ~400-600 lines
- **Scheduled Tasks**: ~200-300 lines
- **Testing**: ~400-600 lines

**Time Estimate** (single developer):
- Phase 1-3: 8-12 hours
- Phase 4-6: 10-15 hours
- Phase 7-9: 12-18 hours
- Phase 10-12: 8-12 hours
- **Total: 40-60 hours**

---

## Launch Checklist

- [ ] All commands tested
- [ ] Board rendering works for all grid sizes
- [ ] Turn timer tested over 24 hour period
- [ ] Daily AP grant tested
- [ ] Jury system tested
- [ ] Grid shrinking tested (if enabled)
- [ ] Endgame voting tested
- [ ] Help documentation complete
- [ ] Error handling in place
- [ ] Logging configured
- [ ] Test mode available for quick playtesting
- [ ] Admin commands secured (role-based permissions)
- [ ] Bot stays online during game (screen session + auto-restart)

---

## Future Enhancements

- [ ] Multiple concurrent games in different channels
- [ ] Spectator mode
- [ ] Game replay system
- [ ] Statistics dashboard (web interface)
- [ ] Custom game modes (different grid sizes, rule variants)
- [ ] Achievements and player profiles
- [ ] Tournament system
- [ ] Mobile-friendly web viewer for the grid
