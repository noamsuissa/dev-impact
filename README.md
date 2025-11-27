# dev-impact

> A new standard in showcasing developer impact. Out with the old resumes that end up nowhere.

## Motivation

Traditional resumes are static documents that rarely capture the true impact of a developer's work. They get lost in the pile, forgotten in inboxes, and fail to tell the compelling story of what you've actually built and achieved.

**dev-impact** changes this. It's a platform for developers to showcase their real impact through:
- Quantifiable metrics that matter
- Clear problem-solution narratives
- Beautiful, shareable profiles at `dev-impact.io/your-username`
- Easy export to multiple formats
- Public profile links to share with anyone

Show your work. Show your impact. Stand out.

## How to Run

### Prerequisites
- Python 3.8+
- Node.js 16+
- A GitHub account

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The backend API will run at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at `http://localhost:5173`

### Quick Start

1. Start both backend and frontend servers (see above)
2. Open `http://localhost:5173` in your browser
3. Click "Get Started" and complete onboarding
4. Connect your GitHub account (optional but recommended)
5. Start building your impact profile!
6. Click "Publish Profile" to get a shareable link!

## Features

### 🎯 Core Features
- **Project Builder**: Add projects with metrics, tech stack, and impact stories
- **Profile Preview**: See how your profile looks before sharing
- **GitHub Integration**: Connect your GitHub for seamless username generation
- **Export Options**: Download your profile in multiple formats

### 🚀 Publish & Share (NEW!)
- **One-Click Publish**: Generate shareable links instantly
- **Public Profiles**: Share at `dev-impact.io/your-username`
- **No Auth Required**: Anyone can view your published profile
- **View Tracking**: See how many times your profile has been viewed
- **Auto Username**: Uses your GitHub username or generates from your name

👉 **[Quick Start Guide](PUBLISH_README.md)** - Get publishing in 5 minutes!

📚 **Full Documentation**:
- [Publish Feature Overview](docs/PUBLISH_FEATURE.md)
- [Setup Instructions](docs/PUBLISH_SETUP.md)
- [Production Deployment](docs/PRODUCTION_DEPLOYMENT.md)

## How to Contribute

We welcome contributions! Here's how you can help:

### Reporting Issues
- Found a bug? Open an issue with details and steps to reproduce
- Have a feature idea? Share it in the issues with the "enhancement" label

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/dev-impact.git
   cd dev-impact
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

3. **Make your changes**
   - Backend: Follow FastAPI best practices
   - Frontend: Keep the terminal aesthetic consistent
   - Write clear commit messages

4. **Test your changes**
   - Ensure backend starts without errors
   - Verify frontend functionality works
   - Check that existing features aren't broken

5. **Submit a pull request**
   - Describe what you changed and why
   - Reference any related issues
   - Wait for review and feedback

### Development Guidelines

- **Code Style**: Follow existing patterns and conventions
- **Commit Messages**: Use clear, descriptive messages (e.g., "feat: add GitHub OAuth", "fix: dashboard rendering")
- **Documentation**: Update relevant docs if you change functionality
- **Testing**: Manually test your changes before submitting

### Areas We'd Love Help With

- Custom usernames (let users choose their own)
- Profile analytics dashboard
- SEO optimization for public profiles
- Social media preview cards (Open Graph)
- Additional OAuth providers (GitLab, Bitbucket)
- More export formats (PDF, JSON Resume)
- Profile themes and customization
- Mobile responsive improvements
- Accessibility enhancements
- Performance optimizations

## Project Structure

```
dev-impact/
├── backend/          # FastAPI backend
│   ├── routers/      # API endpoints
│   ├── services/     # Business logic
│   └── models/       # Data models
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── utils/       # Helper functions
└── docs/            # Documentation
```

## Tech Stack

- **Backend**: FastAPI, Python 3.12
- **Frontend**: React 19, Vite, TailwindCSS, React Router
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **OAuth**: GitHub Device Flow
- **Hosting**: Ready for Vercel, Railway, Fly.io, etc.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Questions?

- Open an issue for any questions or problems

---

Built with ❤️ by developers, for developers.
