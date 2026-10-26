# Prompts: shelf-thumbnails

Paste one of these into Claude from your working folder. The thumbnails skill uses YOUR photos, makes four concepts with no words on them, then adds the headline as a real text layer so it is spelled correctly. The four-concept step needs a Gemini key (GEMINI_API_KEY) in ~/.claude/.env.

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown, except the one marked unproven.
Replace the sample names and figures with your own.

## Prompt 1: Build your photo catalogue first

**You need:** A folder of your own photos (the sample uses photos/ with three files). No key.

```text
Use the thumbnails skill. I have not catalogued my photos yet. They are in the photos/ folder. Look at each one and write photos/catalogue.md with one row per photo: file name, expression, pose and setting. Also write brand.md rules from what I tell you: colours are cream #FFF3DC, crust brown #7A4A24 and one bright accent #E8452C; headlines are heavy condensed sans, white fill with a dark brown stroke; never use stock photos of other people. Then tell me what you still need before you can make a thumbnail.
```

## Prompt 2: Four concepts side by side

**You need:** Your photo catalogue, brand rules and a Gemini key.

```text
Use the thumbnails skill. Make a 16:9 YouTube thumbnail for my video "How Northwind Bakery doubled Saturday sales". Use my photos in photos/ and the rules in brand.md. Generate four scene concepts with no text in the images, lay them out as a 2x2 sheet so I can compare them, and save the sheet as thumbnail-options.png. Do not add the headline yet. I will tell you which one I want.
```

**Not proven end to end:** the Gemini image call needs a valid key, and the only Gemini key on the build Mac was rejected by Google (API_KEY_INVALID). In the proof run Claude stopped, said so plainly, and told the member where to put a new key. The catalogue (prompt 1) and the headline layer (prompt 3) were proven.

## Prompt 3: Add the headline as a real text layer

**You need:** The concept image you picked, and the brand rules. No key and no image model: this step is a local overlay.

```text
Use the thumbnails skill. I picked concept_2.png. Add the headline DOUBLED SATURDAY SALES to it as a real text layer, using the type rules in brand.md, in the top left, with enough contrast to read at the size of a phone screen. Do not use any image model for this step. Save it as saturday-sales_thumbnail.png and tell me how you made the text.
```
