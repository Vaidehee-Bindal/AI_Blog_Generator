from __future__ import annotations

import json
import re

from datetime import date, datetime

from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Tuple,
)

import pandas as pd
import streamlit as st

from workflow.blog_workflow import app


# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Blog Writer",
    layout="wide",
)


# ---------------------------------------------------
# Global CSS
# ---------------------------------------------------
st.markdown(
    """
<style>

/* Main App */
.block-container{
    padding-top:2rem;
    padding-bottom:3rem;
    max-width:1400px;
}

/* Prevent clipping */
div[data-testid="stMarkdownContainer"]{
    overflow: visible !important;
}

/* Improve readability */
p, li{
    line-height:1.9;
    font-size:1.05rem;
}

/* Headings */
h1,h2,h3{
    margin-top:1.4rem;
    margin-bottom:1rem;
}

/* Tables */
thead tr th{
    font-weight:700 !important;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    width:340px !important;
}

/* Prevent hidden overflow */
.element-container{
    overflow: visible !important;
}

/* Better code blocks */
pre{
    overflow-x:auto !important;
    border-radius:10px;
    padding:1rem !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------
# Session State
# ---------------------------------------------------
if "blog_history" not in st.session_state:
    st.session_state.blog_history = []

if "current_blog_index" not in st.session_state:
    st.session_state.current_blog_index = None

if "logs" not in st.session_state:
    st.session_state.logs = []


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def safe_slug(text: str) -> str:

    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9\s_-]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        "_",
        text
    )

    return text[:80]


def log(message: str):

    timestamp = datetime.now().strftime(
        "%H:%M:%S"
    )

    st.session_state.logs.append(
        f"[{timestamp}] {message}"
    )


def extract_latest_state(
    current_state: Dict[str, Any],
    step_payload: Any
):

    if isinstance(
        step_payload,
        dict
    ):

        if (
            len(step_payload) == 1
            and isinstance(
                next(
                    iter(
                        step_payload.values()
                    )
                ),
                dict
            )
        ):

            inner = next(
                iter(
                    step_payload.values()
                )
            )

            current_state.update(
                inner
            )

        else:

            current_state.update(
                step_payload
            )

    return current_state


def try_stream(
    graph_app,
    inputs: Dict[str, Any]
) -> Iterator[Tuple[str, Any]]:

    try:

        for step in graph_app.stream(
            inputs,
            stream_mode="updates"
        ):

            yield (
                "updates",
                step
            )

        out = graph_app.invoke(
            inputs
        )

        yield (
            "final",
            out
        )

    except Exception as e:

        log(f"ERROR: {e}")

        raise e


# ---------------------------------------------------
# Title
# ---------------------------------------------------
st.title(
    "AI Blog Writing Agent"
)


# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
with st.sidebar:

    st.header(
        "Generate Blog"
    )

    topic = st.text_area(
        "Topic",
        placeholder="Enter your blog topic...",
        height=120,
    )

    tone = st.selectbox(
        "Writing Tone",
        [
            "Professional",
            "Conversational",
            "Beginner Friendly",
            "Technical",
            "Casual",
            "Storytelling",
            "Academic",
            "Marketing",
            "SEO Optimized",
        ]
    )

    as_of = st.date_input(
        "As-of Date",
        value=date.today()
    )

    generate_btn = st.button(
        "Generate Blog",
        use_container_width=True,
        type="primary",
    )

    st.divider()

    st.subheader(
        "Generated Blogs"
    )

    history = st.session_state.blog_history

    if not history:

        st.caption(
            "No blogs generated yet."
        )

    else:

        labels = []

        for idx, blog in enumerate(history):

            labels.append(
                f"{idx + 1}. "
                f"{blog['title']}"
            )

        selected_label = st.radio(
            "Blog History",
            labels,
            label_visibility="collapsed",
            index=(
                st.session_state.current_blog_index
                if st.session_state.current_blog_index is not None
                else len(labels) - 1
            ),
        )

        selected_index = labels.index(
            selected_label
        )

        if st.button(
            "Load Blog",
            use_container_width=True,
        ):

            st.session_state.current_blog_index = (
                selected_index
            )

            st.rerun()


# ---------------------------------------------------
# Generate Workflow
# ---------------------------------------------------
if generate_btn:

    if not topic.strip():

        st.warning(
            "Please enter a topic."
        )

        st.stop()

    inputs = {
        "topic": topic,
        "tone": tone,
        "as_of": as_of.isoformat(),
        "mode": "",
        "needs_research": False,
        "queries": [],
        "recency_days": 30,
        "evidence": [],
        "plan": None,
        "sections": [],
        "merged_md": "",
        "final": "",
    }

    status = st.status(
        "Generating blog...",
        expanded=True
    )

    progress_area = st.empty()

    current_state = {}

    for kind, payload in try_stream(
        app,
        inputs
    ):

        if kind == "updates":

            current_state = (
                extract_latest_state(
                    current_state,
                    payload
                )
            )

            summary = {
                "mode":
                    current_state.get(
                        "mode"
                    ),

                "needs_research":
                    current_state.get(
                        "needs_research"
                    ),

                "queries":
                    current_state.get(
                        "queries",
                        []
                    ),

                "evidence_count":
                    len(
                        current_state.get(
                            "evidence",
                            []
                        )
                    ),

                "sections_generated":
                    len(
                        current_state.get(
                            "sections",
                            []
                        )
                    ),
            }

            progress_area.json(
                summary
            )

        elif kind == "final":

            out = payload

            plan = out.get(
                "plan"
            )

            if hasattr(
                plan,
                "blog_title"
            ):

                blog_title = (
                    plan.blog_title
                )

            elif isinstance(
                plan,
                dict
            ):

                blog_title = (
                    plan.get(
                        "blog_title",
                        topic
                    )
                )

            else:

                blog_title = topic

            # ---------------------------------------------------
            # Serialize Plan
            # ---------------------------------------------------
            plan_data = out.get(
                "plan"
            )

            if hasattr(
                plan_data,
                "model_dump"
            ):

                plan_data = (
                    plan_data.model_dump()
                )

            # ---------------------------------------------------
            # Serialize Evidence
            # ---------------------------------------------------
            serialized_evidence = []

            raw_evidence = out.get(
                "evidence",
                []
            )

            if isinstance(
                raw_evidence,
                list
            ):

                for item in raw_evidence:

                    if hasattr(
                        item,
                        "model_dump"
                    ):

                        item = item.model_dump()

                    if not isinstance(
                        item,
                        dict
                    ):
                        continue

                    serialized_evidence.append(
                        {
                            "title":
                                str(
                                    item.get(
                                        "title",
                                        ""
                                    )
                                ),

                            "url":
                                str(
                                    item.get(
                                        "url",
                                        ""
                                    )
                                ),

                            "published_at":
                                str(
                                    item.get(
                                        "published_at",
                                        ""
                                    )
                                ),

                            "snippet":
                                str(
                                    item.get(
                                        "snippet",
                                        ""
                                    )
                                ),

                            "source":
                                str(
                                    item.get(
                                        "source",
                                        ""
                                    )
                                ),
                        }
                    )

            # ---------------------------------------------------
            # Final Blog
            # ---------------------------------------------------
            final_blog = out.get(
                "final",
                ""
            )

            if not isinstance(
                final_blog,
                str
            ):

                final_blog = str(
                    final_blog
                )

            # ---------------------------------------------------
            # Blog Entry
            # ---------------------------------------------------
            blog_entry = {
                "title":
                    blog_title,

                "timestamp":
                    str(
                        datetime.now()
                    ),

                "plan":
                    plan_data,

                "evidence":
                    serialized_evidence,

                "final":
                    final_blog,
            }

            st.session_state.blog_history.append(
                blog_entry
            )

            st.session_state.current_blog_index = (
                len(
                    st.session_state.blog_history
                ) - 1
            )

            log(
                f"Generated blog: {blog_title}"
            )

            status.update(
                label="Blog Generated Successfully",
                state="complete",
                expanded=False,
            )


# ---------------------------------------------------
# Current Blog
# ---------------------------------------------------
current_blog = None

history = st.session_state.blog_history

current_index = (
    st.session_state.current_blog_index
)

if (
    history
    and current_index is not None
    and current_index < len(history)
):

    current_blog = history[
        current_index
    ]


# ---------------------------------------------------
# Tabs
# ---------------------------------------------------
tab_plan, tab_evidence, tab_preview, tab_logs = st.tabs(
    [
        "Plan",
        "Evidence",
        "Markdown Preview",
        "Logs",
    ]
)


# ---------------------------------------------------
# PLAN TAB
# ---------------------------------------------------
with tab_plan:

    st.subheader(
        "Execution Plan"
    )

    if not current_blog:

        st.info(
            "No plan available."
        )

    else:

        plan = current_blog.get(
            "plan"
        )

        if hasattr(
            plan,
            "model_dump"
        ):

            plan = plan.model_dump()

        if not plan:

            st.info(
                "No plan available."
            )

        else:

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Audience",
                str(
                    plan.get(
                        "audience",
                        "-"
                    )
                )
            )

            col2.metric(
                "Tone",
                str(
                    plan.get(
                        "tone",
                        "-"
                    )
                )
            )

            col3.metric(
                "Type",
                str(
                    plan.get(
                        "blog_kind",
                        "-"
                    )
                )
            )

            tasks = plan.get(
                "tasks",
                []
            )

            if tasks:

                st.dataframe(
                    pd.DataFrame(
                        tasks
                    ),
                    use_container_width=True,
                    hide_index=True,
                )


# ---------------------------------------------------
# EVIDENCE TAB
# ---------------------------------------------------
with tab_evidence:

    st.subheader(
        "Research Evidence"
    )

    if not current_blog:

        st.info(
            "No evidence available."
        )

    else:

        evidence = current_blog.get(
            "evidence",
            []
        )

        if not evidence:

            st.info(
                "No evidence available."
            )

        else:

            cleaned_rows = []

            for item in evidence:

                if hasattr(
                    item,
                    "model_dump"
                ):

                    item = item.model_dump()

                if not isinstance(
                    item,
                    dict
                ):
                    continue

                cleaned_rows.append(
                    {
                        "Title":
                            str(
                                item.get(
                                    "title",
                                    ""
                                )
                            ),

                        "Source":
                            str(
                                item.get(
                                    "source",
                                    ""
                                )
                            ),

                        "Published":
                            str(
                                item.get(
                                    "published_at",
                                    ""
                                )
                            ),

                        "URL":
                            str(
                                item.get(
                                    "url",
                                    ""
                                )
                            ),
                    }
                )

            st.dataframe(
                pd.DataFrame(
                    cleaned_rows
                ),
                use_container_width=True,
                hide_index=True,
            )


# ---------------------------------------------------
# PREVIEW TAB
# ---------------------------------------------------
with tab_preview:

    st.subheader(
        "Generated Blog"
    )

    if not current_blog:

        st.info(
            "No blog available."
        )

    else:

        final_md = current_blog.get(
            "final",
            ""
        )

        st.markdown(
            final_md,
            unsafe_allow_html=True
        )

        st.divider()

        st.download_button(
            "Download Markdown",

            data=final_md.encode(
                "utf-8"
            ),

            file_name=(
                safe_slug(
                    current_blog.get(
                        "title",
                        "blog"
                    )
                ) + ".md"
            ),

            mime="text/markdown",
        )


# ---------------------------------------------------
# LOGS TAB
# ---------------------------------------------------
with tab_logs:

    st.subheader(
        "System Logs"
    )

    if not st.session_state.logs:

        st.info(
            "No logs available."
        )

    else:

        st.text_area(
            "Logs",

            value="\n".join(
                st.session_state.logs[-200:]
            ),

            height=600,
        )


# ---------------------------------------------------
# Empty State
# ---------------------------------------------------
if not current_blog:

    st.info(
        "Generate a blog to begin."
    )