const cron = require('node-cron');
const { users, items, notifications } = require('../utils/db');
const { sendExpiryReminder } = require('../services/email');

function checkExpiringItems() {
  console.log('Running reminder check...');
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const twoDaysLater = new Date(today);
  twoDaysLater.setDate(today.getDate() + 2);
  
  const formatDate = (d) => d.toISOString().split('T')[0];
  
  items.find({ 
    status: 'active',
    expiry_date: { $gte: formatDate(today), $lte: formatDate(twoDaysLater) }
  }, (err, allItems) => {
    if (err) {
      console.error('Find items error:', err);
      return;
    }

    const userMap = new Map();
    for (const item of allItems) {
      if (!userMap.has(item.user_id)) {
        userMap.set(item.user_id, []);
      }
      userMap.get(item.user_id).push(item);
    }

    let processed = 0;
    for (const [userId, itemList] of userMap) {
      users.findOne({ _id: userId }, (err, user) => {
        if (err) {
          console.error('Find user error:', err);
          processed++;
          return;
        }

        if (user?.email_notifications && itemList.length > 0) {
          sendExpiryReminder(user.email, itemList);
        }
        
        for (const item of itemList) {
          notifications.insert({
            user_id: userId,
            title: '物品即将过期',
            message: `您的物品 "${item.name}" 即将在48小时内过期，请尽快使用！`,
            type: 'expiry_warning',
            is_read: false,
            created_at: new Date().toISOString()
          });
        }

        processed++;
        if (processed === userMap.size) {
          console.log(`Checked ${userMap.size} users for expiring items`);
        }
      });
    }

    if (userMap.size === 0) {
      console.log('No expiring items found');
    }
  });
}

function startReminderJob() {
  cron.schedule('0 9 * * *', checkExpiringItems);
  console.log('Reminder job scheduled to run daily at 9 AM');
}

module.exports = { startReminderJob, checkExpiringItems };
