/**
 * Reusable Coin Animation System
 * Usage: CoinAnimation.show(coins, message, options)
 */

class CoinAnimation {
    constructor() {
        this.defaultOptions = {
            coins: 75,
            message: "🎉 You earned {coins} coins! 🎉",
            duration: 5000,
            notificationDuration: 3000,
            numberOfCoins: 15,
            coinDelay: 100,
            animationDelay: 500
        };
        
        this.ensureStylesLoaded();
    }

    /**
     * Show coin celebration animation
     * @param {number} coins - Number of coins earned
     * @param {string} message - Custom message (use {coins} placeholder)
     * @param {object} options - Animation options
     */
    show(coins = 75, message = null, options = {}) {
        const config = { ...this.defaultOptions, ...options };
        const finalMessage = message || config.message.replace('{coins}', coins);
        
        setTimeout(() => {
            this.createCelebration(coins, finalMessage, config);
        }, config.animationDelay);
    }

    /**
     * Show celebration for specific step bonus
     * @param {number} stepNumber - Step number (1, 2, 3, etc.)
     * @param {number} coins - Coins awarded
     */
    showStepBonus(stepNumber, coins) {
        const stepNames = {
            1: "Intro Interview",
            2: "Story Brainstorm",
            3: "Start Writing",
            4: "World Building",
            5: "Character Creation"
        };
        
        const stepName = stepNames[stepNumber] || `Step ${stepNumber}`;
        const message = `🎉 ${stepName} Complete! +${coins} coins! 🎉`;
        
        this.show(coins, message);
    }

    /**
     * Show custom celebration
     * @param {string} title - Achievement title
     * @param {number} coins - Coins awarded
     */
    showAchievement(title, coins) {
        const message = `🏆 ${title}! +${coins} coins! 🏆`;
        this.show(coins, message);
    }

    /**
     * Create the celebration elements
     */
    createCelebration(coins, message, config) {
        // Create coin celebration container
        const celebrationContainer = document.createElement('div');
        celebrationContainer.className = 'coin-celebration';
        document.body.appendChild(celebrationContainer);
        
        // Create bonus notification
        const bonusNotification = document.createElement('div');
        bonusNotification.className = 'bonus-notification';
        bonusNotification.innerHTML = `
            <div class="coin-icon"></div>
            <span>${message}</span>
        `;
        document.body.appendChild(bonusNotification);
        
        // Create falling coins
        for (let i = 0; i < config.numberOfCoins; i++) {
            setTimeout(() => {
                const coin = this.createCoin();
                celebrationContainer.appendChild(coin);
            }, i * config.coinDelay);
        }
        
        // Remove bonus notification
        setTimeout(() => {
            bonusNotification.classList.add('fadeOut');
            setTimeout(() => {
                if (bonusNotification.parentNode) {
                    bonusNotification.remove();
                }
            }, 400);
        }, config.notificationDuration);
        
        // Remove celebration container
        setTimeout(() => {
            if (celebrationContainer.parentNode) {
                celebrationContainer.remove();
            }
        }, config.duration);
    }

    /**
     * Create individual coin element
     */
    createCoin() {
        const coin = document.createElement('div');
        coin.className = 'coin';
        
        // Random horizontal position
        coin.style.left = Math.random() * 100 + '%';
        
        // Slight random delay for more natural effect
        coin.style.animationDelay = (Math.random() * 0.5) + 's';
        
        // Random coin size variation (80% to 120%)
        const sizeVariation = 0.8 + (Math.random() * 0.4);
        coin.style.transform = `scale(${sizeVariation})`;
        
        return coin;
    }

    /**
     * Ensure CSS styles are loaded
     */
    ensureStylesLoaded() {
        if (document.getElementById('coin-animation-styles')) {
            return; // Styles already loaded
        }

        const style = document.createElement('style');
        style.id = 'coin-animation-styles';
        style.textContent = `
            /* Coin Animation Styles */
            .coin-celebration {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                pointer-events: none;
                z-index: 9999;
                overflow: hidden;
            }
            
            .coin {
                position: absolute;
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: 3px solid #B45309;
                box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
                animation: coinFall 3s ease-out forwards;
            }
            
            .coin::before {
                content: '$';
                font-size: 18px;
            }
            
            .bonus-notification {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                color: white;
                padding: 24px 32px;
                border-radius: 16px;
                font-size: 18px;
                font-weight: 700;
                box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
                z-index: 10000;
                animation: bonusPopIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                border: 2px solid #047857;
                max-width: 90vw;
                text-align: center;
            }
            
            .bonus-notification .coin-icon {
                display: inline-block;
                width: 24px;
                height: 24px;
                background: #F59E0B;
                border-radius: 50%;
                margin-right: 8px;
                vertical-align: middle;
                position: relative;
            }
            
            .bonus-notification .coin-icon::before {
                content: '$';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            
            @keyframes coinFall {
                0% {
                    transform: translateY(-100px) rotate(0deg);
                    opacity: 1;
                }
                70% {
                    opacity: 1;
                }
                100% {
                    transform: translateY(100vh) rotate(720deg);
                    opacity: 0;
                }
            }
            
            @keyframes bonusPopIn {
                0% {
                    transform: translate(-50%, -50%) scale(0.5);
                    opacity: 0;
                }
                100% {
                    transform: translate(-50%, -50%) scale(1);
                    opacity: 1;
                }
            }
            
            @keyframes bonusPopOut {
                0% {
                    transform: translate(-50%, -50%) scale(1);
                    opacity: 1;
                }
                100% {
                    transform: translate(-50%, -50%) scale(0.8);
                    opacity: 0;
                }
            }
            
            .bonus-notification.fadeOut {
                animation: bonusPopOut 0.4s ease-in forwards;
            }
            
            /* Responsive adjustments */
            @media (max-width: 768px) {
                .bonus-notification {
                    font-size: 16px;
                    padding: 20px 24px;
                }
                
                .coin {
                    width: 35px;
                    height: 35px;
                    font-size: 12px;
                }
                
                .coin::before {
                    font-size: 16px;
                }
            }
        `;
        
        document.head.appendChild(style);
    }
}

// Create global instance
window.CoinAnimation = new CoinAnimation();

// Also provide direct methods for convenience
window.showCoinCelebration = (coins, message, options) => window.CoinAnimation.show(coins, message, options);
window.showStepBonus = (stepNumber, coins) => window.CoinAnimation.showStepBonus(stepNumber, coins);
window.showAchievement = (title, coins) => window.CoinAnimation.showAchievement(title, coins);