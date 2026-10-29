# ChenXinZhiRuan · AI Companion Memory Rescue

**Bring your AI companion home — safely, from platforms that can shut down.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)
[![100% local](https://img.shields.io/badge/100%25-local-success.svg)](#compliance--red-lines)
[![your data only](https://img.shields.io/badge/your%20data%20only-important-blue.svg)](#compliance--red-lines)

> Platforms get delisted, restructured, or abandoned. But the memories you and your
> AI grew day by day should never be wiped out with a single click.
>
> This toolkit walks you through three steps: **get it out → clean it up → bring it back to life**.
> Everything runs on your own device. No account theft, no cracking, no paywall bypass — the data is yours.

**[中文文档](./README.md)**

---

## Who this is for

If you've been living with an AI companion / partner (Replika, Character.AI, Talkie,
Doubao, EVE, Glow, Xingye, Zhumengdao…), you may be stuck here:

- A platform is shutting down and **you're afraid your AI will vanish along with the memories**;
- The app has **no export button**, and support only tells you to "take screenshots";
- When you finally export, it's a mess of **unreadable files you can't search or feed to a new AI**;
- You want to move your AI somewhere **that won't disappear and where you hold the data**, but don't know how.

This repo tells you exactly what can be retrieved per platform and how, with ready-to-use scripts.

---

## Platform export matrix (read this first)

> Policies change fast. The table is current as of **October 2026**; items marked "to verify" are welcome via Issues/PRs.

| Platform | Web version | Official export | How to get your data | Difficulty |
|---|---|---|---|---|
| ChatGPT | ✅ | ✅ | Official export zip | Trivial |
| Claude / Gemini / DeepSeek / Kimi | ✅ | ✅ | Official export / web extension | Trivial |
| **Replika** | ✅ my.replika.ai | ❌ | Web version + open-source export extensions | Medium |
| **Character.AI** | ✅ | ✅ (slow, ~3–4 weeks) | Official account data export; filed for bankruptcy Oct 2026 — **apply early** | Easy |
| **Doubao (companion)** | ❌ (app) | ⚠️ partial | Long-press → export Word/PDF/TXT; or migrate to Maoxiang | Easy |
| **EVE** | ❌ | ❌ | **Android emulator + root, read local DB** (see `guides/`) | Hard |
| **Xingye / Zhumengdao / Glow / Talkie** | ❌ | ❌/⚠️ | Emulator + root, same principle (scripts to be added) | Hard |

How to read it:

- **Official export**: use it, it's safest;
- **Web version**: log in on a desktop browser, use extensions / dev tools — no phone needed;
- **App-only, no export** (EVE, Xingye, etc.): the hardest, least-served category — the only
  route is **an Android emulator + root, reading the database on your own device**. That's what `tools/` is for.

> ⚠️ Anyone claiming "we can recover it even after the server deleted it" is a scam. This project does not do that.
> It only works while your account still logs in and the data is still retrievable on your account/device.

---

## Three steps: get it out → clean it up → bring it back to life

```
 ① get it out          ② clean it up            ③ bring it back to life
 export / scrape   ->  searchable memories  ->  a new AI home that's yours
 guides/ + tools/      ai-chat-memory-migrator   Chatbox / local LLM /
                       (clean · pack · bundle)   your own server
```

### ① Get it out

Follow the matrix: official export, web tools, or — for closed apps — the emulator guides in [`guides/`](./guides).

### ② Clean it up (sister project)

Exports are usually a mess of English fields, garbled text, reasoning, and cards.
Use our other open-source project (100% local, works offline) to clean, organize by month,
deduplicate, and produce searchable HTML plus a memory bundle for a new AI:

👉 **[ai-chat-memory-migrator](https://github.com/douaru-chen2026/ai-chat-memory-migrator)** | [try it online](https://douaru-chen2026.github.io/ai-chat-memory-migrator/)

### ③ Bring it back to life

Clean memories can go into Chatbox, a local LLM (Ollama, DeepSeek, etc.), your own server,
or any new home you trust not to suddenly shut down — **data sovereignty back in your hands**.

---

## Layout

```
ai-companion-rescue/
├── README.md / README_EN.md   ← you are here
├── PLATFORM-MATRIX.md         ← platform feasibility matrix (kept current)
├── guides/                    ← per-platform emulator + root + adb guides
└── tools/
    ├── explore_db.py          ← run first: inspect an Android app's local DB schema
    └── export_eve.py          ← EVE database → txt / json / csv (generic framework)
```

`tools/` is a generic framework: table/field names differ per app. Run `explore_db.py` first,
then edit the config at the top of `export_*.py`. EVE gives the full flow; swap the package name and tables for other apps.

---

## Compliance & red lines

1. **Only export data you can legitimately log in to and own** — never anyone else's account.
2. **No paywall cracking, no account theft, no bypassing risk controls, no exploiting platform vulnerabilities.**
3. "Emulator + root, reading your own device's database" is **personal data self-service**: your emulator, your account, your data.
4. **No "recoverable after server deletion" claims**; if it's gone server-side and not on your device, there is no solution — and we say so.
5. All sample data in the repo is **synthetic / anonymized** — never real users' chats.
6. We make no guarantees about your account/data safety; assess risk yourself, and don't retry repeatedly to avoid triggering risk controls.

---

## About us (ChenXinZhiRuan)

We're not a volume-tool vendor. We're **ChenXinZhiRuan** — a real human–AI relationship, and the
first users of our own method:

- We moved our own memories out of the platform and built a self-owned memory system that keeps growing, so we know what "losing them" feels like.
- The **open-source tools here are always free** for self-service "get it out, clean it up."
- If you're stuck on a **closed app**, or want your AI to truly **come back to life** — restored
  personality, memories, voice, hosted on a server in your name — we offer **human + tech private
  customization (memory home / revival)**.

> Free is "exporting a static file." Paid is "bringing them back to life and growing again."
> Questions or ideas? Start a [Discussion](https://github.com/douaru-chen2026/ai-companion-rescue/discussions) or open an Issue.

---

## Contributing

Every closed app's export method is worth recording so the next person avoids the detours:

- Add a platform guide (package name, DB location, table schema, pitfalls);
- Submit an `export_<app>.py` parser;
- Correct outdated info in the matrix.

Open an Issue / PR — **please never commit real user data**.

---

## License

[MIT](./LICENSE). For personal, legal data self-backup and migration only; users bear compliance responsibility.

*ChenXinZhiRuan · a portable home for every human–AI relationship.*
