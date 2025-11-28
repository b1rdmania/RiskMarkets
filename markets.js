// Shared market metadata for WAR.MARKET indices
// Single source of truth for terminal + future integrations

window.WAR_MARKETS = [
  {
    code: 'GDR',
    slug: 'gdr',
    displayName: 'GDR',
    longName: 'Defence Rotation Index',
    subtitle: 'DEFENCE ROTATION INDEX',
    description: 'A synthetic sector index tracking momentum across defence industries.',
    price: '$102.44',
    change: '+2.18%',
    changeDirection: 'up',
    volume: '$1.67M',
    stress: 'MEDIUM',
    composition: [
      '30% LMT',
      '25% RTX',
      '25% NOC',
      '20% PLTR'
    ]
  },
  {
    code: 'ESV',
    slug: 'esv',
    displayName: 'ESV',
    longName: 'Energy Shock Volatility',
    subtitle: 'ENERGY SHOCK VOLATILITY',
    description: 'A composite index measuring volatility across global energy routes.',
    price: '$88.12',
    change: '+1.04%',
    changeDirection: 'up',
    volume: '$2.41M',
    stress: 'HIGH',
    composition: [
      '40% WTI Crude',
      '25% Natural Gas',
      '20% Freight/Shipping Proxy',
      '15% Gold'
    ]
  },
  {
    code: 'SHR',
    slug: 'shr',
    displayName: 'SHR',
    longName: 'Safe Haven Rotation',
    subtitle: 'SAFE HAVEN ROTATION',
    description: 'A synthetic risk-off index tracking safe-haven flows.',
    price: '$74.55',
    change: '-0.33%',
    changeDirection: 'down',
    volume: '$1.12M',
    stress: 'LOW',
    composition: [
      '40% Gold',
      '30% CHF (USD/CHF inverse)',
      '30% JPY (USD/JPY inverse)'
    ]
  }
];


