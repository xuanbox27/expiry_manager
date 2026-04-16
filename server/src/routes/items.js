const express = require('express');
const { users, items } = require('../utils/db');
const { authenticateToken } = require('../middleware/auth');
const { lookupBarcode, getAllProducts, getCategories } = require('../services/barcode');

const router = express.Router();

router.use(authenticateToken);

router.get('/', (req, res) => {
  const { status, category } = req.query;

  const user = users.findOne({ _id: req.user.id });

  let query = { user_id: req.user.id };

  if (user?.family_code) {
    const familyUsers = users.find({ family_code: user.family_code });
    const userIds = familyUsers.map(u => u._id);
    query.user_id = { $in: userIds };
  }

  if (status) query.status = status;
  if (category) query.category = category;

  items.find(query).exec((err, docs) => {
    if (err) {
      console.error('Get items error:', err);
      return res.status(500).json({ error: 'Failed to get items' });
    }

    const result = docs || [];

    const enriched = result.map(item => {
      const owner = users.findOne({ _id: item.user_id });
      return { ...item, id: item._id, owner_name: owner?.nickname };
    });

    enriched.sort((a, b) => new Date(a.expiry_date) - new Date(b.expiry_date));

    res.json(enriched);
  });
});

router.post('/', (req, res) => {
  const { barcode, name, category, expiry_date, notes, purchase_date, shelf_life_days } = req.body;

  if (!name || !expiry_date) {
    return res.status(400).json({ error: 'Name and expiry date are required' });
  }

  let finalExpiryDate = expiry_date;

  if (purchase_date && shelf_life_days) {
    if (shelf_life_days <= 0 || !Number.isInteger(shelf_life_days)) {
      return res.status(400).json({ error: 'shelf_life_days must be a positive integer' });
    }
    if (new Date(purchase_date) > new Date(expiry_date)) {
      return res.status(400).json({ error: 'purchase_date cannot be after expiry_date' });
    }
    const purchaseDateObj = new Date(purchase_date);
    purchaseDateObj.setDate(purchaseDateObj.getDate() + shelf_life_days);
    finalExpiryDate = purchaseDateObj.toISOString().split('T')[0];
  } else if (shelf_life_days && !purchase_date) {
    return res.status(400).json({ error: 'purchase_date is required when shelf_life_days is provided' });
  } else if (purchase_date && !shelf_life_days) {
    return res.status(400).json({ error: 'shelf_life_days is required when purchase_date is provided' });
  }

  const doc = {
    user_id: req.user.id,
    barcode: barcode || null,
    name,
    category: category || '其他',
    expiry_date: finalExpiryDate,
    purchase_date: purchase_date || null,
    shelf_life_days: shelf_life_days || null,
    notes: notes || null,
    status: 'active',
    added_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  items.insert(doc, (err, newDoc) => {
    if (err) {
      console.error('Create item error:', err);
      return res.status(500).json({ error: 'Failed to create item' });
    }
    res.status(201).json({ ...newDoc, id: newDoc._id });
  });
});

router.get('/scan/:barcode', (req, res) => {
  const { barcode } = req.params;
  const product = lookupBarcode(barcode);

  if (product) {
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + product.defaultExpiryDays);
    
    res.json({
      found: true,
      barcode,
      name: product.name,
      category: product.category,
      suggestedExpiryDate: expiryDate.toISOString().split('T')[0],
      defaultExpiryDays: product.defaultExpiryDays
    });
  } else {
    res.json({
      found: false,
      barcode,
      message: 'Product not found in database. Please enter details manually.'
    });
  }
});

router.get('/barcodes', (req, res) => {
  res.json({
    products: getAllProducts(),
    categories: getCategories()
  });
});

router.get('/:id', (req, res) => {
  const { id } = req.params;

  items.findOne({ _id: id, user_id: req.user.id }, (err, item) => {
    if (err) {
      console.error('Get item error:', err);
      return res.status(500).json({ error: 'Failed to get item' });
    }
    if (!item) {
      return res.status(404).json({ error: 'Item not found' });
    }
    res.json({ ...item, id: item._id });
  });
});

router.put('/:id', (req, res) => {
  const { id } = req.params;
  const { name, category, expiry_date, notes, status, purchase_date, shelf_life_days } = req.body;

  items.findOne({ _id: id, user_id: req.user.id }, (err, existingItem) => {
    if (err) {
      console.error('Get item error:', err);
      return res.status(500).json({ error: 'Failed to get item' });
    }
    if (!existingItem) {
      return res.status(404).json({ error: 'Item not found' });
    }

    let finalExpiryDate = expiry_date || existingItem.expiry_date;

    if (purchase_date !== undefined || shelf_life_days !== undefined) {
      const finalPurchaseDate = purchase_date !== undefined ? purchase_date : existingItem.purchase_date;
      const finalShelfLifeDays = shelf_life_days !== undefined ? shelf_life_days : existingItem.shelf_life_days;

      if (finalPurchaseDate && finalShelfLifeDays) {
        if (finalShelfLifeDays <= 0 || !Number.isInteger(finalShelfLifeDays)) {
          return res.status(400).json({ error: 'shelf_life_days must be a positive integer' });
        }
        if (new Date(finalPurchaseDate) > new Date(finalExpiryDate)) {
          return res.status(400).json({ error: 'purchase_date cannot be after expiry_date' });
        }
        const purchaseDateObj = new Date(finalPurchaseDate);
        purchaseDateObj.setDate(purchaseDateObj.getDate() + finalShelfLifeDays);
        finalExpiryDate = purchaseDateObj.toISOString().split('T')[0];
      } else if (finalShelfLifeDays && !finalPurchaseDate) {
        return res.status(400).json({ error: 'purchase_date is required when shelf_life_days is provided' });
      } else if (finalPurchaseDate && !finalShelfLifeDays) {
        return res.status(400).json({ error: 'shelf_life_days is required when purchase_date is provided' });
      }
    }

    const updates = { updated_at: new Date().toISOString() };
    if (name) updates.name = name;
    if (category) updates.category = category;
    if (expiry_date !== undefined) updates.expiry_date = finalExpiryDate;
    if (notes !== undefined) updates.notes = notes;
    if (status) updates.status = status;
    if (purchase_date !== undefined) updates.purchase_date = purchase_date || null;
    if (shelf_life_days !== undefined) updates.shelf_life_days = shelf_life_days || null;

    items.update({ _id: id }, { $set: updates }, {}, (err) => {
      if (err) {
        console.error('Update item error:', err);
        return res.status(500).json({ error: 'Failed to update item' });
      }

      items.findOne({ _id: id }, (err, item) => {
        if (err) {
          console.error('Get updated item error:', err);
          return res.status(500).json({ error: 'Failed to get updated item' });
        }
        res.json({ ...item, id: item._id });
      });
    });
  });
});

router.delete('/:id', (req, res) => {
  const { id } = req.params;

  items.findOne({ _id: id, user_id: req.user.id }, (err, item) => {
    if (err) {
      console.error('Get item error:', err);
      return res.status(500).json({ error: 'Failed to get item' });
    }
    if (!item) {
      return res.status(404).json({ error: 'Item not found' });
    }

    items.remove({ _id: id }, {}, (err) => {
      if (err) {
        console.error('Delete item error:', err);
        return res.status(500).json({ error: 'Failed to delete item' });
      }
      res.json({ message: 'Item deleted successfully' });
    });
  });
});

module.exports = router;
