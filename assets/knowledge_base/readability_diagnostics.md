# Ad Copy Readability & Cognitive Friction Diagnostics
**Target Platform:** Mobile Social Feeds (Meta/TikTok)
**Scope:** Linguistic simplification, Flesch-Kincaid adjustments, and cognitive load reduction for direct-response marketing.

## Flesch-Kincaid Grade Level (The <9.0 Rule)
**Diagnostic Triggers:** `is_high_cognitive_friction=True`, `flesch_kincaid_grade_level>9.0`, `flesch_reading_ease<60.0`
**Cognitive Mechanism:** Attention Span & Processing Fluency. Direct-response advertising targets cold audiences in a passive, scrolling state. Content exceeding an 8th-grade reading level requires active analytical thought. If an ad feels like "work" to read, the user will scroll past it. The target for maximum conversion is a **5th to 8th-grade reading level** (Reading Ease: 65–85).
**The Linguistic Rule:**
1. Do not "dumb down" the product concept; simplify the *delivery* of the concept.
2. Remove compound-complex sentences. Use simple Subject-Verb-Object structures.
3. Strip unnecessary transition words ("Furthermore," "Therefore," "Additionally").
4. Default to active voice. Never use passive voice.
**Rewrite Exemplar:**
- *Before (Grade 11.2):* Our latest footwear collection was specifically engineered to provide maximum arch support, thereby alleviating the discomfort frequently experienced by long-distance runners during marathon events.
- *After (Grade 6.1):* We built this shoe to support your arches and stop foot pain. Run your next marathon without the blisters.

## Sentence Complexity & Working Memory (The <18 Word Rule)
**Diagnostic Triggers:** `average_words_per_sentence>18.0`
**Cognitive Mechanism:** Working Memory Reset. Mobile reading happens in narrow, vertical columns. When a sentence exceeds 18 words, the user's eye has to track back and forth across the screen 4 to 5 times. By the time they reach the period, their working memory drops the beginning of the sentence.
**The Linguistic Rule:**
1. Hard limit: No single sentence may exceed **18 words**.
2. Target average: **10 to 14 words per sentence**.
3. Use the "Conjunction Chop": Find conjunctions (and, but, because, so) and replace them with a period. Start the next sentence with a capital letter.
4. Embrace punchy, conversational fragments. In copywriting, grammatically incomplete sentences drive momentum.
**Rewrite Exemplar:**
- *Before (26 words):* You should try our new vitamin C serum because it brightens dark spots in just two weeks and is formulated with completely natural, vegan ingredients. 
- *After (11, 7, and 5 words):* Try our new vitamin C serum. It brightens dark spots in just two weeks. 100% natural and vegan.

## Syllabic Density & Jargon (The Anglo-Saxon Rule)
**Diagnostic Triggers:** `average_syllables_per_word>1.6`
**Cognitive Mechanism:** Subvocalization Friction. Words with 3 or more syllables (polysyllabic) take longer for the brain to sound out silently. High syllable density makes copy sound academic, sterile, and corporate.
**The Linguistic Rule:**
1. Replace Latin-based corporate jargon with Anglo-Saxon root words. Anglo-Saxon words are typically older, shorter, punchier, and carry higher emotional weight.
2. The Syllable Swap Checklist:
   - Replace *Utilize* (3) with *Use* (1).
   - Replace *Facilitate* (4) with *Help* (1).
   - Replace *Innovative* (4) with *New* (1) or *Fresh* (1).
   - Replace *Eliminate* (4) with *Stop* (1) or *Kill* (1).
   - Replace *Demonstrate* (3) with *Show* (1).
3. Kill "-ly" adverbs. Instead of "runs extremely fast," use "sprints."
**Rewrite Exemplar:**
- *Before (Syllable dense):* Our revolutionary application facilitates seamless communication to maximize your operational efficiency.
- *After (Anglo-Saxon punch):* Our new app helps your team talk faster and get more done.

## Micro-Copy Exemption (The <10 Word Rule)
**Diagnostic Triggers:** `words_count<10`, `is_high_cognitive_friction=False`
**Cognitive Mechanism:** Statistical Formula Failure. Standard readability algorithms fail mathematically on ultra-short text strings, frequently generating false-positive "High Friction" scores because the sentence denominator is too small. 
**The Linguistic Rule:**
1. If the ad text is under 10 words, it is classified as "Micro-Copy." 
2. Micro-copy is inherently readable and requires no structural simplification.
3. For Micro-Copy, do not shorten it further. Focus purely on maximizing the emotional hook, the urgency, or the direct offer without adding unnecessary filler words.
**Rewrite Exemplar:**
- *Before (Micro-copy):* Flash sale ends at midnight! Grab yours now.
- *Action:* No readability rewrite required. Maintain current length.