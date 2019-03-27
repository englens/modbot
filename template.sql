create table users (
    u_key INTEGER PRIMARY KEY
    discord_id TEXT,
);

create table meme_points (
    user_key INTEGER,
    upvotes INTEGER,
    downvotes INTEGER,
    general_participation INTEGER,
    voting_participation INTEGER,
    FOREIGN KEY(user_key) REFERENCES users(u_key)
);

SELECT ? FROM meme_points WHERE user_key=?;
