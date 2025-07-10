const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const db = new sqlite3.Database(path.join(__dirname, '../database/data.db'));

db.serialize(() => {

    db.run("PRAGMA foreign_keys = ON");
    
    db.run("CREATE TABLE IF NOT EXISTS guilds (guild_id INTEGER PRIMARY KEY)");
    
    db.run(`
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL UNIQUE,
        
        region INTEGER NOT NULL,
        empire TEXT DEFAULT 'None',
        claim TEXT DEFAULT 'None',
        
        carpentry INTEGER DEFAULT 1,
        mining INTEGER DEFAULT 1,
        fishing INTEGER DEFAULT 1,
        farming INTEGER DEFAULT 1,
        foraging INTEGER DEFAULT 1,
        forestry INTEGER DEFAULT 1,
        scholar INTEGER DEFAULT 1,
        masonry INTEGER DEFAULT 1,
        smithing INTEGER DEFAULT 1,
        tailoring INTEGER DEFAULT 1,
        hunting INTEGER DEFAULT 1,
        leatherworking INTEGER DEFAULT 1,
        
        construction INTEGER DEFAULT 1,
        cooking INTEGER DEFAULT 1,
        merchanting INTEGER DEFAULT 1,
        sailing INTEGER DEFAULT 1,
        slayer INTEGER DEFAULT 1,
        taming INTEGER DEFAULT 1,
        
        PRIMARY KEY (user_id)
    )`);
    
    db.run(`
        CREATE TABLE IF NOT EXISTS guild_settings (
        guild_id TEXT PRIMARY KEY,
        verification_enabled BOOLEAN DEFAULT FALSE,
        verification_type TEXT DEFAULT 'verified',
        verification_role INTEGER

        guild_empire TEXT DEFAULT 'None',
        guild_claim TEXT DEFAULT 'None'
    )`);
    
    db.run(`CREATE TABLE IF NOT EXISTS groups (
        group_type TEXT NOT NULL, 
        owner_id INTEGER NOT NULL,
        name TEXT PRIMARY KEY,
        description TEXT,
        discord_id INTEGER,
        discord_link TEXT,
        region INTEGER NOT NULL,
        empire TEXT DEFAULT 'None',
        
        FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE
    )`);
});

function getGuildSettings(guildId, callback) {
  db.get(`SELECT * FROM guild_settings WHERE guild_id = ?`, [guildId], (err, row) => {
    if (err) return callback(err);
    if (!row) {
      const defaults = {
        verification_enabled: 0,
        verification_type: 'verified',
        verification_role: null,
        empire: 'None',
        claim: 'None'
      };
      db.run(`INSERT INTO guild_settings (guild_id) VALUES (?)`, [guildId]);
      return callback(null, defaults);
    }
    callback(null, {
      verification_enabled: row.verification_enabled,
      verification_type: row.verification_type,
      verification_role: row.verification_role,
      empire: row.empire || 'None',
      claim: row.claim || 'None'
    });
  });
}

function saveGuildSettings(guildId, settings, callback) {
  const {
    verification_enabled,
    verification_type,
    verification_role,
    empire = 'None',
    claim = 'None'
  } = settings;

  db.run(`
    INSERT INTO guild_settings (
      guild_id, verification_enabled, verification_type, verification_role, empire, claim
    ) VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(guild_id) DO UPDATE SET
      verification_enabled = excluded.verification_enabled,
      verification_type = excluded.verification_type,
      verification_role = excluded.verification_role,
      empire = excluded.empire,
      claim = excluded.claim
  `, [guildId, verification_enabled, verification_type, verification_role, empire, claim], callback);
}

module.exports = { db, getGuildSettings, saveGuildSettings };
