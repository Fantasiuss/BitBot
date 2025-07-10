const express = require('express');
const passport = require('passport');
const DiscordStrategy = require('passport-discord').Strategy;

const router = express.Router();

const scopes = ['identify', 'guilds'];

passport.serializeUser((user, done) => {
  done(null, user);
});

passport.deserializeUser((obj, done) => {
  done(null, obj);
});

passport.use(new DiscordStrategy(
  {
    clientID: process.env.CLIENT_ID,
    clientSecret: process.env.CLIENT_SECRET,
    callbackURL: process.env.CALLBACK_URL,
    scope: scopes,
  },
  (accessToken, refreshToken, profile, done) => {
    // You could save profile or tokens here
    process.nextTick(() => done(null, profile));
  }
));

router.get('/login', passport.authenticate('discord'));
router.get(
  '/callback',
  passport.authenticate('discord', { failureRedirect: '/' }),
  (req, res) => {
    res.redirect('http://localhost:3000'); // React frontend
  }
);

router.get('/logout', (req, res) => {
  req.logout(err => {
    res.redirect('http://localhost:3000');
  });
});

router.get('/me', (req, res) => {
  if (!req.user) return res.status(401).json({ error: 'Unauthorized' });

  // Filter only guilds where the user can manage the server
  const manageableGuilds = req.user.guilds.filter(guild =>
    (guild.permissions & 0x20) === 0x20 // 0x20 = MANAGE_GUILD
  );

  res.json({
    id: req.user.id,
    username: req.user.username,
    discriminator: req.user.discriminator,
    avatar: req.user.avatar,
    guilds: manageableGuilds,
  });
});


module.exports = router;
