# dev-impact

> A new standard in showcasing developer impact. Out with the old resumes that end up nowhere.

## Motivation

Traditional resumes are static documents that rarely capture the true impact of a developer's work. They get lost in the pile, forgotten in inboxes, and fail to tell the compelling story of what you've actually built and achieved.

**dev-impact** changes this. It's a platform for developers to showcase their real impact through:
- Quantifiable metrics that matter
- Clear problem-solution narratives
- Beautiful, shareable profiles
- Easy export to multiple formats

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

For detailed setup and testing instructions, see [SETUP.md](SETUP.md) and [TESTING.md](TESTING.md).

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

- Additional OAuth providers (GitLab, Bitbucket)
- More export formats (PDF, JSON Resume)
- Analytics and insights features
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
- **Frontend**: React, Vite, TailwindCSS
- **OAuth**: GitHub Device Flow
- **Storage**: Browser localStorage (no database required)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Questions?

- Check out [SETUP.md](SETUP.md) for detailed setup instructions
- See [TESTING.md](TESTING.md) for testing guidelines
- Open an issue for any questions or problems

---

Built with ❤️ by developers, for developers.
