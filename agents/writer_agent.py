from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from prompts.writer_prompt import (
    WRITER_SYSTEM
)

from utils.config import (
    writer_llm,
)


def writer_node(state) -> dict:
    """
    Advanced tone-aware blog writer.
    """

    plan = state["plan"]

    evidence = state.get(
        "evidence",
        []
    )

    sections = []

    # ---------------------------------------------------
    # Running Context Memory
    # ---------------------------------------------------
    running_context = ""

    # ---------------------------------------------------
    # Opening Diversity Memory
    # ---------------------------------------------------
    used_openings = []

    # ---------------------------------------------------
    # Tone Handling
    # ---------------------------------------------------
    tone = (
        plan.tone.lower()
        if hasattr(plan, "tone")
        else "professional"
    )

    # ---------------------------------------------------
    # Tone Style Engines
    # ---------------------------------------------------
    technical_tones = [
        "technical",
        "professional",
        "academic",
    ]

    marketing_tones = [
        "marketing",
        "seo",
        "business",
    ]

    storytelling_tones = [
        "storytelling",
    ]

    casual_tones = [
        "casual",
        "informal",
        "conversational",
    ]

    # ---------------------------------------------------
    # Sequential Writing
    # ---------------------------------------------------
    for index, task in enumerate(plan.tasks):

        # ---------------------------------------------------
        # Concepts Formatting
        # ---------------------------------------------------
        bullets_text = "\n".join(
            f"- {bullet}"
            for bullet in task.bullets
        )

        # ---------------------------------------------------
        # Compact Evidence
        # ---------------------------------------------------
        compact_evidence = []

        for item in evidence[:3]:

            if not isinstance(item, dict):
                continue

            compact_evidence.append(
                (
                    f"- {item.get('title', '')}\n"
                    f"  {item.get('snippet', '')[:140]}"
                )
            )

        evidence_text = "\n".join(
            compact_evidence
        )

        # ---------------------------------------------------
        # Opening Diversity
        # ---------------------------------------------------
        recent_openings = "\n".join(
            used_openings[-8:]
        )

        # ---------------------------------------------------
        # Previous Context
        # ---------------------------------------------------
        previous_context = ""

        if running_context.strip():

            previous_context = (
                "Previously Written Content:\n\n"
                + running_context[-5000:]
            )

        # ---------------------------------------------------
        # Dynamic Style Rules
        # ---------------------------------------------------
        if tone in technical_tones:

            style_rules = """
STYLE REFERENCE:
Write like DataCamp or professional Medium technical blogs.

WRITING STYLE:
- Prioritize clarity and structure
- Explain concepts directly
- Use concise educational writing
- Use practical examples frequently
- Sound professional and knowledgeable
- Avoid emotional storytelling
- Avoid dramatic hooks
- Avoid philosophical writing
- Avoid reflective monologues
- Prefer educational depth over narrative immersion

HEADINGS:
- Use direct professional headings
- Make headings descriptive and practical

FORMATTING:
- Use short readable paragraphs
- Use occasional bullet points only when useful
- Keep content highly scannable
- Use clean markdown hierarchy

PARAGRAPHS:
- Maximum 5-6 sentences
- Most sections under 250 words
- Avoid unnecessary repetition

EXAMPLES:
- Prefer practical real-world examples
- Mention tools, workflows, systems, or use-cases naturally
"""

        elif tone in marketing_tones:

            style_rules = """
STYLE REFERENCE:
Write like Hostinger marketing blogs.

WRITING STYLE:
- SEO-friendly
- Engaging but professional
- Reader-focused
- Action-oriented
- Practical and tactical
- Use actionable advice
- Maintain high readability

HEADINGS:
- Use benefit-oriented headings
- Make headings clickable but professional

FORMATTING:
- Highly scannable
- Use numbered lists occasionally
- Use bullet points sparingly
- Optimize readability

PARAGRAPHS:
- Short-medium length
- Internet-friendly formatting
- Avoid large text blocks
"""

        elif tone in storytelling_tones:

            style_rules = """
STYLE REFERENCE:
Write like Acumen storytelling blogs.

WRITING STYLE:
- Human-centered narrative
- Emotional but grounded
- Character-driven
- Reflective but controlled
- Immersive without becoming dramatic

HEADINGS:
- Narrative-oriented
- Emotionally meaningful

PARAGRAPHS:
- Varied rhythm
- Natural pacing
- Human storytelling flow
"""

        elif tone in casual_tones:

            style_rules = """
STYLE REFERENCE:
Write like Pepper Content casual blogs.

WRITING STYLE:
- Conversational
- Relaxed
- Simple language
- Approachable
- Friendly and engaging

HEADINGS:
- Curiosity-driven
- Natural internet-blog style

PARAGRAPHS:
- Short
- Highly skimmable
- Fast readable pacing
"""

        else:

            style_rules = """
WRITING STYLE:
Write like a modern professional blog.
"""

        # ---------------------------------------------------
        # Generate Section
        # ---------------------------------------------------
        try:

            response = writer_llm.invoke(
                [
                    SystemMessage(
                        content=WRITER_SYSTEM
                    ),

                    HumanMessage(
                        content=(
                            f"Blog Title:\n"
                            f"{plan.blog_title}\n\n"

                            f"Audience:\n"
                            f"{plan.audience}\n\n"

                            f"Tone:\n"
                            f"{plan.tone}\n\n"

                            f"Blog Type:\n"
                            f"{plan.blog_kind}\n\n"

                            f"{previous_context}\n\n"

                            f"Section Heading:\n"
                            f"## {task.title}\n\n"

                            f"Current Section Goal:\n"
                            f"{task.goal}\n\n"

                            f"Target Words:\n"
                            f"{task.target_words}\n\n"

                            f"Concepts To Naturally Cover:\n"
                            f"{bullets_text}\n\n"

                            f"Available Evidence:\n"
                            f"{evidence_text}\n\n"

                            f"{style_rules}\n\n"

                            f"""
IMPORTANT WRITING RULES:
- Avoid repetitive transitions
- Avoid repetitive paragraph openings
- Avoid robotic AI phrasing
- Avoid overexplaining obvious ideas
- Avoid bullet points
- Avoid generic filler content
- Avoid textbook-style transitions

OPENING VARIETY:
Recent openings already used:
{recent_openings}

DO NOT repeat similar openings.

FORBIDDEN AI PATTERNS:
- "So..."
- "As we..."
- "Imagine..."
- "In today's world..."
- "Let's explore..."
- "Now let's..."
- "You might think..."

LIST USAGE RULES:
- Never overuse bullet points
- Prefer narrative prose
- Most sections should contain zero lists
- Only use lists when readability improves significantly

QUOTE RULES:
- Occasionally include meaningful quotes
- Keep quotes relevant and natural
- Never overuse quotes

MARKDOWN RULES:
- ALWAYS use markdown headings
- Use clean spacing
- Use proper markdown hierarchy
- Keep formatting readable

CRITICAL OUTPUT RULES:
- NEVER explain edits
- NEVER describe improvements
- NEVER behave like an editor
- NEVER output commentary
- NEVER output meta explanations
- NEVER mention instructions
- NEVER act as an editor
- NEVER say "I made the following changes"

FORBIDDEN PHRASES:
- "I made the following changes"
- "Improved readability"
- "Enhanced transitions"
- "Here's the revised version"
- "Below is the article"

ONLY output actual blog content.
"""
                        )
                    ),
                ]
            )

            section_markdown = (
                response.content.strip()
            )

            # ---------------------------------------------------
            # Cleanup
            # ---------------------------------------------------
            section_markdown = (
                section_markdown
                .replace("```markdown", "")
                .replace("```", "")
                .strip()
            )

            # ---------------------------------------------------
            # HARD REMOVE EDITOR LEAKAGE
            # ---------------------------------------------------
            meta_phrases = [

                "changes made",
                "improved readability",
                "enhanced transitions",
                "reduced robotic phrasing",
                "improved human feel",
                "preserved all headings",
                "maintained depth",
                "seo-style blogs",
                "here's the revised version",
                "below is the revised article",
                "i made the following changes",
                "preserved markdown formatting",
                "improved flow",
                "preserved article flow",
                "enhanced flow",
                "maintained continuity",
                "rewritten version",
                "revised article",
                "editor improvements",
                "optimization changes",

            ]

            lower_text = section_markdown.lower()

            if any(
                phrase in lower_text
                for phrase in meta_phrases
            ):

                lines = section_markdown.split("\n")

                cleaned_lines = []

                started = False

                for line in lines:

                    clean = line.strip()

                    if clean.startswith("##"):
                        started = True

                    if started:
                        cleaned_lines.append(line)

                cleaned = "\n".join(
                    cleaned_lines
                ).strip()

                if cleaned:
                    section_markdown = cleaned

            # ---------------------------------------------------
            # REMOVE STRAY META LINES
            # ---------------------------------------------------
            filtered_lines = []

            for line in section_markdown.split("\n"):

                clean = line.strip().lower()

                if any(
                    phrase in clean
                    for phrase in meta_phrases
                ):
                    continue

                filtered_lines.append(line)

            section_markdown = "\n".join(
                filtered_lines
            ).strip()

            # ---------------------------------------------------
            # Track Openings
            # ---------------------------------------------------
            try:

                first_lines = (
                    section_markdown
                    .split("\n")
                )

                opening = ""

                for line in first_lines:

                    clean = line.strip()

                    if (
                        clean
                        and not clean.startswith("#")
                    ):

                        opening = clean[:120]
                        break

                if opening:

                    used_openings.append(
                        opening
                    )

            except Exception:

                pass

            # ---------------------------------------------------
            # Empty Fallback
            # ---------------------------------------------------
            if not section_markdown.strip():

                section_markdown = (
                    f"## {task.title}\n\n"
                    f"Content unavailable."
                )

        except Exception as e:

            print(
                f"[Writer Error] {e}"
            )

            section_markdown = (
                f"## {task.title}\n\n"
                f"{task.goal}\n\n"
                f"{bullets_text}"
            )

        # ---------------------------------------------------
        # Store Section
        # ---------------------------------------------------
        sections.append(
            (
                task.id,
                section_markdown
            )
        )

        # ---------------------------------------------------
        # Update Context Memory
        # ---------------------------------------------------
        running_context += (
            "\n\n"
            + section_markdown[:3000]
        )

    return {
        "sections": sections
    }