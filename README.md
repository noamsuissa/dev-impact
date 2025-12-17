<p align="center">
  <img src="frontend/public/dev-impact-large.png" width="120" />
</p>

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
- A GitHub account (optional)
- Cloud or [Self-hosted](https://supabase.com/docs/guides/self-hosting/docker) Supabase

### Environment Setup

Copy `.env.example` to `.env` in both the `backend` and `frontend` folders and fill in the required values. You’ll need to provide your Supabase keys and set the correct redirect URLs.

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
cd dev-impact
pip install -r backend/requirements.txt
python -m backend.main
or
uvicorn backend.main:app --reload --host 0.0.0.0 --port 3000
```

### Frontend Setup

```bash
cd dev-impact/frontend
npm install
npm run dev
```

### Quick Start

1. Start both backend and frontend servers (see above)
2. Open `http://localhost:5173` in your browser
3. Click "Get Started" and complete onboarding
4. Connect your GitHub account (optional but recommended)
5. Start building your impact profile!
6. Click "Publish Profile" to get a shareable link!

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

### Development Guidelines

- **Code Style**: Follow existing patterns and conventions.
- **Commit Messages**: Use clear, descriptive messages (e.g., "feat: add GitHub OAuth", "fix: dashboard rendering").
- **Documentation**: Update relevant docs if you change functionality.
- **Testing**: Manually test your changes before submitting.

**Want to help but not sure where to start?** Check out our [issues](https://github.com/noamsuissa/dev-impact/issues) for bugs, feature requests, and good first contributions!


## License

This project is licensed under the AGPLv3 - see the [LICENSE](LICENSE) file for details.

## Questions?

- Open an issue for any questions or problems

---

Built with ❤️ by developers, for developers.
