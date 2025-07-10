import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const verificationTypes = ['verified', 'claim', 'empire'];

export default function GuildSettings() {
  const { id } = useParams();
  const [settings, setSettings] = useState({});
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [botInGuild, setBotInGuild] = useState(null);

  useEffect(() => {
    axios.get(`http://localhost:3001/api/guilds/${id}/bot-in-guild`, { withCredentials: true })
      .then(res => {
        setBotInGuild(res.data.botInGuild);
        if (res.data.botInGuild) {
          return Promise.all([
            axios.get(`http://localhost:3001/api/guilds/${id}/settings`, { withCredentials: true }),
            axios.get(`http://localhost:3001/api/guilds/${id}/roles`, { withCredentials: true })
          ]);
        }
        return [null, null];
      })
      .then(([settingsRes, rolesRes]) => {
        if (settingsRes) setSettings(settingsRes.data);
        if (rolesRes) setRoles(rolesRes.data);
      })
      .finally(() => setLoading(false));
  }, [id]);

  const saveSettings = () => {
    axios.post(`http://localhost:3001/api/guilds/${id}/settings`, settings, { withCredentials: true })
      .then(() => alert('Settings saved!'))
      .catch(() => alert('Failed to save'));
  };

  if (loading) return <div>Loading...</div>;

  if (!botInGuild) {
    return (
      <div>
        <h2>The bot is not in this server.</h2>
        <a href={`https://discord.com/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&scope=bot&permissions=8&guild_id=${id}`}>
          Invite the bot
        </a>
      </div>
    );
  }

  return (
    <div>
      <h2>Verification Module Settings</h2>

      <label>
        <input
          type="checkbox"
          checked={!!settings.verification_enabled}
          onChange={() =>
            setSettings(prev => ({
              ...prev,
              verification_enabled: prev.verification_enabled ? 0 : 1
            }))
          }
        />
        Enable Verification
      </label>

      <div>
        <label>Verification Type:</label>
        <select
          value={settings.verification_type}
          onChange={e =>
            setSettings(prev => ({ ...prev, verification_type: e.target.value }))
          }
        >
          {verificationTypes.map(type => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label>Verified Role:</label>
        <select
          value={settings.verification_role || ''}
          onChange={e =>
            setSettings(prev => ({ ...prev, verification_role: e.target.value }))
          }
        >
          <option value="">None</option>
          {roles.map(role => (
            <option key={role.id} value={role.id}>
              {role.name}
            </option>
          ))}
        </select>
      </div>

      <h2>Server Metadata</h2>

      <div>
        <label>Empire:</label>
        <input
          type="text"
          value={settings.empire || 'None'}
          onChange={e =>
            setSettings(prev => ({ ...prev, empire: e.target.value }))
          }
        />
      </div>

      <div>
        <label>Claim:</label>
        <input
          type="text"
          value={settings.claim || 'None'}
          onChange={e =>
            setSettings(prev => ({ ...prev, claim: e.target.value }))
          }
        />
      </div>

      <br />
      <button onClick={saveSettings}>Save</button>
    </div>
  );
}
