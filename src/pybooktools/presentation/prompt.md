I would like a Python program that takes a Markdown file containing fenced code blocks and displays it as an interactive
browser
presentation, which contains:

- Markdown headers and subheads as leveled bullet points. Collect these on a slide until you encounter a fenced code
  block, then display the bullet points on that slide.
- The code blocks as code examples, each on their own slide.
- Then the next Markdown header and subheads as a slide.
- Then the next code block as a slide.
- And so on.

- Using the right and left arrow keys moves forward and backward through the slides.
- The examples should use color syntax highlighting and be in a nice font with a background that can either be black or
  white, toggled by the 'b' key.
- Each example is by default fit to the width of the screen so no side-scrolling is necessary.
- Left justify the code rather than center it. It should be indented a little.
- Inside a code example, scroll up and down using the scroll wheel on my mouse.
- The slides should be as clean as possible. For example, no scrolling bars.
- When moving to a new example, the new example should be shown starting at the first line.
- The '=' key increases the font size.
- The '-' key decreases the font size.
- The 'q' key quits.
- When the font size for the code example being displayed is increased or decreased, the code examples should be
  reformatted using Ruff to fit the new character width of the screen.

- Use argparse to parse the command line arguments and provide help text.
- If you need to create files, put them in an appropriate subdirectory under ".presentation" in the directory of the
  Markdown file.
  Create new files for every run.
- Make the code as well-crafted and understandable as possible. Please make the code for this tool both compact (using
  sophisticated Python features) and easy to understand.
- Use the most modern Python standard libraries and third-party libraries as needed.
- Try to anticipate things that might need to be changed in the future.
- As part of the process, start the browser using webbrowser so it shows the first slide.