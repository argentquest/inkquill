# Reusable Coin Animation System

## Overview
A reusable JavaScript class for displaying coin celebration animations throughout the application.

## Files
- `/app/static/js/coin-animation.js` - Main animation system
- Automatically included in `base.html` layout

## Usage Examples

### Basic Usage
```javascript
// Show simple coin celebration
showCoinCelebration(75, "🎉 You earned 75 coins! 🎉");

// Or use the class directly
CoinAnimation.show(75, "🎉 You earned 75 coins! 🎉");
```

### Step Bonuses
```javascript
// Show step-specific bonus (auto-generates message)
showStepBonus(1, 75);  // "🎉 Intro Interview Complete! +75 coins! 🎉"
showStepBonus(2, 50);  // "🎉 Story Brainstorm Complete! +50 coins! 🎉"
showStepBonus(3, 50);  // "🎉 Start Writing Complete! +50 coins! 🎉"
```

### Achievement Celebrations
```javascript
// Show custom achievement
showAchievement("First Story Published", 100);
// "🏆 First Story Published! +100 coins! 🏆"
```

### Advanced Customization
```javascript
CoinAnimation.show(200, "🎊 Epic Bonus! {coins} coins! 🎊", {
    numberOfCoins: 25,        // More falling coins
    duration: 7000,           // Longer animation
    notificationDuration: 4000, // Longer popup
    animationDelay: 200       // Delayed start
});
```

## API Reference

### CoinAnimation.show(coins, message, options)
- **coins** (number): Number of coins earned
- **message** (string): Custom message (use `{coins}` placeholder)
- **options** (object): Animation configuration

### CoinAnimation.showStepBonus(stepNumber, coins)
- **stepNumber** (number): Step number (1-5 have predefined names)
- **coins** (number): Coins awarded

### CoinAnimation.showAchievement(title, coins)
- **title** (string): Achievement title
- **coins** (number): Coins awarded

## Configuration Options
```javascript
{
    coins: 75,                    // Default coin amount
    message: "🎉 You earned {coins} coins! 🎉", // Default message
    duration: 5000,               // Total animation duration (ms)
    notificationDuration: 3000,   // Popup duration (ms)
    numberOfCoins: 15,            // Number of falling coins
    coinDelay: 100,               // Delay between coin drops (ms)
    animationDelay: 500           // Delay before animation starts (ms)
}
```

## Animation Features
- **Falling Coins**: 15 golden coins with spinning animation
- **Popup Notification**: Center-screen bonus message
- **Responsive Design**: Works on all screen sizes
- **Auto Cleanup**: All elements removed after animation
- **Size Variation**: Coins have random size variations (80%-120%)
- **Staggered Timing**: Coins appear with slight delays for natural effect

## Integration Points

### Welcome Interview
- Automatically triggered on interview completion
- Uses `showStepBonus(1, 75)`

### Home Page Step Progression
- Triggered via `markStepCompleted()` function
- Uses `showStepBonus(step, coinAmount)`

### Future Integrations
- Story completion bonuses
- Achievement unlocks
- Daily/weekly bonuses
- Special event celebrations

## Browser Compatibility
- Modern browsers (ES6+ support required)
- Mobile responsive
- Hardware accelerated animations