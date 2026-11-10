# ANAVASIS app pages

Support and privacy pages for ANAVASIS LLC apps, served by GitHub Pages:
`https://ipapapa.github.io/anavasis-apps/<app>/` and `…/<app>/privacy/`.

- Add an app: add an entry to `apps.json` (its own facts: ads, AI tutor, purchases,
  reminders), run `python3 -I build.py`, commit the generated HTML.
- Shared wording lives once in `build.py`; every app's page updates from it.
- URLs are folder-style so a later custom domain keeps the same paths.
- Never rename the repo or move a page: the URLs are built into apps and store listings.
