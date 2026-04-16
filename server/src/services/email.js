const sgMail = require('@sendgrid/mail');

let apiKey = process.env.SENDGRID_API_KEY;
if (apiKey && apiKey !== 'SG.your-sendgrid-api-key') {
  sgMail.setApiKey(apiKey);
}

async function sendExpiryReminder(email, items) {
  if (!apiKey || apiKey === 'SG.your-sendgrid-api-key') {
    console.log(`[Mock Email] Would send reminder to ${email} for ${items.length} items`);
    return { success: true, mock: true };
  }

  const itemList = items.map(item => `- ${item.name}: ${item.expiry_date}`).join('\n');

  const msg = {
    to: email,
    from: 'noreply@expiry-manager.com',
    subject: '【保质期管家】您有物品即将过期',
    text: `您好！\n\n以下物品即将在48小时内过期：\n\n${itemList}\n\n请尽快使用或处理。\n\n—— 保质期管家`,
    html: `
      <h2>保质期管家提醒</h2>
      <p>您好！以下物品即将在48小时内过期：</p>
      <ul>
        ${items.map(item => `<li><strong>${item.name}</strong> - 到期日期: ${item.expiry_date}</li>`).join('')}
      </ul>
      <p>请尽快使用或处理。</p>
      <hr>
      <p>—— 保质期管家</p>
    `,
  };

  try {
    await sgMail.send(msg);
    console.log(`Email sent to ${email}`);
    return { success: true };
  } catch (error) {
    console.error('SendGrid error:', error);
    return { success: false, error: error.message };
  }
}

module.exports = { sendExpiryReminder };
