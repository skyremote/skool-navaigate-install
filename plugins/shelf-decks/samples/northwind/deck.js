/* Northwind Bakery: opening a second shop. A FICTIONAL practice deck.
   Northwind Bakery, Mill Lane, Harbour Street and every number here are made up
   to show the builders; none of it is evidence of anything.
   Render: shelf-decks render deck.js   (HTML + PPTX, then shots and pdf) */

module.exports = {
  profile: "member",            // the brand.json beside this file (or your own, after shelf-decks init)
  name: "Northwind_Second_Shop",
  title: "Northwind Bakery: opening a second shop",
  imagesDir: "images",

  slides: [
    { type: "cover", eyebrow: "Investor update · November", image: "cover",
      titleParts: [{ text: "A second\n" }, { text: "Northwind", c: "accent" }, { text: ",\non Harbour\nStreet." }],
      tagline: "We sell out by two o'clock most days. A second shop turns that queue into a second business.",
      promise: "Fictional sample deck.\nEvery figure is made up for practice.",
      // PPTX-only fine tuning: the PowerPoint cover title is set in points, not pixels.
      titleSize: 40, titleY: 1.75, titleH: 2.4, taglineY: 4.45, seamY: 5.5, promiseY: 5.7,
      talk: `Open on the ask in one line, then the reason.\n\n"Thanks for coming. In ten minutes I want to show you why we think Northwind is ready for a second shop, what it costs, and what we are asking you for."` },

    { type: "bigStats", eyebrow: "Where we are", title: "The first shop is full",
      dek: "Twelve months of till data from Mill Lane.", cardH: 2.75,
      items: [
        { num: "2,400", unit: "Loaves a week", label: "Up from 1,500 a year ago, with the same two ovens." },
        { num: "9 in 10", unit: "Days sold out", label: "The shelves are empty before two o'clock on most days." },
        { num: "31%", unit: "Travel 3+ miles", label: "Card postcodes show a third of customers come from the harbour side." },
        { num: "140", unit: "Wholesale waitlist", label: "Cafes and shops asking for a standing order we cannot bake." },
      ],
      footer: "Source: Northwind till and card data, Oct 2025 to Sep 2026 (fictional sample figures)",
      talk: `Let the numbers make the case. Linger on the sell-out figure.\n\n"Two thousand four hundred loaves a week, and nine days in ten we are sold out before two. The demand is there. The ovens are the limit."` },

    { type: "statement", dark: true, eyebrow: "The problem in one line",
      lines: [{ text: "We are not short of customers." }, { text: "We are short of oven.", c: "accentL" }],
      body: "Every extra loaf at Mill Lane means a night shift we cannot staff. A second site adds ovens, counter space and a team.",
      talk: `Pause after the second line.\n\n"We are not short of customers. We are short of oven."` },

    { type: "split", eyebrow: "The site", image: "harbour-street",
      titleParts: [{ text: "Harbour Street,\n" }, { text: "1.2 miles", c: "accent" }, { text: " from the queue" }],
      body: "A corner unit with a gas supply and a rear yard for the van, on the side of town a third of our customers already come from.",
      pills: ["1,100 sq ft", "10-year lease", "Gas on site"],
      footer: "Source: agent's particulars (fictional)",
      talk: `Show the place, then why it is the right place.\n\n"This is the unit. It sits right where a third of our customers already live."` },

    { type: "timelineAlt", eyebrow: "The plan", title: "From lease to first loaf in 20 weeks",
      phases: [
        { label: "Week 0", title: "Sign the lease", desc: "Rent-free fit-out period agreed." },
        { label: "Week 4", title: "Ovens ordered", desc: "Two deck ovens, eight-week lead time." },
        { label: "Week 10", title: "Fit-out", desc: "Counter, sinks, electrics, signage." },
        { label: "Week 14", title: "Team hired", desc: "Four bakers, three counter staff." },
        { label: "Week 18", title: "Soft opening", desc: "Wholesale waitlist first." },
        { label: "Week 20", title: "Doors open", desc: "Full hours, both shops baking." },
      ],
      talk: `Walk the line left to right; the last node is the date that matters.\n\n"Twenty weeks from signing to the doors opening."` },

    { type: "diagram", diagram: "flow",
      kicker: "How the two shops work together", title: "One night bake, two counters",
      footer: "Planned operation, not yet tested",
      image: "flow",
      data: { stages: [
        { label: "Mix at Mill Lane", note: "Doughs for both shops are mixed in one place, by the same team." },
        { label: "Bake overnight", note: "Mill Lane bakes the long-proved loaves from 2am." },
        { label: "Van at 5:30", note: "One van run takes the loaves to Harbour Street." },
        { label: "Finish on site", note: "Harbour Street bakes rolls and pastries fresh in its own ovens." },
        { label: "Counters at 7:00", note: "Both shops open with full shelves." },
      ] },
      talk: `Hover the stages in the HTML version to show the notes.\n\n"One team mixes, two shops sell. That keeps the bread the same in both."` },

    { type: "calculator", eyebrow: "What it costs", title: "£212,000 to open the second shop",
      foundation: { name: "Fit-out and two deck ovens", sub: "Quoted by two suppliers", price: "£148,000" },
      modules: [
        { name: "Lease deposit and legal fees", price: "£18,000" },
        { name: "Delivery van and racking", price: "£22,000" },
        { name: "Hiring and training, eight weeks", price: "£15,000" },
        { name: "Opening stock and launch", price: "£9,000" },
      ],
      total: "£212,000",
      footer: "Source: supplier quotes, Sep 2026 (fictional sample figures)",
      talk: `Read the total, then the biggest line.\n\n"Two hundred and twelve thousand pounds, and most of it is the ovens and the fit-out."` },

    { type: "outcomeBars", eyebrow: "Year one, planning case",
      titleParts: [{ text: "What changes in " }, { text: "the first year", c: "accent" }],
      outcomes: [
        { title: "Loaves baked each week", stat: "4,100", subLabel: "From 2,400 today", desc: "Two sites with four ovens, one shared night bake.",
          baselineRatio: 0.59, baselineLabel: "Today", withLabel: "Two shops", barCaption: "Scenarios, not forecasts" },
        { title: "Yearly revenue", stat: "£1.6m", subLabel: "From £0.9m today", desc: "Counter sales at Harbour Street plus the wholesale waitlist.",
          baselineRatio: 0.56, baselineLabel: "Today", withLabel: "Two shops", barCaption: "Scenarios, not forecasts" },
      ],
      footer: "Planning case built from the Mill Lane figures (fictional sample)",
      talk: `Say "planning case" out loud. These are scenarios, not forecasts.\n\n"If Harbour Street does what Mill Lane did in its second year, this is where we land."` },

    { type: "compare", eyebrow: "Risks", title: "What could go wrong, and our answer",
      left: { title: "The risk", items: ["The fit-out runs late", "Harbour Street sells less than planned", "We cannot hire bakers in time", "One van run fails"] },
      right: { title: "What we have in place", dark: true, items: ["Rent-free period covers eight weeks of delay", "Wholesale orders cover the fixed costs from week one", "Two Mill Lane bakers move across to lead", "A second driver and a back-up bake slot"] },
      talk: `Name each risk plainly, then the answer. Do not rush this slide.\n\n"Here is what keeps us up at night, and what we have done about each one."` },

    { type: "close", kicker: "The ask", image: "close.jpg",
      title: "Back us for £120,000",
      promise: "The rest comes from the bank loan already agreed in principle.",
      sub: "Decision by 30 November. Doors open in the spring.",
      ctaPrimary: "Book a site visit",
      ctaSub: "Fictional sample deck: every figure is made up",
      talk: `Land on the one action. Then stop talking.\n\n"We are asking for one hundred and twenty thousand pounds by the end of November. Come and see the site."` },
  ],
};
