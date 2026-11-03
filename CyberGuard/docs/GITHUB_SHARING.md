# Sharing the finished work on GitHub

The completed code is committed on a branch in the local clone:

    branch : finish/phase8-database
    base   : main (ab921f1)
    commits: 3  (database layer, documents, subject submissions)

Nothing has been pushed yet. Choose one of the four routes below.

---

## Route 1 - Push the branch and open a Pull Request (recommended)

This keeps `main` clean and gives a review step.

```bat
cd <your path>\CyberGuard

git remote -v                      REM must show origin  https://github.com/jay-kxz/CyberGuard.git
git log --oneline origin/main..HEAD --stat

git push -u origin finish/phase8-database
```

Then on GitHub: the repository page shows **"Compare & pull request"** for the new branch.
Create the pull request, read the file list, and press **Merge pull request**.

## Route 2 - Put it straight on main

Only if the branch is yours alone and nobody else is working in the repository.

```bat
git checkout main
git pull origin main                REM in case she pushed something new
git merge --no-ff finish/phase8-database -m "Complete Phase 8: database layer, File Integrity Lab, documents"
git push origin main
```

## Route 3 - You cannot push (the repository belongs to her account)

Send the commits as a patch or a bundle and let her apply them. No access required.

```bat
REM a patch file - one text file per commit
git format-patch main --stdout > cyberguard-phase8.patch

REM or a bundle - behaves like a small repository
git bundle create cyberguard-phase8.bundle main..finish/phase8-database
```

She runs this in her own clone:

```bat
git am < cyberguard-phase8.patch
REM or
git fetch ../cyberguard-phase8.bundle finish/phase8-database:finish/phase8-database
```

A zip of the project folder also works if she only wants the files: the only items that
must not travel are `.env`, `.venv/`, `backend/vendor/*.h*,json.hpp` and `*.exe`, because
`.gitignore` excludes them and `setup.bat` rebuilds the headers.

## Route 4 - Upload the Word documents through the website

For the seven submission files only, no git knowledge needed:

1. Open the repository and click **Add file -> Upload files**.
2. Drag `CyberGuard_Case_Study_*.docx` and `CyberGuard_Project_Report_*.docx` into `docs/`.
3. Commit message: `Add case studies and project reports`, then **Commit changes**.

---

## If the push asks for a password

GitHub no longer accepts an account password over HTTPS. Use a token:

1. GitHub -> **Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens**.
2. **Generate new token**, choose the repository `CyberGuard`, permission
   **Contents: Read and write**, expiry 7 days.
3. Copy the token once, then paste it when git asks for a **password**
   (the username is your GitHub username).

Windows also ships **Git Credential Manager**, so a small browser window may open instead
and ask you to sign in. That is the easier path - accept it.

## Adding each other to the repository

- Repository -> **Settings -> Collaborators -> Add people**, enter her GitHub username,
  choose **Write**, send the invitation. She accepts from her email or the GitHub bell icon.
- To check what you may do: `git push --dry-run origin finish/phase8-database`.

## Before every push, confirm the right files and no secrets

```bat
git status --short                  REM must not list .env
git check-ignore -v .env            REM confirms .gitignore is doing its job
git diff --stat main..HEAD          REM the exact change set that will be shared
```

## Sharing the documents themselves

The seven Word files live in `docs/` and are in the repository, so she gets them with a
clone or a `git pull`. An identical set, ready to forward, is on your Desktop in
`CyberGuard_Submission\`, together with `CyberGuard_Submission.zip`.
