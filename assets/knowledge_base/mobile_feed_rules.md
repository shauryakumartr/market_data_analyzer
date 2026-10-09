# Mobile Feed Physics & Cognitive Rules
**Target Platform:** Meta (Facebook & Instagram Mobile Feeds)
**Scope:** Direct-Response Paid Advertising Copy Optimization

## Mobile Fold & The 125-Character Hook Window
**Diagnostic Triggers:** `is_mobile_truncated=True`, `is_offer_buried=True`
**Cognitive Mechanism:** Attention Decay & Micro-Friction. On mobile devices, Meta truncates primary text at approximately 125 characters behind a "...See More" link. Less than 10% of users tap to expand. If the hook or commercial incentive is placed after character 125, it is functionally invisible.
**The Mechanical Rule:**
1. The primary hook, core benefit, or promotional incentive MUST resolve completely within the first 110–125 characters.
2. Select one of four high-converting hook archetypes:
   - *Direct Offer:* "Save 25% on our award-winning sleep blend tonight only."
   - *Negative Constraint / Problem:* "Stop washing your face with hot water. Here is why:"
   - *Social Proof Lead:* "Over 45,000 runners switched to this recovery shoe this month."
   - *Contrarian Stance:* "Most protein powders bloat your gut. Ours fixes it."
3. Never use introductory pleasantries or rhetorical fluff ("Are you looking for...").
**Rewrite Exemplar:**
- *Before (Buried at char 198):* Tired of dull morning skin? Our natural hydration serum is clinically tested to lock in moisture for 24 hours straight without clogging pores. Use code GLOW20 to claim 20% off.
- *After (Resolved at char 94):* Wake up with glowing, hydrated skin. ✨ Use code GLOW20 for 20% off our 24-hr clinical serum.

## Visual Pacing & Wall-of-Text Formatting
**Diagnostic Triggers:** `is_wall_of_text=True`, `line_breaks<=1`
**Cognitive Mechanism:** Visual Fatigue & Scanning Resistance. Mobile users scan via rapid 150–250 millisecond saccadic eye movements. An unbroken paragraph exceeding 200 characters registers as a cognitive burden, triggering a scroll-away reflex. Whitespace acts as visual resting points that pull the eye downward.
**The Mechanical Rule:**
1. No paragraph may exceed two sentences (or 35 words).
2. Insert double line breaks (`\n\n`) between thoughts to generate vertical whitespace.
3. Use single-concept lines and bulleted value lists (2 to 4 items maximum).
4. Bullet points must maintain uniform grammatical structure (all starting with active verbs or benefit nouns).
**Rewrite Exemplar:**
- *Before (Dense block):* We spent two years engineering the world's most comfortable desk chair with adaptive lumbar support, breathable mesh fabric, and 4D adjustable armrests designed to completely eliminate lower back pain during long work hours.
- *After (Spaced for mobile scanning):* We spent 2 years engineering the ultimate desk chair.
  Say goodbye to mid-day back pain:
  • Adaptive lumbar support
  • Breathable cool-weave mesh
  • 4D adjustable armrests
  Built for 8+ hour workdays.

## Cognitive Load & Subvocalization Friction
**Diagnostic Triggers:** `is_high_cognitive_friction=True`, `flesch_kincaid_grade_level>9.0`, `average_words_per_sentence>18.0`
**Cognitive Mechanism:** Subvocal Processing Bottleneck. Readers silently pronounce words in their minds. Polysyllabic, corporate jargon (3+ syllables) slows subvocalization speed, increases mental effort, and reduces impulse-click readiness on cold traffic.
**The Mechanical Rule:**
1. Maintain a Flesch-Kincaid Grade Level between **5.0 and 7.5**.
2. Keep average sentence length under **14–16 words**.
3. Replace multi-syllabic academic vocabulary with concrete, Anglo-Saxon root words:
   - Swap "utilize" for "use"
   - Swap "formulation" for "blend" or "recipe"
   - Swap "revolutionary" for "new" or "proven"
   - Swap "dermatologically tested" for "doctor approved"
**Rewrite Exemplar:**
- *Before (Grade 12.4, 28 words/sentence):* Our proprietary dermatological formulation utilizes bio-compatible peptides specifically engineered to facilitate subcutaneous cellular rejuvenation and reverse epidermal degradation caused by environmental pollutants.
- *After (Grade 5.1, 11 words/sentence):* Our doctor-approved peptide serum repairs damaged skin fast. It protects against daily dirt, locks in moisture, and restores a firm, youthful look.

## Headline Character Limits & The Button Anchor
**Diagnostic Triggers:** `headline_length>27`, missing headline CTA alignment
**Cognitive Mechanism:** Dual-Processing Anchor. On mobile feeds, the headline sits directly adjacent to the CTA button under the media asset. When button text expands on narrow screens, Meta truncates headlines beyond 27 characters. The headline's psychological purpose is to provide the immediate *click rationale* that justifies tapping the button.
**The Mechanical Rule:**
1. Strict character limit: **27 characters or fewer** (including spaces).
2. Never repeat the opening hook from the primary text.
3. Pair the headline directly with the selected button:
   - For "Shop Now" button: Highlight financial incentive or product tier (e.g., "Get 20% Off Today", "Shop Best Sellers").
   - For "Learn More" button: Highlight friction-free discovery (e.g., "See How It Works", "Find Your Shade").
   - For "Get Offer" button: Highlight exclusivity (e.g., "Claim Free Shipping").
**Rewrite Exemplar:**
- *Before (Truncates on mobile UI):* Discover the All-New Zero-Sugar Energy Drink That Crushes Fatigue (67 chars)
- *After (Full visibility):* Clean Energy. 0g Sugar. (24 chars)

## Offer Architecture, Urgency & Risk Reversal
**Diagnostic Triggers:** `has_offer=False`, `has_urgency=False`, buried discount mechanics
**Cognitive Mechanism:** Information Scent & Loss Aversion. Skeptical mobile buyers abandon carts if discount mechanics require guesswork or if financial risk is not mitigated. Vague urgency ("Hurry, limited time!") triggers ad cynicism; specific anchors trigger genuine loss aversion.
**The Mechanical Rule:**
1. Explicit Offer Math: State the exact discount value, coupon code, or threshold terms clearly (e.g., "Use code SAVE20 for $20 off orders over $75").
2. Logical Scarcity Anchors: Ground urgency in a realistic operational constraint (e.g., "Small-batch roast", "Warehouse clearance", "Offer ends Sunday at midnight").
3. Risk Reversal: If space permits before the fold or directly above the CTA, embed a friction remover:
   - "30-Day Money-Back Guarantee"
   - "Free returns, no questions asked"
   - "Ships free within 24 hours"
**Rewrite Exemplar:**
- *Before (Weak, ambiguous incentive):* Check out our website today for special promotional pricing on all winter apparel before everything is gone!
- *After (Concrete terms + risk reversal):* Take 30% off all winter jackets with code FROST30.
  Sale ends Sunday at midnight.
  Free shipping + 30-day free returns on every order.

## Emoji Functional Hygiene & Directional Cues
**Diagnostic Triggers:** `emoji_density>0.05` (Spam Alert) or `emoji_count==0` (Sterility Alert)
**Cognitive Mechanism:** Pattern Interrupt vs. Trust Degradation. Over-indexing on emojis (>5% density) registers as spam and damages perceived brand authority. Omitting emojis entirely makes the ad feel like an unformatted text dump.
**The Mechanical Rule:**
1. Limit emoji count to **1 to 3 emojis** per 100 words.
2. Use emojis strictly for operational functions:
   - *Structural Organizers:* Use clean geometric markers (•, ✔, →) to structure benefits.
   - *Gaze Anchors / Visual Pointers:* Place a single downward arrow (👇 or ⬇️) at the end of the text pointing directly to the headline and CTA button.
3. Ban emotional replacement emojis (e.g., replacing words with symbols like "We ❤️ our 🐶 customers").
**Rewrite Exemplar:**
- *Before (Over-saturated spam):* 🔥🚨 MASSIVE SALE ALERT! 🚨🔥 Get your hands on the BEST 👟 shoes in town! 🏃💨 Don't wait 😱!
- *After (Functional & clean):* Our best-selling trail shoes are back in stock.
  Engineered for wet terrain and long miles.
  Claim your pair before inventory runs out 👇

## CTA Congruency & Behavioral Match
**Diagnostic Triggers:** Body copy directive conflicting with CTA button value
**Cognitive Mechanism:** Cognitive Dissonance. If body copy instructs the user to "Buy your bottle right now" while the Meta button displays "Learn More", the mismatched signals create friction at the decision point. High-friction asks on low-commitment buttons suppress conversion rates.
**The Mechanical Rule:**
1. High-Intent Products (Impulse buys <$50, direct sales): Match closing copy ("Tap below to order") to the `"Shop Now"` button.
2. Moderate-Intent / Educational Products (SaaS, high-ticket, complex goods): Match closing copy ("See our clinical results below") to the `"Learn More"` button.
3. Lead Generation / Free Trials: Match closing copy ("Get your free guide below") to `"Download"` or `"Sign Up"`.
**Rewrite Exemplar:**
- *Before (Conflicting intent):* "Order your custom kitchen cabinets today and pay in full!" (Button: `Learn More`)
- *After (Congruent progression):* "See our custom finishes and get a free project estimate below." (Button: `Learn More`)