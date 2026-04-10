export const generateMockOHLC = (length, startPrice = 150) => {
  const data = [];
  let currentOpen = startPrice;
  // Starting timestamp (e.g., 2026-01-01)
  let currentTime = new Date('2026-01-01T09:30:00Z').getTime() / 1000;

  for (let i = 0; i < length; i++) {
    // Random volatility
    const volatility = currentOpen * 0.005; 
    const close = currentOpen + (Math.random() - 0.5) * volatility * 2;
    const high = Math.max(currentOpen, close) + Math.random() * volatility;
    const low = Math.min(currentOpen, close) - Math.random() * volatility;
    const volume = Math.floor(Math.random() * 100000) + 10000;

    data.push({
      time: currentTime, // UNIX timestamp in seconds
      open: currentOpen,
      high,
      low,
      close,
      value: close, // Used for the line chart series
      volume,
    });

    // Next open is roughly the previous close
    currentOpen = close + (Math.random() - 0.5) * volatility * 0.2;
    // Add 1 hour per tick
    currentTime += 3600; 
  }

  return data;
};

// Simple Moving Average (SMA) calculator
export const calculateSMA = (data, period = 14) => {
  const smaData = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      continue; // Not enough data yet
    }
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close;
    }
    smaData.push({
      time: data[i].time,
      value: sum / period,
    });
  }
  return smaData;
}
