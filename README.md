# Thursday Cookie Lab Signup

A signup page for the **Learn to Bake Cookies Club**, which meets on Thursdays in the Great Hall.
Students pick a Thursday and one of three baking sessions:

- Chocolate Chip Cookies (3:00 PM)
- Sugar Cookies (4:00 PM)
- Oatmeal Cookies (5:00 PM)

## Features

- **Sign up** with a name, a Thursday (the next four, starting this week) and a session
- **Clear error messages** for a missing name, Thursday or session, with the other choices kept
- **Prevent duplicate signups** (same name, Thursday and session)
- **Switch activities** by signing up again with a different session on the same Thursday
- **Cancel a signup** by entering your name, Thursday and session, then pressing *Cancel My Signup*
- **Limit available spots** to 10 per session, with "spots left" and *Full* shown on each choice
- **Roster** that stays hidden until you search for a name or choose Thursdays
  - **Count by activity** (for example, *3 of 10 spots*)
  - **Names sorted A–Z**
  - **Search past sessions**
- **Mark attendance** on Thursdays that have happened (club leaders only)
- Keyboard friendly, screen-reader labels, and a layout that works on phones
- Cookie-themed design: cookie session buttons, scattered baking drawings and a rolling-pin cursor

## Try it

Open `index.html` in a web browser. No install or build step is needed.

When the page is opened straight from a file, signups are kept only until the page is closed.
Saved signups, the shared roster and attendance work when the page is published as a Claude artifact,
which provides the database the page uses.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole website: layout, styles, drawings and code in one file |
| `design.md` | The original design written for the class assignment, before the extra features were added |
