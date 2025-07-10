const express = require('express');
const session = require('express-session');
const passport = require('passport');
const cors = require('cors');
require('dotenv').config();

const authRoutes = require('./auth');

const app = express();
const PORT = process.env.PORT || 3001;

BOT_TOKEN = process.env.BOT_TOKEN;

app.use(cors({ origin: 'http://localhost:3000', credentials: true }));
app.use(express.json());

app.use(
  session({
    secret: 'some random secret',
    resave: false,
    saveUninitialized: false,
  })
);
app.use(passport.initialize());
app.use(passport.session());

app.use('/auth', authRoutes);

app.get('/api/test', (req, res) => {
  res.json({ message: 'API is working!' });
});

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});

const { getGuildSettings, saveGuildSettings } = require('./db');

app.get('/api/guilds/:id/settings', (req, res) => {
  if (!req.user) return res.status(401).json({ error: 'Unauthorized' });
  const guildId = req.params.id;
  const userGuild = req.user.guilds.find(g => g.id === guildId);
  if (!userGuild || (userGuild.permissions & 0x20) !== 0x20) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  getGuildSettings(guildId, (err, settings) => {
    if (err) return res.status(500).json({ error: 'DB error' });
    res.json(settings);
  });
});

app.post('/api/guilds/:id/settings', (req, res) => {
  if (!req.user) return res.status(401).json({ error: 'Unauthorized' });
  const guildId = req.params.id;
  const userGuild = req.user.guilds.find(g => g.id === guildId);
  if (!userGuild || (userGuild.permissions & 0x20) !== 0x20) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  saveGuildSettings(guildId, req.body, (err) => {
    if (err) return res.status(500).json({ error: 'Save failed' });
    res.json({ success: true });
  });
});

// In server/index.js (or routes file)
const { db } = require('./db'); // Your sqlite3 db instance or helper

app.get('/api/guilds/:id/bot-in-guild', (req, res) => {
  if (!req.user) return res.status(401).json({ error: 'Unauthorized' });

  const guildId = req.params.id;
  // Check if user manages this guild
  const userGuild = req.user.guilds.find(g => g.id === guildId);
  if (!userGuild || (userGuild.permissions & 0x20) !== 0x20) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  // Check if bot is in the guild by querying your guilds table
  db.get('SELECT guild_id FROM guilds WHERE guild_id = ?', [guildId], (err, row) => {
    if (err) return res.status(500).json({ error: 'DB error' });
    res.json({ botInGuild: !!row });
  });
});

const axios = require('axios');

app.get('/api/guilds/:id/roles', async (req, res) => {
  if (!req.user) return res.status(401).json({ error: 'Unauthorized' });

  const guildId = req.params.id;
  const userGuild = req.user.guilds.find(g => g.id === guildId);
  if (!userGuild || (userGuild.permissions & 0x20) !== 0x20) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  try {
    const response = await axios.get(`https://discord.com/api/v10/guilds/${guildId}/roles`, {
      headers: {
        Authorization: `Bot ${BOT_TOKEN}`
      }
    });

    const roles = response.data
      .filter(r => r.name !== '@everyone')
      .map(r => ({ id: r.id, name: r.name }));

    res.json(roles);
  } catch (err) {
    console.error(err.response?.data || err.message);
    res.status(500).json({ error: 'Failed to fetch roles' });
  }
});
