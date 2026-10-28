---
name: rich-doc
description: Write a rich doc—a Markdown document for one reader to review, leading with what they must decide or know, with diagrams, tables, screenshots and at most one live widget. Use when asked for a briefing on a person, organisation, project or decision, a primer or explainer on a topic, or a plan for the reader's review; to prepare the ground for a message or meeting; or to add a TL;DR, visuals or a decision box to an existing document.
---

# Rich doc

A rich doc exists so its reader (the person asking) can decide, act or understand quickly. Lead with what they must decide or know, show structure as pictures, show sources as screenshots, and keep the full evidence trail below. Markdown is the format; the reader's review tool is where they read it.



## Steps

### Before starting: check for updates

If `scripts/check-update.sh` exists in this skill's folder, run
`bash <this skill's folder>/scripts/check-update.sh` from the user's project
folder. It checks at most once a day and prints nothing when the skill is
current.

- **It reports an update:** run it with `--diff` and read the code changes.
  Show the user the release notes and a short summary of the changes, flagging
  anything the notes do not explain. Ask whether to update now, update now and
  automatically from now on, or not now. For the first run it with `--apply`;
  for the second run it with `--enable-auto`, then `--apply`; for the third
  carry on.
- **It reports an automatic update:** run it with `--diff` and read the
  changes. If they match the release notes and do nothing risky, run it with
  `--apply` and tell the user in one line. Otherwise show the user your
  concerns and ask.
- **After `--apply` succeeds:** re-read this SKILL.md before continuing.
- **It reports a migration conflict:** show the user the conflicting files
  and wait for them to choose which version to keep.

### Writing the doc

1. **Gather.** Follow the project's sourcing rules (for example: primary sources read this session, every claim linked). Fan research out to subagents and keep their access logs. Done when every fact the doc will state has a source you or a subagent read this session.

2. **Find the shape.** Before writing, list:
   - the **decisions** the reader must make, each with your recommendation and a one-line reason (a primer may have none);
   - the one **structure** that explains the situation (a pipeline, a comparison design, who-reports-to-whom, what a plan changes), if there is one, and what in it is missing, broken or new;
   - the **visual sources**: pages, charts or UIs whose look carries evidence;
   - things compared across the same attributes (→ tables);
   - dated events (→ a timeline when there are five or more).

3. **Write the Markdown** in the order for its kind (see "Kinds of doc").

4. **Make the images** (see "Images"). Done when every image is rendered, looked at once, and any overlap or clipping fixed in one pass.

5. **Open it** in the reader's review tool (for example, `roughdraft open <absolute path>`). In the reply, give the path, the decisions or key points in brief, and anything unverified.

The doc is done when every decision has a recommendation and a reason, every claim keeps its link, and every image has been looked at.

## Kinds of doc

All three kinds start with front matter, a title and one paragraph on purpose and on what has or hasn't been sent or done. All three end with **What rests on inference**: every claim that rests on a summary, memory, inference or a source not read.

**Briefing** (on a person, organisation, project or decision, often before a message or meeting):
1. **Decision box**: an `[!IMPORTANT]` callout holding a table of decision · recommendation · why. Add any quick check the reader should do first.
2. **Whole-picture diagram**, with a caption saying what the dashed and tinted parts mean and a line citing its sources.
3. The body sections, in the order the reader needs them.
4. Any draft (message, email, agenda) as a blockquote, followed by the choices made in it that the reader may want to change.

**Primer** (explaining a topic, tool or field so the reader can work with it):
1. **Key points**: three to five lines the reader should leave with, as a `[!NOTE]` callout. A decision box only if the primer ends in a choice.
2. **The one diagram** of how the thing works or fits together.
3. The body, from the general to the particular, with tables for comparisons and a glossary when there are more than a handful of new terms.
4. **Where to go next**: the best two or three sources, each with a line on why.

**Plan** (for the reader's review):
1. **TL;DR** of three to five lines: what changes, what doesn't, and what the plan needs from the reader.
2. **Decision box**. Once the reader has answered, record each answer in it rather than deleting the row.
3. **Before-and-after diagram** of the structure the plan changes, with new parts dashed in the accent colour and changed parts tinted. If the order of steps carries risk (a cutover, a migration, a launch), add a sequence diagram of those steps.
4. The body: what exists now, the design, phases, risks, then any draft as a blockquote.

Plans and primers rarely need screenshots or a timeline. Use them only when the doc turns on a UI's look or on five or more dates.

## Elements

- **Callouts:** GitHub alerts, with the marker alone on the first line and a bold lead-in on the next:
  ```markdown
  > [!WARNING]
  > **The design gap.** Our judge removes the weakest ideas before the reader sees anything…
  ```
  `[!IMPORTANT]` for the decision box, `[!WARNING]` for a gap or risk, `[!TIP]` for a shortcut or a constraint that turns out not to bind, `[!NOTE]` for key points or context that changes how to read a section, `[!CAUTION]` for something irreversible. Roughdraft and GitHub both render them.
- **Tables:** for anything compared across the same attributes (people, products, options, who rates what). Keep a source column or cite under the table.
- **Screenshots:** for a source whose look is the evidence: a chart, a landing page, a UI, a published claim. Crop to the part that matters, and caption it with the URL and capture date. Check every subagent's description of a visual against the screenshot; descriptions of charts are often wrong.
- **Diagrams:** for structure. Mark what doesn't exist yet (dashed, accent outline) and what is broken or changed (tinted fill), since the gap is usually the point. Draw only where there is structure; a decorative diagram is padding. Two ways to draw one:
  - **A ` ```mermaid ` fence** for most diagrams: flowcharts, sequences, small org charts. It stays text, so the reader can comment on it and suggest edits, and git diffs stay readable. Roughdraft and GitHub draw it, with the source folded underneath. Use `classDef` for the new, changed and broken kinds. Avoid semicolons in labels and messages: Mermaid reads them as statement breaks.
  - **Hand-written SVG** (see "Images") for the one whole-picture diagram, when its layout carries the argument and Mermaid's automatic layout would muddle it.
- **Timeline:** for five or more dated events, drawn to scale as SVG (Mermaid's `timeline` isn't to scale), with the events that matter for the decision filled in the accent colour.
- **Quotes:** a pull-quote when one sentence from a source carries the case.
- **Illustrations:** none unless the reader asks. A generated image carries no information and pushes the decisions down.

## Images

Put images in `assets/` beside the Markdown file, with descriptive names, and reference them relatively (`![alt](assets/name.svg)`). Roughdraft serves only paths in or below the document's folder, so `../` image paths come up blank.

`scripts/visual.py` in this skill's folder (run with `python3 -I`; it needs Pillow, and Google Chrome or `$CHROME`) does the mechanical work through headless Chrome:

```bash
python3 -I <skill>/scripts/visual.py shot <url> <out.png> [--width 1280] [--height 1100] [--crop x,y,w,h]
python3 -I <skill>/scripts/visual.py svg <in.svg> [--scale 2]   # writes <in>.png beside it
```

For a diagram, start from `assets/diagram-template.svg` in this skill: its comments give the palette, box kinds and arrow markers. Embed the SVG itself; Roughdraft renders it. An SVG shown as an image loads no web fonts and ignores dark mode, so keep the template's system-font stack and its own background rectangle. Use `visual.py svg` only to get a PNG you can look at: hand-written SVG takes one look and usually one fix (labels colliding with curves are the common fault).

Use the template's palette, or swap in your organisation's colours and keep the roles. The same hex values work in Mermaid `classDef` lines.

## Interactive parts

When the doc ends in an action the reader takes from it (sending a message, choosing among options), make that part a live widget inside the Markdown: a ` ```html live ` fence, which Roughdraft runs in a sandboxed frame sized to its content. The decisions drive the output; for example, choices that rewrite the draft message as the reader picks them. Everything else stays Markdown, so it can still be commented on and diffed.

- **Self-contained:** the frame has no network, so inline all CSS and JS and use `data:` URIs for images. No web fonts; use a system-font stack.
- **No clipboard API** (the sandbox allows scripts only): put the output in a read-only `<textarea>` with a "Select all" button, and let the reader copy it.
- **Readable without it:** GitHub and other viewers show the fence as code, so give the default output as plain Markdown too (the draft message as a blockquote below the widget).
- **Small:** one widget per doc, for the one action.

A full standalone HTML page is for when the reader asks for one: load `artifact-design` first, and keep it a local file when it holds candid views about people or organisations.
