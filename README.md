# Andreas Lindeman Portfolio

Static portfolio site. No build step, no frameworks. Drop into any static host.

## Structure

```
portfolio/
├── index.html              # landing page (hero, about, timeline, stack, contact)
├── style.css               # all styles, including project-page styles
├── script.js               # timeline rendering, filters, tooltip
├── projects_data/
│   ├── manifest.json       # lists every entry JSON below
│   └── *.json              # one file per timeline entry
└── projects/
    ├── _template.html      # copy this when adding a new deep-dive
    └── *.html              # one file per deep-dive
```

## Deploy on GitHub Pages

1. Push this folder to a repo (e.g. `andreas-lindeman/andreas-lindeman.github.io`,
   or any repo with Pages enabled).
2. In **Settings → Pages**, set source to the `main` branch / root.
3. Done. The site is live at the Pages URL within a minute.

For a custom domain, add a `CNAME` file at the root containing the domain and
point your DNS at GitHub.

## Adding a new timeline entry

1. Create a new JSON file in `projects_data/`, named
   `YYYY-short-slug.json`. Use any existing file as a reference; the schema is:

   ```json
   {
     "id": "unique-id",
     "title": "Display title",
     "category": "work | school | hobby",
     "isProject": true,
     "start": "YYYY"            // or "YYYY-MM"
     "end": "YYYY",             // optional; can also be "YYYY-MM" or "present"
     "shortDescription": "Shown in the tooltip and mobile list.",
     "tags": ["python", "ml"],
     "projectPage": "projects/<slug>",             // optional; clean URL, no .html
     "externalLinks": [                            // optional
       { "label": "GitHub", "url": "https://...", "type": "github" }
     ],
     "status": "nda | lost | ongoing",            // optional
     "statusNote": "Free-form note shown next to the status tag." // optional
   }
   ```

2. Add the filename to `projects_data/manifest.json` so the loader picks it up.
3. (Optional) If `projectPage` is set, copy `projects/_template.html` to that
   path and fill it in.

That's it. No JS to touch, the timeline rebuilds from the JSONs.

## A note on framing

A few items on the timeline come from a chapter of my life where I was a teenager
doing things I'd handle very differently today. The index page uses neutral
framing for those: "first standalone Python program", "self-taught
cybersecurity research", "network systems exploration". The deep-dive pages
behind them are candid about what actually happened, what I learned, and what I
would change. The point of including them is not to brag; it's to show the
trail honestly, and the technical lessons are real.
