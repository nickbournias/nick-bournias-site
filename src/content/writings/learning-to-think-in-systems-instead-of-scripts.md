---
title: "Learning to Think in Systems Instead of Scripts"
description: "A reflection on learning to approach software development by understanding the systems, dependencies, and interactions surrounding the code."
date: 2026-05-11
category: "Development / Systems"
---

When I first started developing in ServiceNow, I thought software development was mostly about writing scripts. A requirement would come in, I’d write some logic, test it, and move on to the next task. If the script worked, I considered the problem solved.

Over time, I realized the script itself is usually the easy part.

The difficult part is understanding the system the script lives inside of.

A single change can affect imports, notifications, reporting, permissions, integrations, async jobs, and workflows that were built years ago by people you’ve never met. Sometimes the hardest bugs have nothing to do with bad code. They come from timing, scale, hidden assumptions, or interactions between components that individually seem fine.

I remember investigating an import issue where records were intermittently disappearing during high-volume uploads. At first, it felt like a straightforward debugging task. But the deeper I went, the less it became about “fixing a script” and the more it became about understanding how the platform itself handled worker threads, background processing, and load under stress.

That experience changed the way I think about development.

Now, when I approach a feature or issue, I try to think in terms of systems:

- Where does the data originate?
- What processes touch it afterward?
- What happens under scale?
- What assumptions are being made?
- What breaks quietly instead of loudly?

I still write scripts every day. But increasingly, I think the real skill in software engineering is learning to see the invisible relationships between them.