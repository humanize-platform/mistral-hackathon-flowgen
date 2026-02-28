import streamlit as st
import streamlit.components.v1 as components
import json
from generate_flow_chart import generate_flow_chart

st.set_page_config(
    page_title="FlowGen AI — Editable Flow Diagrams from Text",
    page_icon="🔀",
    layout="wide",
)

# Initialize session state
if "generating" not in st.session_state:
    st.session_state.generating = False
if "xml_output" not in st.session_state:
    st.session_state.xml_output = None
if "error" not in st.session_state:
    st.session_state.error = None


def on_generate():
    st.session_state.generating = True
    st.session_state.xml_output = None
    st.session_state.error = None


# ── Hero Section ──
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #FF7000 0%, #FF9A00 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    ">
        <h1 style="margin:0; font-size:2rem;">🔀 FlowGen AI <span style="font-size:0.9rem; opacity:0.85;">by Team humanize</span></h1>
        <p style="font-size:1.15rem; margin:0.5rem 0 0.3rem 0; font-weight:500;">
            Generate <u>fully editable</u> Draw.io flow diagrams from plain-text descriptions — powered by Mistral AI Agents.
        </p>
        <p style="font-size:0.95rem; margin:0; opacity:0.92;">
            🚫 No more static images &nbsp;|&nbsp; 🚫 No more uneditable Mermaid/Markdown &nbsp;|&nbsp;
            ✅ Real Draw.io XML you can open, edit, and share
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Why this matters ──
with st.expander("💡 **Why FlowGen AI?** — The problem we solve", expanded=False):
    st.markdown(
        """
        Today, when you ask an AI assistant to create a flow chart, you typically get:

        | What you get | The problem |
        |---|---|
        | 🖼️ A static **image** (PNG/SVG) | Can't edit nodes, labels, or layout |
        | 📝 **Mermaid / Markdown** text | Requires rendering tools; not drag-and-drop editable |
        | 📄 A bulleted **text outline** | Not even a diagram |

        **FlowGen AI is different.** It generates industry-standard **Draw.io XML** — the same format used by
        [diagrams.net](https://app.diagrams.net), Confluence, and VS Code extensions. The output is a
        **fully editable, drag-and-drop flow diagram** that professionals can immediately refine and integrate
        into their documentation.

        ### How it works
        1. **Flow Analyst Agent** (Mistral) — analyzes your text and structures it into logical process steps
        2. **Flow Generator Agent** (Mistral) — converts the structured steps into valid Draw.io XML
        3. **Embedded Editor** — renders the XML right here so you can edit before exporting

        *Built with Mistral AI Agents · LangChain · Streamlit*
        """
    )

# ── Main Layout ──
col_input, col_output = st.columns([1, 2], gap="large")

with col_input:
    st.markdown("#### ✏️ Describe your process")
    flow_description = st.text_area(
        "Flow Description",
        placeholder="Example: User opens app → logs in → views dashboard → clicks report → downloads PDF → logs out",
        height=280,
        label_visibility="collapsed",
    )
    st.button(
        "🚀 Generate Flow Chart",
        type="primary",
        disabled=st.session_state.generating or not flow_description,
        on_click=on_generate,
        use_container_width=True,
    )

with col_output:
    st.markdown("#### 🎨 Editable Flow Diagram")

    if st.session_state.generating:
        with st.spinner("⏳ Mistral agents are working... analyzing → generating → rendering"):
            try:
                st.session_state.xml_output = generate_flow_chart(flow_description)
            except Exception as e:
                st.session_state.error = str(e)
            finally:
                st.session_state.generating = False
                st.rerun()

    if st.session_state.xml_output:
        xml_escaped = json.dumps(st.session_state.xml_output)
        drawio_html = f"""
        <iframe id="drawio-editor"
            src="https://embed.diagrams.net/?embed=1&proto=json&spin=1&modified=unsavedChanges&libraries=1"
            style="width:100%;height:500px;border:1px solid #ddd;border-radius:8px;">
        </iframe>
        <script>
            var iframe = document.getElementById('drawio-editor');
            var xmlData = {xml_escaped};
            window.addEventListener('message', function(evt) {{
                try {{
                    if (evt.data.length > 0) {{
                        var msg = JSON.parse(evt.data);
                        if (msg.event === 'init') {{
                            iframe.contentWindow.postMessage(JSON.stringify({{
                                action: 'load',
                                xml: xmlData
                            }}), '*');
                        }}
                    }}
                }} catch(e) {{}}
            }});
        </script>
        """
        components.html(drawio_html, height=520)
    elif not st.session_state.generating and not st.session_state.error:
        st.info("👈 Describe a process on the left and hit **Generate** to see an editable flow diagram here.")

    if st.session_state.error:
        st.error(f"❌ Error: {st.session_state.error}")
