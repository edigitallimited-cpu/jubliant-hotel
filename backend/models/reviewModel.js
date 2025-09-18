// const { MongoClient } = require('mongodb');

// const uri = 'mongodb+srv://jubilantlandhotelloungebarspa_db_user:Juba73812@@@jubilanthotel.dybd1xl.mongodb.net/jubilant_hotel?retryWrites=true&w=majority';

// const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

async function getApprovedReviews() {
  try {
    await client.connect();
    const db = client.db('jubilant_hotel');
    const reviewsCollection = db.collection('reviews');
    const reviews = await reviewsCollection.find({ approved: true }).sort({ created_at: -1 }).toArray();
    return reviews;
  } catch (error) {
    console.error('Error fetching reviews:', error);
    return [];
  }
}

module.exports = { getApprovedReviews };