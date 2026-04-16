const express = require('express');
const bcrypt = require('bcrypt');
const crypto = require('crypto');
const { users } = require('../utils/db');
const { generateToken, authenticateToken } = require('../middleware/auth');

const router = express.Router();

router.post('/register', (req, res) => {
  const { email, password, nickname } = req.body;

  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' });
  }

  users.findOne({ email }, (err, existingUser) => {
    if (err) {
      console.error('Find user error:', err);
      return res.status(500).json({ error: 'Server error' });
    }

    if (existingUser) {
      if (process.env.NODE_ENV === 'development') {
        users.remove({ _id: existingUser._id }, {}, (err) => {
          if (err) console.error('Failed to remove existing user:', err);
        });
      } else {
        return res.status(409).json({ error: 'Email already registered' });
      }
    }

    bcrypt.hash(password, 10).then((passwordHash) => {
      const familyCode = crypto.randomBytes(4).toString('hex').toUpperCase();

      const doc = {
        email,
        password_hash: passwordHash,
        nickname: nickname || email.split('@')[0],
        family_code: familyCode,
        email_notifications: true,
        created_at: new Date().toISOString()
      };

      users.insert(doc, (err, newDoc) => {
        if (err) {
          console.error('Register error:', err);
          return res.status(500).json({ error: 'Registration failed' });
        }

        const user = {
          id: newDoc._id,
          email: newDoc.email,
          nickname: newDoc.nickname,
          family_code: newDoc.family_code,
          created_at: newDoc.created_at
        };

        const token = generateToken({ id: newDoc._id });
        res.status(201).json({ user, token });
      });
    });
  });
});

router.post('/login', (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' });
  }

  users.findOne({ email }, (err, user) => {
    if (err) {
      console.error('Find user error:', err);
      return res.status(500).json({ error: 'Server error' });
    }

    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    bcrypt.compare(password, user.password_hash).then((validPassword) => {
      if (!validPassword) {
        return res.status(401).json({ error: 'Invalid credentials' });
      }

      const token = generateToken({ id: user._id });
      res.json({
        user: {
          id: user._id,
          email: user.email,
          nickname: user.nickname,
          family_code: user.family_code,
          email_notifications: user.email_notifications
        },
        token
      });
    });
  });
});

router.get('/me', authenticateToken, (req, res) => {
  users.findOne({ _id: req.user.id }, (err, user) => {
    if (err) {
      console.error('Get user error:', err);
      return res.status(500).json({ error: 'Server error' });
    }

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({
      id: user._id,
      email: user.email,
      nickname: user.nickname,
      family_code: user.family_code,
      email_notifications: user.email_notifications,
      created_at: user.created_at
    });
  });
});

router.put('/settings', authenticateToken, (req, res) => {
  const { email_notifications, nickname } = req.body;

  const updates = {};
  if (email_notifications !== undefined) updates.email_notifications = email_notifications;
  if (nickname !== undefined) updates.nickname = nickname;

  if (Object.keys(updates).length === 0) {
    return res.status(400).json({ error: 'No fields to update' });
  }

  users.update({ _id: req.user.id }, { $set: updates }, {}, (err) => {
    if (err) {
      console.error('Update settings error:', err);
      return res.status(500).json({ error: 'Failed to update settings' });
    }

    users.findOne({ _id: req.user.id }, (err, user) => {
      if (err) {
        console.error('Get user error:', err);
        return res.status(500).json({ error: 'Server error' });
      }

      res.json({
        id: user._id,
        email: user.email,
        nickname: user.nickname,
        family_code: user.family_code,
        email_notifications: user.email_notifications
      });
    });
  });
});

module.exports = router;
