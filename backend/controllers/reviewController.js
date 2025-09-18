const reviewModel = require('../models/reviewModel');

async function getReviews(req, res) {
  try {
    const approved = await reviewModel.getApprovedReviews();
    const reviews = approved.map(r => ({
      _id: r._id.toString(),
      name: r.name || '',
      comment: r.comment || '',
      created_at: r.created_at ? r.created_at.toISOString() : ''
    }));
    res.json({ reviews });
  } catch (error) {
    console.error('Error fetching reviews:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
}

module.exports = { getReviews };