const express = require('express');
const { notifications } = require('../utils/db');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

router.use(authenticateToken);

router.get('/', (req, res) => {
  const { unread_only } = req.query;

  let query = { user_id: req.user.id };
  if (unread_only === 'true') {
    query.is_read = false;
  }

  notifications.find(query).exec((err, docs) => {
    if (err) {
      console.error('Get notifications error:', err);
      return res.status(500).json({ error: 'Failed to get notifications' });
    }

    const result = docs || [];

    result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    const limited = result.slice(0, 50);

    const enriched = limited.map(n => ({ ...n, id: n._id }));

    res.json(enriched);
  });
});

router.put('/:id/read', (req, res) => {
  const { id } = req.params;

  notifications.findOne({ _id: id, user_id: req.user.id }, (err, notification) => {
    if (err) {
      console.error('Get notification error:', err);
      return res.status(500).json({ error: 'Failed to get notification' });
    }
    if (!notification) {
      return res.status(404).json({ error: 'Notification not found' });
    }

    notifications.update({ _id: id }, { $set: { is_read: true } }, {}, (err) => {
      if (err) {
        console.error('Mark notification read error:', err);
        return res.status(500).json({ error: 'Failed to mark notification as read' });
      }

      notifications.findOne({ _id: id }, (err, updated) => {
        if (err) {
          console.error('Get updated notification error:', err);
          return res.status(500).json({ error: 'Failed to get updated notification' });
        }
        res.json({ ...updated, id: updated._id });
      });
    });
  });
});

router.put('/read-all', (req, res) => {
  notifications.update(
    { user_id: req.user.id, is_read: false },
    { $set: { is_read: true } },
    { multi: true },
    (err) => {
      if (err) {
        console.error('Mark all notifications read error:', err);
        return res.status(500).json({ error: 'Failed to mark all notifications as read' });
      }
      res.json({ message: 'All notifications marked as read' });
    }
  );
});

router.delete('/:id', (req, res) => {
  const { id } = req.params;

  notifications.findOne({ _id: id, user_id: req.user.id }, (err, notification) => {
    if (err) {
      console.error('Get notification error:', err);
      return res.status(500).json({ error: 'Failed to get notification' });
    }
    if (!notification) {
      return res.status(404).json({ error: 'Notification not found' });
    }

    notifications.remove({ _id: id }, {}, (err) => {
      if (err) {
        console.error('Delete notification error:', err);
        return res.status(500).json({ error: 'Failed to delete notification' });
      }
      res.json({ message: 'Notification deleted' });
    });
  });
});

module.exports = router;
