# TTT Implementation Roadmap

## Quick Start Implementation Order

This is the recommended order to build the game incrementally, with working milestones at each step.

---

## Milestone 1: "Hello Grid" (2-3 hours)
**Goal:** Display a basic grid with players on it

### Tasks:
1. Install Pillow: `pip install Pillow`
2. Create `ttt/` directory structure
3. Create `ttt/renderer.py`:
   - Function to generate 16x16 grid PNG
   - Draw colored squares
   - Add player letters (A-P)
   - Add simple legend
4. Create `ttt/game.py`:
   - Basic `TTTGame(DispatchedBot)` class
   - Command: `/ttt test_board` - generates and posts a test image
5. Register in `main.py`

**Deliverable:** Bot can post a pretty grid image to Discord

---

## Milestone 2: "I Can Move" (3-4 hours)
**Goal:** Players can join and move around the grid

### Tasks:
1. Create `ttt/models.py`:
   - `Player` class (position, hearts, AP, range, etc.)
   - `Position` class (x, y with validation)
   - `GameState` class (players dict, board dict, turn info)
2. Add game state to GameData defaults
3. Implement commands:
   - `/ttt join` - Add player to game
   - `/ttt move <direction>` - Move north/south/east/west
   - `/ttt board` - Show current grid
4. Create `ttt/mechanics.py`:
   - `validate_movement()` - Check if move is legal
   - `update_position()` - Move player on grid
5. Update renderer to show actual game state

**Deliverable:** Players can join and move around, see their position update

---

## Milestone 3: "Turn System" (4-5 hours)
**Goal:** Proper turn-based gameplay with time limits

### Tasks:
1. Add turn tracking to GameState:
   - Turn number
   - Who has submitted
   - Turn start time
2. Implement commands:
   - `/ttt start` - Start game with registered players
   - `/ttt pass` - Submit turn without action
   - `/ttt status` - DM player their stats
3. Create `ttt/scheduler.py`:
   - Turn timer (use discord.ext.tasks)
   - Process turn end (execute all moves)
   - Reset for next turn
4. Add turn countdown posts
5. Implement "missed turn" penalty (lose 1 heart)

**Deliverable:** Full turn cycle works, players must submit actions before timer

---

## Milestone 4: "Combat & Actions" (4-5 hours)
**Goal:** All player actions work

### Tasks:
1. Create `ttt/mechanics.py` functions:
   - `calculate_range()` - Who can player interact with?
   - `attack_player()` - Deal damage, handle downing
   - `upgrade_range()` - Spend AP, increase range
   - `add_heart()` - Spend AP, gain heart
2. Implement commands:
   - `/ttt attack <player>`
   - `/ttt upgrade_range`
   - `/ttt add_heart`
3. Handle downing:
   - Transfer AP to attacker
   - Mark player as downed
   - Update board renderer (different color for downed)

**Deliverable:** Players can attack each other and use all actions

---

## Milestone 5: "Trading & Social" (3-4 hours)
**Goal:** Players can give hearts/AP to allies

### Tasks:
1. Implement:
   - `give_hearts()` in mechanics
   - `give_ap()` in mechanics
2. Implement commands:
   - `/ttt give_hearts <player> <amount>`
   - `/ttt give_ap <player> <amount>`
3. Handle revival:
   - Giving heart to downed player revives them
   - Set to 1 heart, 1 AP
4. Send DM notifications for trades

**Deliverable:** Players can form alliances through trading

---

## Milestone 6: "Daily AP & Spawns" (5-6 hours)
**Goal:** Daily AP grants and random item spawns

### Tasks:
1. Create scheduled tasks:
   - Daily AP grant (random time, once per day)
   - Heart spawn (once per day, random time)
   - Loot drop (random, every 2-5 turns)
2. Implement pickup system:
   - When player moves onto heart: gain 1 heart
   - When player moves onto loot: gain AP
3. Update renderer to show items on grid
4. Track last AP grant time to prevent duplicates

**Deliverable:** Game has daily progression and random events

---

## Milestone 7: "Jury System" (5-6 hours)
**Goal:** Downed players can vote

### Tasks:
1. Create `ttt/jury.py`:
   - Haunt vote tracking
   - Intercession vote tracking
   - Vote counting and processing
2. Set up `#ttt-graveyard` channel:
   - Auto-add downed players
   - Auto-remove revived players
3. Implement commands:
   - `/ttt vote_haunt <player>`
   - `/ttt vote_intercession <player>`
4. Process votes daily:
   - Haunt: Most votes = skip AP grant
   - Intercession: 3+ votes = grant 3 AP
5. DM vote confirmations (secret)

**Deliverable:** Downed players have influence through voting

---

## Milestone 8: "Grid Shrinking" (3-4 hours) *OPTIONAL*
**Goal:** Grid shrinks every 3 turns

### Tasks:
1. Track grid size in GameState
2. Every 3 turns:
   - Reduce grid_size by 1
   - Check all positions
   - Down players in shrink zone
   - Remove downed players' revive ability
   - Remove items in shrink zone
3. Update renderer for dynamic grid size
4. Add visual indicator of "danger zone"

**Deliverable:** Grid creates pressure to engage

---

## Milestone 9: "Endgame" (4-5 hours)
**Goal:** Game ends with placement voting

### Tasks:
1. Detect 4 or fewer players alive
2. Calculate current standings:
   - Sort by: hearts > AP > range > kills
3. Create voting system:
   - `/ttt agree_placement` - Vote to accept
   - Show current standings
   - Require unanimous agreement
4. If disagreement, continue playing
5. Post final results:
   - 1st, 2nd, 3rd place
   - Game statistics
   - MVP awards?
6. Archive game to history

**Deliverable:** Game has proper conclusion

---

## Milestone 10: "Polish" (6-8 hours)
**Goal:** Ready for real players

### Tasks:
1. Create `/ttt help` with full rules
2. Add player onboarding tutorial
3. Create test mode:
   - `/ttt testgame` - 8x8 grid, 5-min turns, 4 players
4. Admin commands:
   - `/ttt admin_status` - Full game state
   - `/ttt force_end_turn` - Skip to turn end
   - `/ttt reset` - Clear game
5. Error handling everywhere
6. Logging system
7. Input validation
8. Rate limiting
9. Game stats tracking:
   - Kills, deaths, damage dealt, AP spent, hearts given
10. Pretty embeds for all messages

**Deliverable:** Production-ready game

---

## Development Tips

### Testing Without 16 Players
1. Use test mode (4 players minimum)
2. Create multiple Discord test accounts
3. Implement `/ttt bot_player` to add AI players for testing
4. Use `/ttt simulate_turn` admin command to auto-complete turns

### Debugging
1. Add verbose logging mode
2. Create `/ttt debug_state` to dump full game state
3. Use test channel separate from production
4. Keep game state in JSON (easy to inspect/edit manually)

### Performance
1. Cache grid images (only regenerate on state change)
2. Batch database writes during turn resolution
3. Use async for all Discord API calls
4. Limit board updates (not every command, only on turn end)

---

## Quick Implementation Commands

```bash
# Create directory structure
mkdir -p ttt
touch ttt/__init__.py
touch ttt/game.py
touch ttt/models.py
touch ttt/renderer.py
touch ttt/mechanics.py
touch ttt/commands.py
touch ttt/jury.py
touch ttt/spawns.py
touch ttt/scheduler.py
touch ttt/utils.py

# Install dependencies
pip install Pillow

# Add to main.py (at the end, before bot.start()):
# from ttt.game import TTTGame
# bots.append(TTTGame())
```

---

## When Each Feature is Needed

### Must Have (MVP):
- ✅ Grid display
- ✅ Movement
- ✅ Turn system
- ✅ Combat
- ✅ Basic actions (add heart, upgrade range)
- ✅ Daily AP grants
- ✅ Endgame detection

### Should Have (Launch):
- ✅ Trading (give hearts/AP)
- ✅ Random spawns (hearts, loot)
- ✅ Jury system
- ✅ Help documentation
- ✅ Test mode

### Nice to Have (Post-Launch):
- Grid shrinking
- Statistics tracking
- Game history/replays
- Achievements
- Multiple games at once
- Web dashboard

---

## Estimated Timeline

**Working 2-3 hours per day:**
- Week 1: Milestones 1-3 (Grid, movement, turns)
- Week 2: Milestones 4-6 (Combat, trading, daily systems)
- Week 3: Milestones 7-9 (Jury, shrinking, endgame)
- Week 4: Milestone 10 (Polish + testing)

**Full-time work (6-8 hours per day):**
- Days 1-2: Milestones 1-3
- Days 3-4: Milestones 4-6
- Days 5-6: Milestones 7-9
- Days 7-8: Milestone 10

**Total:** ~40-50 hours of development

---

## Risk Areas

### High Risk (Complex):
- Turn synchronization (what if bot restarts mid-turn?)
- Scheduled tasks (daily AP grants must work reliably)
- Jury voting (votes must stay secret)
- Grid shrinking edge cases

### Medium Risk:
- Image generation performance
- DM delivery failures
- Combat edge cases (simultaneous attacks)
- Database corruption from crashes

### Low Risk:
- Movement validation
- Range calculation
- Command parsing
- Basic rendering

---

## Launch Checklist

### Before First Playtest:
- [ ] Create test Discord server
- [ ] Set up test mode (5-min turns)
- [ ] Recruit 4 test players
- [ ] Document known bugs
- [ ] Have admin commands ready for intervention

### Before Production Launch:
- [ ] 24-hour turn timer tested
- [ ] Daily AP grant tested
- [ ] Bot auto-restart working
- [ ] Backup/restore game state tested
- [ ] Player documentation written
- [ ] At least one full test game completed
- [ ] Admin team trained on commands

### Post-Launch Monitoring:
- [ ] Check logs daily for errors
- [ ] Monitor turn timer accuracy
- [ ] Watch for cheating/exploits
- [ ] Gather player feedback
- [ ] Track game balance (is anyone too powerful?)
