from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from prompts.editor_prompt import (
    EDITOR_SYSTEM
)

from utils.config import (
    llm,
)


def editor_node(state) -> dict:
    """
    Intelligent blog editor.

    Responsibilities:
    - improve human feel
    - smooth transitions
    - improve readability
    - preserve article depth
    - prevent truncation
    - maintain markdown structure

    IMPORTANT:
    Never aggressively rewrite long blogs.
    """

    merged_markdown = state.get(
        "merged_md",
        ""
    )

    # ---------------------------------------------------
    # Empty Fallback
    # ---------------------------------------------------
    if not merged_markdown.strip():

        return {
            "final":
                "Blog generation failed."
        }

    # ---------------------------------------------------
    # IMPORTANT:
    # Skip editing for extremely large blogs
    # to prevent truncation.
    # ---------------------------------------------------
    if len(merged_markdown) > 18000:

        return {
            "final":
                merged_markdown
        }

    # ---------------------------------------------------
    # Medium Blog Handling
    # ---------------------------------------------------
    try:

        # ---------------------------------------------------
        # Safer editor token budget
        # ---------------------------------------------------
        editor_llm = llm.bind(
            max_tokens=2500,
            temperature=0.4,
        )

        response = editor_llm.invoke(
            [
                SystemMessage(
                    content=EDITOR_SYSTEM
                ),

                HumanMessage(
                    content=(
                        f"TOPIC:\n"
                        f"{state['topic']}\n\n"

                        f"TONE:\n"
                        f"{state['tone']}\n\n"

                        f"""
IMPORTANT:

This is already a completed blog.

Your task is ONLY to:
- improve readability
- improve transitions
- improve flow
- reduce robotic phrasing
- improve human feel

DO NOT:
- remove sections
- shorten content heavily
- rewrite the entire article
- reduce depth

Preserve:
- ALL headings
- ALL markdown
- ALL sections
- ALL explanations
- ALL article flow

BLOG MARKDOWN:

{merged_markdown}
"""
                    )
                ),
            ]
        )

        final_markdown = (
            response.content
            .replace("```markdown", "")
            .replace("```", "")
            .strip()
        )

        # ---------------------------------------------------
        # Truncation Protection
        # ---------------------------------------------------
        original_length = len(
            merged_markdown
        )

        edited_length = len(
            final_markdown
        )

        # If editor shrinks content too much,
        # editor likely truncated output.
        if (
            edited_length
            < original_length * 0.75
        ):

            final_markdown = (
                merged_markdown
            )

        # ---------------------------------------------------
        # Empty Protection
        # ---------------------------------------------------
        if not final_markdown.strip():

            final_markdown = (
                merged_markdown
            )

    except Exception as e:

        print(
            f"[Editor Error] {e}"
        )

        # ---------------------------------------------------
        # Safe fallback
        # ---------------------------------------------------
        final_markdown = (
            merged_markdown
        )

    # ---------------------------------------------------
    # Final Cleanup
    # ---------------------------------------------------
    final_markdown = (
        final_markdown
        .replace("```markdown", "")
        .replace("```", "")
        .strip()
    )

    return {
        "final":
            final_markdown
    }