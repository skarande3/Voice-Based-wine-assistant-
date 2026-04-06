# Wineard - Voice Wine Explorer by Onki

A premium, Apple-inspired voice-based wine assistant web application.

## 🍷 Features

- **Voice-First Experience**: Ask questions about wines using your voice
- **Intelligent Answers**: Get recommendations based on price, region, rating, and occasion
- **Text-to-Speech**: Wineard speaks answers aloud
- **Premium UI**: Glassmorphism design with smooth animations
- **Multiple Screens**: Welcome → Intro → Voice Interface
- **Animated Mascot**: State-based character animations (idle, listening, processing, responding)
- **Real Wine Data**: Loads from Google Sheets dataset

## 🎨 Design Highlights

- Deep wine red (#5B0F1A) color scheme
- Gradient backgrounds with ambient blur effects
- Glassmorphism panels with backdrop blur
- Smooth Motion (Framer Motion) animations
- Voice waveform visualization
- Responsive design

## 🎤 Example Questions

Try asking:
- "Which are the best-rated wines under $50?"
- "What do you have from Burgundy?"
- "What's the most expensive bottle you have?"
- "Which bottles would make a good housewarming gift?"

## 🏗️ Tech Stack

- **React** with TypeScript
- **React Router** for navigation
- **Motion** (Framer Motion) for animations
- **Web Speech API** for voice recognition and synthesis
- **Tailwind CSS v4** for styling
- **Google Sheets** as data source

## 🚀 How It Works

1. **Welcome Screen**: Landing page with call-to-action
2. **Transition Screen**: Animated intro with mascot
3. **Voice Interface**: Main screen where you interact with Wineard
   - Tap microphone to ask questions
   - Wineard listens, processes, and responds
   - View transcripts and responses on screen
   - Hear answers spoken aloud

## 📊 Data Source

Wine data is loaded from a public Google Sheets spreadsheet containing:
- Wine names
- Regions
- Varietals
- Vintages
- Prices
- Ratings
- Descriptions

## 🎯 Voice States

- **Idle**: Ready to listen (gentle floating animation)
- **Listening**: Recording your question (ear highlighted, waveform visible)
- **Processing**: Analyzing question (pulsing glow)
- **Responding**: Speaking answer (bounce animation)

## 🌐 Browser Compatibility

Best experienced in:
- Chrome/Edge (full Web Speech API support)
- Safari (partial support)
- Firefox (limited support)

**Note**: Voice recognition requires HTTPS in production.

---

Built with ❤️ for Onki
