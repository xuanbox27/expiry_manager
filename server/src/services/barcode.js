const barcodeDatabase = {
  '6901028001688': { name: '农夫山泉矿泉水', category: '饮料', defaultExpiryDays: 730 },
  '6920202888888': { name: '康师傅方便面', category: '食品', defaultExpiryDays: 365 },
  '6954767420127': { name: '蒙牛纯牛奶', category: '乳制品', defaultExpiryDays: 180 },
  '6928155610010': { name: '海天酱油', category: '调味品', defaultExpiryDays: 730 },
  '6902083901012': { name: '小熊饼干', category: '零食', defaultExpiryDays: 365 },
  '6901234567890': { name: '可口可乐', category: '饮料', defaultExpiryDays: 365 },
  '6912345678901': { name: '奥利奥饼干', category: '零食', defaultExpiryDays: 365 },
  '6923456789012': { name: '伊利纯牛奶', category: '乳制品', defaultExpiryDays: 180 },
  '6934567890123': { name: '旺旺雪饼', category: '零食', defaultExpiryDays: 270 },
  '6945678901234': { name: '农夫山泉纯净水', category: '饮料', defaultExpiryDays: 730 },
  '6956789012345': { name: '康师傅冰红茶', category: '饮料', defaultExpiryDays: 365 },
  '6967890123456': { name: '金纺柔顺剂', category: '日用品', defaultExpiryDays: 1095 },
  '6978901234567': { name: '多芬沐浴露', category: '化妆品', defaultExpiryDays: 730 },
  '6989012345678': { name: '云南白药创可贴', category: '药品', defaultExpiryDays: 1095 },
  '6901234567891': { name: '999感冒灵', category: '药品', defaultExpiryDays: 730 },
  '6912345678902': { name: '维生素C片', category: '药品', defaultExpiryDays: 730 },
  '6923456789013': { name: '飘柔洗发水', category: '化妆品', defaultExpiryDays: 1095 },
  '6934567890124': { name: '潘婷护发素', category: '化妆品', defaultExpiryDays: 1095 },
  '6945678901235': { name: '雕牌洗洁精', category: '日用品', defaultExpiryDays: 730 },
  '6956789012346': { name: '立白洗衣粉', category: '日用品', defaultExpiryDays: 1095 },
  '6967890123457': { name: '高露洁牙膏', category: '日用品', defaultExpiryDays: 730 },
  '6978901234568': { name: '佳洁士牙刷', category: '日用品', defaultExpiryDays: 1095 },
  '6989012345679': { name: '吉列剃须刀', category: '日用品', defaultExpiryDays: 1095 },
  '6901234567892': { name: '红牛功能饮料', category: '饮料', defaultExpiryDays: 365 },
  '6912345678903': { name: '王老吉凉茶', category: '饮料', defaultExpiryDays: 365 },
  '6923456789014': { name: '加多宝凉茶', category: '饮料', defaultExpiryDays: 365 },
  '6934567890125': { name: '青岛啤酒', category: '饮料', defaultExpiryDays: 365 },
  '6945678901236': { name: '雪花啤酒', category: '饮料', defaultExpiryDays: 365 },
  '6956789012347': { name: '农夫果园果汁', category: '饮料', defaultExpiryDays: 365 },
  '6967890123458': { name: '汇源果汁', category: '饮料', defaultExpiryDays: 365 },
};

function lookupBarcode(barcode) {
  return barcodeDatabase[barcode] || null;
}

function getAllProducts() {
  return Object.entries(barcodeDatabase).map(([barcode, data]) => ({
    barcode,
    ...data
  }));
}

function getCategories() {
  return [...new Set(Object.values(barcodeDatabase).map(p => p.category))];
}

module.exports = { lookupBarcode, getAllProducts, getCategories };
