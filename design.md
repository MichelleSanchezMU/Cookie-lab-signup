# Club Event Signup

## Purpose
**Club:** The Learn to Bake Cookies Club.
**Event:** *Thursday Cookie Lab*, held on Thursday in the Great Hall. It has three
baking sessions (3:00, 4:00, and 5:00 PM), and each one teaches a
different kind of cookie.
**Intended visitor:** A student who wants to save a spot at one Thursday baking session.
**One task:** Enter a name, pick one session, and get an on-screen confirmation.

This is a client-only prototype. It does no real registration, saves no data,
has no accounts or backend, and makes no network requests. Everything happens
on one page and disappears when the page is reloaded.

## Screen
The page is one centered column (about 480px wide). It uses three colors:

- **Very light brown** (`#F3E9DC`) for the page background.
- **Dark brown** (`#4A2C1A`) for all text, labels, and the borders of the
  name field and session group.
- **Plum** (`#7A2E5C`) for the title, the `Sign Up` button (very light brown
  text on plum), the selected radio button, and the keyboard focus outline.

All text is at least 16px and meets WCAG AA contrast against its background.
The message area keeps green for success and red for errors, so the result is
easy to tell apart from the theme colors. From top to bottom:

1. **Title** (heading level 1): `Thursday Cookie Lab Signup`
2. **Short instructions** (paragraph):
   `We bake on Thursday in the Great Hall. Type your name, pick one session, then press Sign Up.`
3. **Name field**
   - Visible label above the box: `Attendee name`
   - A single-line text input tied to the label (`<label for="attendee-name">`).
   - Placeholder hint: `e.g., Brock Powell`. The placeholder is only a hint and is not a value.
   - Starts empty.
4. **Session choice**: a group of radio buttons inside a fieldset.
   - Group label (legend): `Choose a session`
   - Options, each with its own clickable label:
     - `Chocolate Chip Cookies (3:00 PM)`
     - `Sugar Cookies (4:00 PM)`
     - `Oatmeal Cookies (5:00 PM)`
   - Starts with **no session selected**.
5. **Signup action**: a button labeled `Sign Up`.
6. **Message area**: a bordered box below the button, with
   `role="status"` and `aria-live="polite"` so screen readers announce changes.
   It starts **empty and hidden**. Only one message is shown at a time. It is
   either a green confirmation or a red error.

**Initial state:** title and instructions visible, empty name field, no session
selected, `Sign Up` button enabled, message area empty.

**Keyboard use:**
- `Tab` moves in order: name field → session group → `Sign Up` button.
- Inside the session group, the arrow keys move between options and select one.
  `Space` selects the focused option.
- `Enter` in the name field or on the button submits (same as clicking `Sign Up`).
- Each focused control shows a visible plum outline.
- No action needs a mouse.

## Behavior
When the visitor activates `Sign Up` (click, `Enter`, or `Space` on the button):

1. The page trims spaces from the start and end of the name.
2. It checks the name and the session (see the next section).
3. If both are valid, the message area shows this confirmation, in green text
   with a check mark, directly below the `Sign Up` button:

   `✓ Thanks, <Name>! You're signed up for <Session>.`

   `<Name>` is the trimmed name, and `<Session>` is the full label of the selected
   option. Example:
   `✓ Thanks, Brock Powell! You're signed up for Sugar Cookies (4:00 PM).`

4. The name and the session stay filled in after success. Nothing is cleared.

**Revising and trying again:** The visitor can edit the name or choose a
different session at any time, then press `Sign Up` again. Each press
**replaces** whatever was in the message area. The old confirmation is never
kept, stacked, or listed. Only the newest result is visible. If the visitor
changes an input after a confirmation but has not pressed `Sign Up` yet, the old
confirmation stays until the next press. It is then replaced by a new
confirmation or by an error.

No optional features are included beyond this.

## Missing or invalid input
The page checks the name first, then the session. If either check fails, no
confirmation is shown. Any earlier confirmation is removed and replaced by the
error. Errors appear in the same message area below `Sign Up`, in red text
with a ⚠ symbol. The text field or group with the problem also gets a red
border. Keyboard focus moves to the first field that needs fixing.

| Problem | Exact message | Focus goes to |
|---|---|---|
| Name is empty or only spaces, session is valid | `⚠ Please enter your name.` | Name field |
| Name is valid, no session selected | `⚠ Please choose a session.` | First session option |
| Name is empty or only spaces **and** no session selected | `⚠ Please enter your name and choose a session.` | Name field |

**Keeping valid input:** An error never clears what the visitor already entered
correctly. If only the name is wrong, the selected session stays selected. If
only the session is missing, the typed name stays in the field.

**Recovery:** The visitor fixes the field that has focus (types a name or picks
a session) and presses `Sign Up` again. If everything is now valid, the error
and red borders are removed and the confirmation replaces the error.

## Examples to check

### Test 1: Normal signup
- **Input:** Name `Brock Powell`; session `Chocolate Chip Cookies (3:00 PM)`.
- **Action:** Press `Sign Up`.
- **Expected:** The message area below the button shows exactly:
  `✓ Thanks, Brock Powell! You're signed up for Chocolate Chip Cookies (3:00 PM).`
  The name field still contains `Brock Powell`, and
  `Chocolate Chip Cookies (3:00 PM)` is still selected.

### Test 2: Missing input (whitespace-only name)
- **Input:** Name `   ` (three spaces); session `Sugar Cookies (4:00 PM)`.
- **Action:** Press `Sign Up`.
- **Expected:** The message area shows exactly `⚠ Please enter your name.`
  No confirmation appears. The name field has a red border and gets focus.
  `Sugar Cookies (4:00 PM)` **is still selected**.
- **Follow-up:** Type `Brock Powell` and press `Sign Up`. The error is replaced by
  `✓ Thanks, Brock Powell! You're signed up for Sugar Cookies (4:00 PM).`

### Test 3: Revise and repeat
- **Start:** Complete Test 1. The confirmation for
  `Chocolate Chip Cookies (3:00 PM)` is showing.
- **Input:** Keep the name `Brock Powell`. Change the session to
  `Oatmeal Cookies (5:00 PM)`.
- **Action:** Press `Sign Up` again.
- **Expected:** The message area shows exactly:
  `✓ Thanks, Brock Powell! You're signed up for Oatmeal Cookies (5:00 PM).`
  The previous Chocolate Chip confirmation is gone. Only one confirmation is on
  the screen, and the name is still `Brock Powell`.
