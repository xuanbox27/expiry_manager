const Datastore = require('@seald-io/nedb');
const path = require('path');
const fs = require('fs');

const dataDir = path.join(__dirname, '../../data');
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });

const users = new Datastore({ filename: path.join(dataDir, 'users.db'), autoload: true });
const items = new Datastore({ filename: path.join(dataDir, 'items.db'), autoload: true });
const familyMembers = new Datastore({ filename: path.join(dataDir, 'familyMembers.db'), autoload: true });
const notifications = new Datastore({ filename: path.join(dataDir, 'notifications.db'), autoload: true });
const reminderSettings = new Datastore({ filename: path.join(dataDir, 'reminderSettings.db'), autoload: true });

users.ensureIndex({ fieldName: 'email', unique: true });
items.ensureIndex({ fieldName: 'user_id' });
items.ensureIndex({ fieldName: 'expiry_date' });
familyMembers.ensureIndex({ fieldName: 'family_code' });
familyMembers.ensureIndex({ fieldName: 'user_id' });
notifications.ensureIndex({ fieldName: 'user_id' });

module.exports = { users, items, familyMembers, notifications, reminderSettings };
