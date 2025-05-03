import express from 'express';
import config from '../config/config';

const googleRouter = express.Router();

// Google Places Autocomplete API endpoint
googleRouter.get('/places-autocomplete', async (req, res) => {
    const { query } = req.query;
    
    if (!query || (typeof query === 'string' && query.length < 2)) {
        res.status(400).json({ error: 'Query must be at least 2 characters' });
    }
    
    try {
        // Use your server-side API key safely
        const API_KEY = config.googlePlacesApiKey;
        
        if (!API_KEY) {
            throw new Error('Google Places API key is not defined');
        }
        
        const response = await fetch(
            `https://maps.googleapis.com/maps/api/place/autocomplete/json?input=${encodeURIComponent(String(query))}&key=${API_KEY}`
        );
        
        if (!response.ok) {
            throw new Error('Failed to fetch from Google Places API');
        }
        
        const data = await response.json();
        res.status(200).json(data);
        
    } catch (error) {
        console.error('Error in places-autocomplete API:', error);
        res.status(500).json({ error: 'Failed to fetch suggestions' });
    }
});

// Place Details API endpoint
googleRouter.get('/place-details', async (req, res) => {
    const { placeId } = req.query;
    
    if (!placeId) {
        res.status(400).json({ error: 'Place ID is required' });
    }
    
    try {
        // Use your server-side API key safely
        const API_KEY = config.googlePlacesApiKey;
        
        if (!API_KEY) {
            throw new Error('Google Places API key is not defined');
        }
        
        const response = await fetch(
            `https://maps.googleapis.com/maps/api/place/details/json?place_id=${encodeURIComponent(String(placeId))}&key=${API_KEY}`
        );
        
        if (!response.ok) {
            throw new Error('Failed to fetch from Google Places API');
        }
        
        const data = await response.json();
        res.status(200).json(data);
        
    } catch (error) {
        console.error('Error in place-details API:', error);
        res.status(500).json({ error: 'Failed to fetch place details' });
    }
});

export default googleRouter;