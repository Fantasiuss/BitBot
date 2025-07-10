import React, { useEffect, useState } from 'react';

function Dashboard() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch('http://localhost:3001/auth/me', { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        if (!data.error) setUser(data);
      });
  }, []);

  if (!user) return <a href="http://localhost:3001/auth/login">Login with Discord</a>;

  return (
    <div>
      <h1>Welcome, {user.username}#{user.discriminator}</h1>
      <h2>Your Servers</h2>
      <ul>
        {user.guilds.map(guild => (
          <li key={guild.id}>
            <a href={`/guild/${guild.id}`}>
              {guild.icon ? (
                <img
                  src={`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`}
                  alt="icon"
                  width={32}
                  height={32}
                  style={{ borderRadius: '50%', verticalAlign: 'middle', marginRight: '10px' }}
                />
              ) : (
                <span style={{ display: 'inline-block', width: 32, height: 32, marginRight: 10 }} />
              )}
              {guild.name}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Dashboard;
