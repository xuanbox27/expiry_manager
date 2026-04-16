const express = require('express');
const { users, items, familyMembers } = require('../utils/db');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

router.use(authenticateToken);

router.get('/members', (req, res) => {
  users.findOne({ _id: req.user.id }, (err, user) => {
    if (err) {
      console.error('Get user error:', err);
      return res.status(500).json({ error: 'Server error' });
    }

    if (!user?.family_code) {
      return res.json({ members: [], is_owner: true });
    }

    const familyCode = user.family_code;

    familyMembers.find({ family_code: familyCode }, (err, members) => {
      if (err) {
        console.error('Get family members error:', err);
        return res.status(500).json({ error: 'Failed to get family members' });
      }

      const enrichedMembers = members.map(m => {
        const u = users.findOne({ _id: m.user_id });
        return {
          id: u?._id,
          nickname: u?.nickname,
          email: u?.email,
          role: m.role,
          joined_at: m.joined_at
        };
      });

      familyMembers.findOne({ family_code: familyCode, role: 'owner' }, (err, ownerMember) => {
        if (err) {
          console.error('Get owner error:', err);
          return res.status(500).json({ error: 'Server error' });
        }

        let owner = null;
        if (ownerMember) {
          owner = users.findOne({ _id: ownerMember.user_id });
          owner = { id: owner?._id, nickname: owner?.nickname, email: owner?.email };
        }

        res.json({
          members: enrichedMembers,
          owner,
          is_owner: ownerMember?.user_id === req.user.id,
          family_code: familyCode
        });
      });
    });
  });
});

router.post('/join', (req, res) => {
  const { family_code } = req.body;

  if (!family_code) {
    return res.status(400).json({ error: 'Family code is required' });
  }

  users.findOne({ family_code: family_code.toUpperCase() }, (err, owner) => {
    if (err) {
      console.error('Find owner error:', err);
      return res.status(500).json({ error: 'Server error' });
    }

    if (!owner) {
      return res.status(404).json({ error: 'Family not found' });
    }

    if (owner._id === req.user.id) {
      return res.status(400).json({ error: 'You cannot join your own family' });
    }

    users.findOne({ _id: req.user.id }, (err, user) => {
      if (err) {
        console.error('Find user error:', err);
        return res.status(500).json({ error: 'Server error' });
      }

      if (user?.family_code) {
        return res.status(400).json({ error: 'You are already in a family' });
      }

      familyMembers.insert({
        family_code: family_code.toUpperCase(),
        user_id: req.user.id,
        role: 'member',
        joined_at: new Date().toISOString()
      }, (err) => {
        if (err) {
          console.error('Join family error:', err);
          return res.status(500).json({ error: 'Failed to join family' });
        }

        users.update({ _id: req.user.id }, { $set: { family_code: family_code.toUpperCase() } }, {}, (err) => {
          if (err) {
            console.error('Update user error:', err);
            return res.status(500).json({ error: 'Failed to update user' });
          }
          res.json({ message: 'Successfully joined family', family_code: family_code.toUpperCase() });
        });
      });
    });
  });
});

router.get('/items', (req, res) => {
  users.findOne({ _id: req.user.id }, (err, user) => {
    if (err) {
      console.error('Get user error:', err);
      return res.status(500).json({ error: 'Server error' });
    }

    if (!user?.family_code) {
      return res.json({ items: [] });
    }

    familyMembers.find({ family_code: user.family_code }, (err, members) => {
      if (err) {
        console.error('Get family members error:', err);
        return res.status(500).json({ error: 'Failed to get family members' });
      }

      const userIds = members.map(m => m.user_id);

      items.find({ user_id: { $in: userIds } }, (err, itemsList) => {
        if (err) {
          console.error('Get items error:', err);
          return res.status(500).json({ error: 'Failed to get items' });
        }

        const enrichedItems = itemsList.map(item => {
          const owner = users.findOne({ _id: item.user_id });
          return { ...item, id: item._id, owner_name: owner?.nickname };
        });

        res.json({ items: enrichedItems });
      });
    });
  });
});

router.post('/leave', (req, res) => {
  familyMembers.findOne({ user_id: req.user.id }, (err, member) => {
    if (err) {
      console.error('Get member error:', err);
      return res.status(500).json({ error: 'Server error' });
    }

    if (member?.role === 'owner') {
      return res.status(400).json({ error: 'Owner cannot leave. Please delete the family instead.' });
    }

    familyMembers.remove({ user_id: req.user.id }, { multi: false }, (err) => {
      if (err) {
        console.error('Remove member error:', err);
        return res.status(500).json({ error: 'Server error' });
      }

      users.update({ _id: req.user.id }, { $set: { family_code: null } }, {}, (err) => {
        if (err) {
          console.error('Update user error:', err);
          return res.status(500).json({ error: 'Failed to leave family' });
        }
        res.json({ message: 'Successfully left family' });
      });
    });
  });
});

router.post('/invite', (req, res) => {
  users.findOne({ _id: req.user.id }, (err, user) => {
    if (err) {
      console.error('Get user error:', err);
      return res.status(500).json({ error: 'Server error' });
    }

    const familyCode = user?.family_code;

    if (!familyCode) {
      return res.status(400).json({ error: 'You are not in a family' });
    }

    res.json({ 
      family_code: familyCode,
      invite_message: `邀请你加入保质期管家家庭，家族码：${familyCode}`
    });
  });
});

module.exports = router;
