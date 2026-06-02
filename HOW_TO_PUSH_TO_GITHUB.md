# How to put this project on GitHub (first-timer steps)

You only need a handful of commands. Do them in order. Plain meaning is in brackets.

## One-time setup (skip if you already did it)

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```
[Tell Git who you are. Use the email you signed up to GitHub with.]

## Step 1: Make the repo on GitHub's website

1. Log in to github.com.
2. Click the green "New" button.
3. Name it: pcos-clinical-classifier
4. Leave it empty (do NOT add a README there, you already have one here).
5. Click "Create repository".
6. Copy the HTTPS link it shows you (ends in .git).

## Step 2: Turn this folder into a Git repo and upload it

Open a terminal inside this project folder, then run these one at a time:

```bash
git init
```
[Start tracking this folder with Git.]

```bash
git add .
```
[Stage everything for the first snapshot. The .gitignore keeps data files out.]

```bash
git commit -m "Initial commit: honest PCOS clinical classifier starter"
```
[Take the snapshot, with a note.]

```bash
git branch -M main
```
[Name the main line of work "main", the modern default.]

```bash
git remote add origin <paste-the-link-you-copied>
```
[Tell Git where online this should live.]

```bash
git push -u origin main
```
[Upload it to GitHub. Refresh the GitHub page and your files should be there.]

## Everyday loop after that

Whenever you change something:

```bash
git add .
git commit -m "short note about what you changed"
git push
```

That is it. add, commit, push. Forever.

## One safety habit

Before you start work on another machine, or after time has passed:

```bash
git pull
```
[Pull down the latest version first, so you do not clash with past changes.]
