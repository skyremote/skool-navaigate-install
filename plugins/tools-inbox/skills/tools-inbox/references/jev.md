# Sorting with Jev (optional)

Jev is a judgement model from TypeSafe (typesafe.ai). It reads one piece of text and answers small questions about
it with probabilities. It does not write text. Code makes the decisions.

## Install
1. Create a TypeSafe account and key at typesafe.ai. Keep the key where the Jev skill's README says (your shell or
   your harness's secret settings), never in a chat or a project file.
2. Install the public skill: `git clone https://github.com/dbreunig/building-with-jev-skill`, then copy its
   `skills/jev` folder into your harness's skills folder, as its README says. It is a third-party skill with its own
   terms. This pack does not copy it.

## The pile questions we use
Ask one small question per judgement, all in one request:
- Choice: "Which pile does this email belong in?" with Reply today, Clients, Billing, Newsletters, Other.
- Noul: "Does the sender ask the reader to do something by a date?"
- Noul: "Is this an automated notification with no person writing?"

## The rule that keeps it safe
- Confidence under 0.7 goes to "Needs review". Never to an automatic action.
- Jev sorts. It never archives, deletes or sends. The member looks at the piles.
