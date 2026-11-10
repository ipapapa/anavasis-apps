#!/usr/bin/env python3
"""Builds the ANAVASIS app pages from apps.json.

    python3 -I build.py

For every app: /<slug>/ (support) and /<slug>/privacy/ (privacy policy).
The policy wording lives here once; each app states only its own facts in
apps.json:
  ads        "none" | "android" (free Android only) | "both" (free tier on both)
  pro        {name, unlocks}            one-time purchase, omit if none
  ai         {feature, sent, note?}     Firebase AI Logic → Gemini, omit if none
  remote_config  feature flags from Firebase Remote Config (installation ID)
  reminders  local daily reminder       ratings  in-app review prompt
URLs are folder-style so a later custom domain keeps the same paths.
Keep each app's facts true to its code: reviewers compare.
"""
import html, json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(ROOT, "apps.json"), encoding="utf-8"))
CO, MAIL = cfg["company"], cfg["contact"]
E = html.escape
MAILTO = f'<a href="mailto:{MAIL}">{MAIL}</a>'
G_ADS = '<a href="https://policies.google.com/technologies/partner-sites">How Google uses information from sites or apps that use its services</a>'
G_PRIV = '<a href="https://policies.google.com/privacy">Google Privacy Policy</a>'

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
<footer>© {E(CO)} · {MAILTO}</footer>
</body>
</html>
"""

def privacy(a):
    n, full = E(a["name"]), E(a.get("full_name", a["name"]))
    ads, pro, ai = a.get("ads", "none"), a.get("pro"), a.get("ai")
    sec = []          # (title, html)
    glance = []       # (information, goes to, why)

    short = ["No account, no sign-up, no email collection. Your study progress stays on your device."]
    if ads == "android":
        short.append("The iPhone app shows no ads, contains no advertising SDK and never asks to track you. "
                     f"The free Android app shows ads from Google AdMob; {E(pro['name']) if pro else 'Pro'} removes them.")
    elif ads == "both":
        short.append(f"The free version shows ads from Google AdMob; {E(pro['name']) if pro else 'Pro'} removes them.")
    else:
        short.append("The app shows no ads, contains no advertising SDK and never asks to track you.")
    if ai:
        short.append(f"When you use {E(ai['feature'])}, the text needed to answer you is sent to Google’s Gemini models through Firebase.")
    short.append("We never sell your personal information and we don’t run any server that receives information from the app.")

    sec.append(("Information stored on your device",
        f"<p>{E(a['stored'])} are stored only on your device. We cannot see them. Deleting the app deletes them, and "
        "“Reset progress” in the app clears them. If you have turned on your device’s own backups (for example iCloud Backup "
        "or Android/Google backup), this data may be included in those backups, which are controlled by Apple or Google and "
        "you — never by us.</p>"))
    glance.append(("Study progress and settings", "Stays on your device", "Your progress and your answers"))

    if ads in ("android", "both"):
        where = "free Android version only" if ads == "android" else "free version only"
        ios = ("<p><strong>iPhone:</strong> the iPhone app shows no ads and contains no advertising SDK. It does not use the "
               "advertising identifier (IDFA), does not ask for tracking permission, and no ad-related data is collected or "
               "shared.</p>") if ads == "android" else ""
        who = "the free Android version" if ads == "android" else "the free version"
        sec.append((f"Advertising ({where})", ios +
            f"<p><strong>{'Android' if ads == 'android' else 'Free version'}:</strong> {who} shows ads served by Google AdMob, "
            "a service of Google LLC: banner ads on some screens and, at natural break points (for example after a practice "
            "session or a mock exam), an occasional full-screen ad. To serve, measure and limit ads and to prevent fraud, "
            "Google’s ads SDK may collect and use your device’s advertising ID (subject to your device settings), approximate "
            "location derived from your IP address, device and app information, and ad interaction data. Google’s use of this "
            f"data is described in the {G_PRIV} and at {G_ADS}.</p>"
            f"<p>Where the law requires it (for example in the EU/EEA and the UK), {who} shows Google’s consent form "
            "(User Messaging Platform) and requests ads only after that step. You can consent, refuse or manage the individual "
            "purposes, and change your choice at any time in the app’s Settings → Ad privacy options. If you decline "
            "personalisation you still see ads, but they are not personalised. You can also reset or delete your advertising "
            "ID in your device settings.</p>"
            + (f"<p>With {E(pro['name'])}, the app requests and shows no ads.</p>" if pro else "")))
        glance.append(("Advertising ID, device and ad interaction data (" + where + ")", "Google AdMob",
                       "Showing, measuring and limiting ads"))

    if pro:
        sec.append((f"{E(pro['name'])} (optional purchase)",
            f"<p>{E(pro['name'])} is an optional one-time purchase that unlocks {E(pro['unlocks'])}. It is processed entirely by "
            "Apple (App Store) on iPhone or Google (Google Play) on Android. We never see your name, payment card or billing "
            "details; the app only receives confirmation from Apple or Google that Pro is unlocked, so it can enable the "
            "features and restore your purchase." + (" On Android, Pro also removes all ads." if ads == "android" else
            " Pro also removes all ads." if ads == "both" else "") + "</p>"))
        glance.append((f"Purchase of {E(pro['name'])}", "Apple or Google", "Payment and unlocking Pro"))

    if ai:
        sec.append((f"{E(ai['feature'][0].upper() + ai['feature'][1:])} (Google Gemini via Firebase)",
            f"<p>When you use {E(ai['feature'])}, the app sends {E(ai['sent'])} to Google’s Gemini models through Firebase AI "
            "Logic, a Google service, to produce a reply. No name, email or account identifier is sent, because the app has "
            "none; as with any internet request, Google receives your device’s IP address. Firebase App Check confirms that "
            "requests come from the genuine app, using Apple App Attest or Google Play Integrity; this does not identify you. "
            f"Google processes this data under the Firebase and Gemini terms and the {G_PRIV}. Please don’t type personal "
            "information into it. " + E(ai.get("note", "")) + "</p>"))
        glance.append(("Text you send to " + E(ai["feature"]), "Google (Firebase AI Logic, Gemini)", "Producing the reply"))

    if a.get("remote_config"):
        sec.append(("App settings (Firebase Remote Config)",
            "<p>When the app starts it may download its feature settings (for example whether an optional feature is "
            "switched on) from Google’s Firebase Remote Config. To do this, Firebase creates a random installation ID for the "
            "app on your device. It is not linked to your name, email or advertising ID, and contains none of your study data. "
            f"Google processes it under the Firebase terms and the {G_PRIV}.</p>"))
        glance.append(("Random Firebase installation ID", "Google (Firebase Remote Config)", "Delivering the app’s feature settings"))

    if a.get("reminders"):
        sec.append(("Reminders",
            "<p>The optional daily study reminder is a local notification scheduled on your device, with your permission. "
            "Nothing is sent to us, and you can turn it off in the app or in your device settings.</p>"))
    if a.get("ratings"):
        sec.append(("Ratings",
            "<p>After some use the app may ask Apple’s or Google’s in-app review prompt to appear. Ratings and reviews are "
            "handled entirely by Apple or Google; we receive only the public reviews you choose to post.</p>"))

    third = ["Apple’s and Google’s own purchase and review frameworks"]
    if a.get("remote_config"): third.insert(0, "Google’s Firebase Remote Config (app settings)")
    if ai: third.insert(0, "Google’s Firebase AI Logic and App Check (" + E(ai["feature"]) + ")")
    if ads == "android": third.insert(0, "Google AdMob and Google’s consent form in the free Android version only")
    if ads == "both": third.insert(0, "Google AdMob and Google’s consent form in the free version")
    sec.append(("What we don’t do", "<ul><li>No accounts, sign-in or email collection.</li>"
        "<li>No selling of personal information.</li><li>No access to your location, contacts, photos or files.</li>"
        "<li>No analytics SDKs and no data brokers. The third-party services the app uses are: " + "; ".join(third) + ".</li>"
        "<li>No servers of ours that receive information from the app.</li></ul>"))

    rows = "".join(f"<tr><td>{i}</td><td>{g}</td><td>{w}</td></tr>" for i, g, w in glance)
    sec.append(("Information at a glance",
        f"<table><thead><tr><th>Information</th><th>Goes to</th><th>Why</th></tr></thead><tbody>{rows}</tbody></table>"))

    sec.append(("Children",
        f"<p>{n} is a study tool for {E(a['audience'])}. It is not directed at children under 13 (under 16 in the EU), and we "
        "do not knowingly collect personal information from children. If you believe a child has provided personal "
        "information through the app, contact us and we will help.</p>"))
    sec.append(("Your choices and rights",
        "<ul>" + ("<li>Ads: change your consent in Settings → Ad privacy options, or remove ads with Pro.</li>" if ads != "none" else "")
        + (f"<li>AI: {E(ai['feature'])} is optional; don’t use it if you prefer not to send text to Google.</li>" if ai else "")
        + "<li>Delete everything: delete the app — your study data lives only on your device.</li></ul>"
        "<p>Depending on where you live (for example in the EU/EEA, the UK or certain U.S. states), you may have rights to "
        "access, delete or correct personal information, to object to processing and to withdraw consent. Because we hold no "
        "personal information about you on our side, most requests are best handled through the controls above and through "
        "Apple’s and Google’s own tools; you can also contact us and we will help.</p>"))
    sec.append(("Security and retention",
        "<p>All of the app’s network requests use encrypted HTTPS connections. Data on your device stays until you delete it "
        "or the app. Data received by Google or Apple is retained according to their policies.</p>"))
    sec.append(("This page",
        "<p>This page uses no cookies, analytics or tracking scripts. It is hosted on GitHub Pages, which processes standard "
        "server logs (such as IP address) to deliver and secure the site.</p>"))
    sec.append(("Changes to this policy", "<p>If we change this policy, we will update this page and the effective date above.</p>"))
    sec.append(("Contact", f"<p>{E(CO)} — {MAILTO}</p>"))

    body = [f"<h1>{n} — Privacy policy</h1>",
            f'<p class="meta">Effective date: {E(a["effective"])} · Applies to {E(a["applies"])}.</p>',
            f"<p>{full} (“{n}”, “the app”) is made by {E(CO)} (“we”, “us”). This policy explains, in plain language, what the "
            "app does with information.</p>",
            "<h2>The short version</h2><ul>" + "".join(f"<li>{s}</li>" for s in short) + "</ul>"]
    for i, (t, h) in enumerate(sec, 1):
        body.append(f"<h2>{i}. {t}</h2>\n{h}")
    if a.get("authority"):
        body.append(f'<p class="note">{n} is an independent study aid. It is not affiliated with, endorsed by, or connected to '
                    f'{E(a["authority"])}. {E(a.get("source_note", ""))}</p>')
    return page(f"{a['name']} — Privacy policy", "\n".join(body), 2)

def support(a):
    n = E(a["name"])
    s = [f"<h1>{n}</h1>", f"<p>{E(a['tagline'])}</p>",
         "<h2>Soporte · Support</h2>" if a.get("lang") == "es" else "<h2>Support</h2>",
         f"<p>{MAILTO}</p>", a.get("support_html", "")]
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
