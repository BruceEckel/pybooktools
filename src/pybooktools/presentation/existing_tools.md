Yes, there are several tools that take a Markdown file and render it as a full-screen HTML page. Here's a short list of
popular options, depending on your goals:

---

### ✅ **1. [Marp](https://marp.app/)**

**Purpose:** Turn Markdown into fullscreen *slide presentations* or static pages  
**How:**

- Install: `npm install -g @marp-team/marp-cli`
- Convert:
  ```sh
  marp yourfile.md --html --theme default --allow-local-files
  ```
- Or use the **VSCode Marp extension** to live-preview and export HTML

**Features:** Custom themes, speaker notes, PDF export, presentation mode

---

### ✅ **2. [Reveal.js + Markdown](https://revealjs.com/markdown/)**

**Purpose:** Create presentations or HTML documents from Markdown  
**How:**

- Use the [Markdown plugin for Reveal.js](https://github.com/hakimel/reveal.js#markdown)
- Or use [reveal-md](https://github.com/webpro/reveal-md) to quickly serve it:
  ```sh
  npm install -g reveal-md
  reveal-md yourfile.md
  ```

---

### ✅ **3. [obsidian-export](https://github.com/zoni/obsidian-export) + your own template**

**Purpose:** Turn Markdown into clean HTML from Obsidian vaults  
**How:** Use it to generate `.html` and wrap in a full-screen CSS layout

---

### ✅ **4. [grip](https://github.com/joeyespo/grip)**

**Purpose:** Preview GitHub-style Markdown in a browser  
**How:**

```sh
pip install grip
grip README.md
```

- Opens local server at `localhost:6419`
- You can save the rendered page as full-screen HTML via browser tools

---

### ✅ **5. Custom CSS Template + Pandoc**

If you want full control, use **Pandoc** with a minimal HTML template:

```sh
pandoc input.md -o output.html --standalone --css=fullscreen.css
```

