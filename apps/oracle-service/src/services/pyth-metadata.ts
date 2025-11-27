import { fetch } from 'undici';
import { config } from '../config';

export interface FeedMetadata {
  id: string;
  symbol?: string;
  asset_type?: string;
  quote_currency?: string;
  description?: string;
}

export async function fetchFeedMetadata(feedId: string): Promise<FeedMetadata | null> {
  try {
    const url = `${config.pythApiUrl}/price_feeds_metadata`;
    const params = new URLSearchParams();
    if (config.pythCluster) {
      params.append('cluster', config.pythCluster);
    }
    
    const response = await fetch(`${url}?${params}`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });

    if (!response.ok) {
      console.warn(`[metadata] API returned ${response.status}, skipping metadata lookup`);
      return null;
    }

    const data = await response.json() as FeedMetadata[];
    const feed = data.find((f) => f.id === feedId || f.id === `0x${feedId}` || f.id === feedId.replace('0x', ''));
    
    return feed || null;
  } catch (err) {
    console.warn(`[metadata] Failed to fetch metadata:`, err);
    return null;
  }
}

export async function listAvailableFeeds(query?: string): Promise<FeedMetadata[]> {
  try {
    const url = `${config.pythApiUrl}/price_feeds_metadata`;
    const params = new URLSearchParams();
    if (config.pythCluster) {
      params.append('cluster', config.pythCluster);
    }
    if (query) {
      params.append('search', query);
    }
    
    const response = await fetch(`${url}?${params}`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });

    if (!response.ok) {
      return [];
    }

    const data = await response.json() as FeedMetadata[];
    return data || [];
  } catch (err) {
    console.warn(`[metadata] Failed to list feeds:`, err);
    return [];
  }
}

export async function validateFeedId(feedId: string): Promise<boolean> {
  const metadata = await fetchFeedMetadata(feedId);
  if (metadata) {
    return true;
  }
  
  // Fallback: try to fetch actual price to validate
  try {
    const url = `${config.pythApiUrl}/latest_price_feeds`;
    const params = new URLSearchParams();
    params.append('ids[]', feedId);
    if (config.pythCluster) {
      params.append('cluster', config.pythCluster);
    }
    
    const response = await fetch(`${url}?${params}`);
    if (response.ok) {
      const data = await response.json();
      return Array.isArray(data) && data.length > 0;
    }
  } catch (err) {
    // ignore
  }
  
  return false;
}

