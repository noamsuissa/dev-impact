# 💥 dev-impact

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
- Cloud or [Self-hosted](https://supabase.com/docs/guides/self-hosting/docker) Supabase

### Environment Setup

Copy `.env.example` to `.env` in both the `backend` and `frontend` folders and fill in the required values. You’ll need to provide your Supabase keys and set the correct redirect URLs.

> Set `AUTH_REDIRECT_URL` to your frontend’s base URL (e.g., `http://localhost:5173`).  
> The backend uses this for Supabase email flows (signup + password reset), and the frontend automatically routes recovery links to `/reset-password`.

---

Once your `.env` files are ready, continue with the Backend and Frontend setup below!

### Database Migrations (Supabase)

Apply the migrations in the `backend/migrations` folder *in order* using the Supabase SQL editor:

1. Open your Supabase project and go to the "SQL Editor".
2. Start with the lowest migration number (e.g., `001_...`), open the file, and paste its contents into the SQL editor.
3. Run the SQL snippet.
4. Repeat for each next migration (`002_...`, etc.), **in order**, until all migrations are applied.

This will set up the database tables and policies required for dev-impact to work!



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

📚 **Full Documentation**:
- See `backend/README.md` for backend architecture, API endpoints, and environment variables
- See `backend/CONTRIBUTING.md` for backend design patterns and contribution guidelines


## How to Contribute

We welcome contributions 🫶! Here's how you can help:

### Reporting Issues
- Found a bug? Open an issue with details and steps to reproduce.
- Have a feature idea? Share it in the issues with the "enhancement" label.

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/dev-impact.git
   cd dev-impact
   ```

2. **Create a feature branch**
   - Make sure your fork is up to date with the upstream repository. By default, all contributions should branch from the `main` branch.
   - Add the upstream remote and fetch the latest branches:
     ```bash
     git remote add upstream https://github.com/noamsuissa/dev-impact.git
     git fetch upstream
     git checkout main
     git pull upstream main
     ```
   - Create your feature or fix branch from `main`:
     ```bash
     git checkout -b feat/your-feature-name # or fix/ bug/ etc.
     ```

3. **Make your changes**
   - Backend: Follow the patterns in `backend/README.md` and `backend/CONTRIBUTING.md`.
   - Frontend: Keep the terminal aesthetic consistent.
   - Write clear commit messages.

4. **Test your changes**
   - Ensure backend starts without errors.
   - Verify frontend functionality works.
   - Check that existing features aren't broken.

5. **Submit a pull request**
   - Push your branch to your own fork:
     ```bash
     git push origin feat/your-feature-name
     ```
   - Open a pull request **from your fork’s feature branch to the `main` branch on the main repository**.
   - Describe what you changed and why.
   - Reference any related issues.
   - Wait for review and feedback.

> **Note:** Only maintainers merge to `main` (connected to the production platform).

### Development Guidelines

- **Code Style**: Follow existing patterns and conventions.
- **Commit Messages**: Use clear, descriptive messages (e.g., "feat: add GitHub OAuth", "fix: dashboard rendering").
- **Documentation**: Update relevant docs if you change functionality.
- **Testing**: Manually test your changes before submitting.

### Areas We'd Love Help With
**Want to help but not sure where to start?** Check out our [issues](https://github.com/noamsuissa/dev-impact/issues) for bugs, feature requests, and good first contributions!

Here are some additional ideas:

- Custom usernames (let users choose their own)
- Profile analytics dashboard
- SEO optimization for public profiles
- Additional OAuth providers (GitLab, Bitbucket)
- More export formats (PDF, JSON Resume)
- Profile themes and customization
- Mobile responsive improvements
- Accessibility enhancements
- Performance optimizations

## Project Structure

```
dev-impact/
├── backend/              # FastAPI backend API
│   ├── routers/          # API route handlers
│   ├── services/         # Business logic layer
│   ├── schemas/          # Pydantic request/response models
│   ├── utils/            # Shared backend utilities (auth, Supabase client, etc.)
│   └── migrations/       # SQL database migrations
├── frontend/             # React frontend (Vite + Tailwind)
│   └── src/
│       ├── components/   # React components and pages
│       ├── contexts/     # React context (e.g., auth)
│       ├── hooks/        # Reusable hooks
│       └── utils/        # API client and helper functions
```

## Tech Stack

- **Backend**: FastAPI, Python 3.12
- **Frontend**: React 19, Vite, TailwindCSS, React Router
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **OAuth**: GitHub Device Flow
- **Hosting**: Ready for Vercel, Railway, Fly.io, etc.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Questions?

- Open an issue for any questions or problems

---

Built with ❤️ by developers, for developers.
