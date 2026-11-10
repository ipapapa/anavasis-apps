#!/usr/bin/env python3
"""Builds the ANAVASIS app pages from apps.json.

    python3 -I build.py

For every app: /<slug>/ (support) and /<slug>/privacy/ (privacy policy).
Shared wording lives here once; each app only states its own facts
(ads, AI tutor, purchases, reminders) in apps.json. URLs are folder-style so
they survive a later move to a custom domain. Commit the generated HTML.
"""
import html, json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(ROOT, "apps.json"), encoding="utf-8"))
CO, MAIL = cfg["company"], cfg["contact"]
E = html.escape

def page(title, body, depth, lang="en"):
    css = "../" * depth + "assets/site.css"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<link rel="stylesheet" href="{css}">
</head>
<body>
{body}
<footer>© {E(CO)} · <a href="mailto:{MAIL}">{MAIL}</a></footer>
</body>
</html>
"""

def privacy(a):
    n = E(a["name"])
    s = [f"<h1>{n} — Privacy policy</h1>",
         f'<p class="meta">Last updated: {E(a["updated"])} · {E(CO)} (“we”).</p>',
         "<h2>Summary</h2>",
         f"<p>{n} has no account and no server of ours. Your progress, settings and purchases stay on your device.</p>",
         "<h2>Stored on your device</h2>",
         f"<p>{E(a['stored'])} Deleting the app deletes them. “Reset progress” in the app clears them too.</p>"]
    if a.get("purchases"):
        s += ["<h2>Purchases</h2>",
              "<p>The one-time Pro purchase is handled by Apple (App Store) or Google (Google Play). We never see your payment details.</p>"]
    if a.get("reminders"):
        s += ["<h2>Reminders</h2>",
              "<p>The optional daily reminder is a local notification scheduled on your device. Nothing is sent to us.</p>"]
    ads = a.get("ads", "none")
    if ads == "android":
        s += ["<h2>Ads (Android free version only)</h2>",
              "<p>The free Android version shows ads from Google AdMob. In the EU/UK you are asked for consent through Google’s consent form, and you can change your choice in Settings › Privacy settings. AdMob may use the advertising ID and device information as described in <a href=\"https://policies.google.com/technologies/ads\">Google’s policy</a>. Pro removes ads. The iOS app has no ads and no tracking.</p>"]
    elif ads == "both":
        s += ["<h2>Ads (free version)</h2>",
              "<p>The free version shows ads from Google AdMob. In the EU/UK you are asked for consent first, and you can change your choice in Settings. AdMob may use the advertising ID and device information as described in <a href=\"https://policies.google.com/technologies/ads\">Google’s policy</a>. Pro removes ads.</p>"]
    else:
        s += ["<h2>Ads and tracking</h2>", "<p>The app has no ads and no tracking.</p>"]
    if a.get("ai_tutor"):
        s += ["<h2>AI tutor (when available)</h2>",
              "<p>If the AI tutor is enabled, the messages you type to it (and the question you ask about) are sent to Google’s Gemini models through Firebase to produce an answer. They are not linked to your identity by us and are not used for tracking. Firebase App Check verifies that requests come from the genuine app. Do not type personal information into the tutor.</p>"]
    s += ["<h2>Children</h2>",
          f"<p>The app is meant for {E(a['audience'])} and does not knowingly collect data from children.</p>",
          "<h2>Changes</h2>",
          "<p>If this policy changes, we update this page and the date above.</p>",
          "<h2>Contact</h2>",
          f'<p><a href="mailto:{MAIL}">{MAIL}</a></p>']
    if a.get("disclaimer"):
        s.append(f'<p class="note">{E(a["disclaimer"])}</p>')
    return page(f"{a['name']} — Privacy", "\n".join(s), 2)

def support(a):
    n = E(a["name"])
    s = [f"<h1>{n}</h1>", f"<p>{E(a['tagline'])}</p>",
         "<h2>Soporte · Support</h2>" if a.get("lang") == "es" else "<h2>Support</h2>",
         f'<p><a href="mailto:{MAIL}">{MAIL}</a></p>',
         a.get("support_html", "")]
    if a.get("disclaimer"):
        s.append(f'<p class="note">{E(a["disclaimer"])}</p>')
    s.append('<p><a href="privacy/">Privacy policy</a></p>')
    return page(f"{a['name']} — Support", "\n".join(x for x in s if x), 1, a.get("lang", "en"))

def write(rel, text):
    path = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)

items = []
for a in cfg["apps"]:
    write(f"{a['slug']}/index.html", support(a))
    write(f"{a['slug']}/privacy/index.html", privacy(a))
    items.append(f'<li><a href="{a["slug"]}/">{E(a["name"])}</a> · <a href="{a["slug"]}/privacy/">Privacy</a></li>')
write("index.html", page(f"{CO} apps", f"<h1>{E(CO)} apps</h1>\n<ul class=\"apps\">\n" + "\n".join(items) + "\n</ul>", 0))
print("built", len(items), "app(s)")
